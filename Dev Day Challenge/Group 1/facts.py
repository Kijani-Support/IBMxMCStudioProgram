"""Passerelle (EN: "Gateway") — Facts Builder & Confidence Scorer.

Tagline: "Franchir la frontière, vérifier d'abord" / "Cross the border, verify first."
Team: Christopher Damian Munene, Mark Lekayia. Group 1, IBM x MC Studio Dev Day.

Purpose:
    Assemble ``facts.json`` from parsed dossiers, bloc intersections, home-vs-target
    comparisons, scoped Verify-first flags (``template``, ``country``, ``bloc``),
    external unverified checks from ``data/external_checks.json``, and deterministic
    Data Confidence scores computed exclusively from country-scope and bloc-scope
    flags (C2).

Inputs:
    Home country identifier, target country identifier, sector name, and optional
    parsed corpus or dossier directory path.

Outputs:
    JSON-serialisable ``facts`` dictionary (and optional written ``facts.json`` file)
    carrying line-level provenance on every dossier figure and name.

Failure behaviour:
    Raises ``ValueError`` if home, target, or sector cannot be resolved; all dossier
    anomalies become structured flags rather than exceptions.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from blocs import compare_blocs, load_json_data
from compare import (
    compare_languages,
    compare_regulators,
    compare_sector_steps,
    compare_taxes,
    resolve_sector,
)
from parser import Field, parse_corpus

# Placeholder regex reused for lightweight route-level checks prior to validate.py.
_PLACEHOLDER_RE = re.compile(r"\b(verify|tbd|n/a)\b", re.IGNORECASE)


def resolve_country_slug(query: str, dossiers: dict[str, dict[str, Any]]) -> str:
    """Resolve a user country input (slug or display name) against parsed dossiers.

    Purpose:
        Match CLI inputs like ``country-a`` or ``Country A`` dynamically using
        only the loaded corpus — zero hard-coded country names (R1).

    Inputs:
        query: User-supplied country slug or name.
        dossiers: Mapping of slug to parsed dossier dict.

    Outputs:
        Canonical slug key present in ``dossiers``.

    Failure behaviour:
        Raises ``ValueError`` listing sample valid slugs if no dossier matches.
    """
    cleaned = query.strip().lower()
    slug_guess = re.sub(r"[^a-z0-9]+", "-", cleaned).strip("-")
    if cleaned in dossiers:
        return cleaned
    if slug_guess in dossiers:
        return slug_guess
    for slug, doc in dossiers.items():
        c_field: Optional[Field] = doc.get("country")
        if c_field and c_field.value.strip().lower() == cleaned:
            return slug
    sample = ", ".join(sorted(dossiers.keys())[:8])
    raise ValueError(f"Unknown country '{query}'. Sample valid slugs: {sample} ...")


def _make_flag(
    rule_id: str,
    severity: str,
    scope: str,
    confidence: str,
    message: str,
    evidence: list[dict[str, Any]],
    why_it_matters: str,
    suggested_check: str,
    affected_count: Optional[int] = None,
    corpus_total: Optional[int] = None,
) -> dict[str, Any]:
    """Construct a standard Passerelle Flag dictionary (C2).

    Purpose:
        Enforce a uniform Flag schema carrying ``scope`` (``template`` | ``country`` |
        ``bloc``) and ``confidence`` (``in-dossier`` | ``our-check``) alongside line
        evidence and plain-language guidance.

    Inputs:
        rule_id: Rule identifier string.
        severity: ``"high"``, ``"med"``, or ``"low"``.
        scope: ``"template"``, ``"country"``, or ``"bloc"``.
        confidence: ``"in-dossier"`` or ``"our-check"``.
        message: Concise factual description of the issue.
        evidence: List of serialized ``Field`` dicts supporting the flag.
        why_it_matters: One plain-language sentence explaining founder impact.
        suggested_check: Plain-language pointer to whom to ask.
        affected_count: Optional corpus-wide count for ``template``-scope flags.
        corpus_total: Optional corpus size for ``template``-scope flags.

    Outputs:
        Flag dictionary ready for ``facts.json``.

    Failure behaviour:
        Never raises.
    """
    flag: dict[str, Any] = {
        "rule_id": rule_id,
        "severity": severity,
        "scope": scope,
        "confidence": confidence,
        "message": message,
        "evidence": [e for e in evidence if e is not None],
        "why_it_matters": why_it_matters,
        "suggested_check": suggested_check,
    }
    if affected_count is not None:
        flag["affected_count"] = affected_count
    if corpus_total is not None:
        flag["corpus_total"] = corpus_total
    return flag


def _compute_corpus_stats(dossiers: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Compute lightweight corpus-wide systemic defect counts for template banners.

    Purpose:
        Supply accurate ``N of 54 dossiers share this defect`` counts dynamically at
        runtime from the loaded corpus (R1, C2).

    Inputs:
        dossiers: Mapping of slug to parsed dossier dict.

    Outputs:
        Dictionary with ``dossier_count`` and systemic defect counts.

    Failure behaviour:
        Never raises; tolerates partial or test fixture corpora of any size.
    """
    total = len(dossiers)
    dpa_licensor = 0
    vat_in_fee = 0
    cit_in_energy = 0
    waemu_prose_mismatch = 0

    for doc in dossiers.values():
        dp = doc.get("data_protection")
        vat = doc.get("vat")
        cit = doc.get("cit")
        fintech = doc.get("sectors", {}).get("fintech")
        energy = doc.get("sectors", {}).get("energy & manufacturing")
        s2_prose = doc.get("section2_prose")
        bloc_keys = {(b.canonical or b.value).upper() for b in doc.get("regional_blocs", [])}

        if fintech and dp and dp.value and dp.value in fintech.value and "licensing for payments" in fintech.value.lower():
            dpa_licensor += 1
        if fintech and vat and vat.value and f"({vat.value})" in fintech.value:
            vat_in_fee += 1
        if energy and cit and cit.value and f"energy regulator: {cit.value.lower()}" in energy.value.lower():
            cit_in_energy += 1
        if s2_prose and "waemu/ecowas/eac" in s2_prose.value.lower() and not (bloc_keys & {"WAEMU", "ECOWAS", "EAC"}):
            waemu_prose_mismatch += 1

    return {
        "dossier_count": total,
        "dpa_as_payments_licensor": dpa_licensor,
        "vat_in_fee_slot": vat_in_fee,
        "cit_in_energy_regulator_slot": cit_in_energy,
        "waemu_prose_outside_blocs": waemu_prose_mismatch,
    }


def _collect_route_flags_phase2(
    home_doc: dict[str, Any],
    target_doc: dict[str, Any],
    comparisons: dict[str, Any],
    blocs_cmp: dict[str, Any],
    corpus_stats: dict[str, Any],
) -> list[dict[str, Any]]:
    """Build baseline scoped flags from parse notes and comparison findings.

    Purpose:
        Populate ``flags`` in Phase 2 (before ``validate.py`` adds the full V01–V17
        registry in Phase 3) so template banners, C2 Data Confidence scoring, and C5
        conflicts work end-to-end immediately.

    Inputs:
        home_doc: Parsed home dossier dict.
        target_doc: Parsed target dossier dict.
        comparisons: Dict of regulator, sector-step, tax, and language comparisons.
        blocs_cmp: Output of ``compare_blocs``.
        corpus_stats: Corpus-wide counts from ``_compute_corpus_stats``.

    Outputs:
        List of structured Flag dictionaries.

    Failure behaviour:
        Never raises.
    """
    flags: list[dict[str, Any]] = []
    total = corpus_stats["dossier_count"]
    regs = comparisons["regulators"]
    steps = comparisons["sector_steps"]
    taxes = comparisons["taxes"]

    # --- Template-scope systemic defects (shown in banner, excluded from Data Confidence) ---
    sec_reg = regs["sector_regulator"]
    if sec_reg["any_section4_conflict"]:
        ev = []
        if sec_reg["home"]["section4_named_field"]:
            ev.append(sec_reg["home"]["section4_named_field"])
        if sec_reg["target"]["section4_named_field"]:
            ev.append(sec_reg["target"]["section4_named_field"])
        if sec_reg["sector_key"] == "fintech":
            flags.append(
                _make_flag(
                    rule_id="TPL-S4-LICENSOR",
                    severity="high",
                    scope="template",
                    confidence="in-dossier",
                    message=(
                        "Section 4 Fintech row names the data protection authority as the "
                        "payments and lending licensor instead of the central bank."
                    ),
                    evidence=ev,
                    why_it_matters="Asking a privacy office for a payment licence wastes time because central banks handle financial licensing.",
                    suggested_check="Confirm payment and lending licensing directly with the central bank named in Section 2.",
                    affected_count=corpus_stats["dpa_as_payments_licensor"],
                    corpus_total=total,
                )
            )
        elif sec_reg["sector_key"] == "energy & manufacturing":
            flags.append(
                _make_flag(
                    rule_id="TPL-S4-CIT-LEAK",
                    severity="high",
                    scope="template",
                    confidence="in-dossier",
                    message=(
                        "Section 4 Energy & manufacturing row places the corporate income "
                        "tax rate inside the Energy regulator slot."
                    ),
                    evidence=ev,
                    why_it_matters="A tax percentage is not a regulator name, so relying on Section 4 alone hides the real licensing body.",
                    suggested_check="Use the energy authority named in Section 3 and confirm its mandate directly.",
                    affected_count=corpus_stats["cit_in_energy_regulator_slot"],
                    corpus_total=total,
                )
            )

    if steps["has_template_flagged_steps"] and steps["sector_key"] == "fintech":
        vat_fee_ev = [
            s["field"]
            for s in (steps["home_steps"] + steps["target_steps"])
            if s["template_flagged"] and "VAT" in (s["flag_reason"] or "")
        ]
        if vat_fee_ev:
            flags.append(
                _make_flag(
                    rule_id="TPL-S4-VAT-LEAK",
                    severity="high",
                    scope="template",
                    confidence="in-dossier",
                    message=(
                        "Section 4 Fintech row inserts the Section 5 VAT percentage inside "
                        "the data-protection registration fee slot."
                    ),
                    evidence=vat_fee_ev,
                    why_it_matters="A sales-tax percentage is not a registration fee, so budgeting from this cell would be misleading.",
                    suggested_check="Ask the national data protection authority for its actual current registration fee schedule.",
                    affected_count=corpus_stats["vat_in_fee_slot"],
                    corpus_total=total,
                )
            )

    # --- Country-scope & bloc-scope flags (drive deterministic Data Confidence) ---
    # 1. Parse notes on home or target (missing sections/fields, non-ISO currency codes).
    for side_label, doc in (("Home", home_doc), ("Target", target_doc)):
        for note in doc.get("parse_notes", []):
            if note["kind"] == "currency_zone_no_bank":
                continue
            sev = "high" if note["kind"] in ("missing_section", "missing_field", "read_error") else "med"
            ev_field = Field(
                value=note["message"],
                file=note["file"],
                section=str(note["section"]),
                line=int(note["line"]),
                raw=note.get("raw", ""),
            )
            fdict = ev_field.to_dict()
            fdict["citation"] = ev_field.citation()
            flags.append(
                _make_flag(
                    rule_id="PARSE-NOTE",
                    severity=sev,
                    scope="country",
                    confidence="in-dossier",
                    message=f"{side_label} dossier parse note ({note['kind']}): {note['message']}",
                    evidence=[fdict],
                    why_it_matters="A missing or non-standard dossier entry means key launch data may be incomplete.",
                    suggested_check="Inspect the source dossier line and confirm the figure with the relevant national ministry or central bank.",
                )
            )

    # 2. Same DPA acronym with different expansions across the two dossiers (bloc/route inconsistency).
    dp = regs["data_protection"]
    if dp["same_acronym_different_expansion"]:
        scope = "bloc" if blocs_cmp["shared_keys"] else "country"
        flags.append(
            _make_flag(
                rule_id="DPA-EXPANSION-MISMATCH",
                severity="med",
                scope=scope,
                confidence="in-dossier",
                message=(
                    f"Both dossiers use the data-protection acronym '{dp['home_acronym']}' "
                    f"with different full names ('{dp['home_expansion']}' vs '{dp['target_expansion']}')."
                ),
                evidence=[dp["home_field"], dp["target_field"]],
                why_it_matters="Conflicting agency names suggest the dossier entry may be templated rather than verified against national law.",
                suggested_check="Confirm the official legal name and active registration office of each country's privacy regulator directly.",
            )
        )

    # 3. Placeholder values ("verify", "TBD", "N/A") in key regulator/agency slots.
    for side_label, doc in (("Home", home_doc), ("Target", target_doc)):
        for fld_key, label in (
            ("central_bank", "central bank"),
            ("data_protection", "data protection authority"),
            ("energy_regulator", "energy regulator"),
            ("investment_agency", "investment promotion agency"),
        ):
            fld: Optional[Field] = doc.get(fld_key)
            if fld and _PLACEHOLDER_RE.search(fld.value):
                # Energy regulator placeholder is low-severity when not in energy sector.
                is_energy = comparisons["sector_steps"]["sector_key"] == "energy & manufacturing"
                sev = "high" if fld_key in ("central_bank", "data_protection") or (fld_key == "energy_regulator" and is_energy) else "med"
                fdict = fld.to_dict()
                fdict["citation"] = fld.citation()
                flags.append(
                    _make_flag(
                        rule_id="PLACEHOLDER-VALUE",
                        severity=sev,
                        scope="country",
                        confidence="in-dossier",
                        message=f"{side_label} dossier has placeholder text in {label}: '{fld.value}'.",
                        evidence=[fdict],
                        why_it_matters="The dossier does not name a verified office to contact for this step.",
                        suggested_check=f"Check the national government portal or Ministry of Finance/Commerce for the current {label}.",
                    )
                )

    # 4. Compound or non-numeric tax cells (CIT / VAT).
    for tax_label, tkey in (("Corporate income tax (CIT)", "cit"), ("VAT / sales tax", "vat")):
        tcmp = taxes[tkey]
        if not tcmp["comparable"]:
            ev = [f for f in (tcmp["home_field"], tcmp["target_field"]) if f is not None]
            reasons = []
            if tcmp["home_compound"] or tcmp["target_compound"]:
                reasons.append("compound/multi-rate cell")
            if tcmp["home_non_numeric"] or tcmp["target_non_numeric"]:
                reasons.append("non-numeric rate")
            flags.append(
                _make_flag(
                    rule_id="TAX-UNCOMPARABLE",
                    severity="med",
                    scope="country",
                    confidence="in-dossier",
                    message=(
                        f"{tax_label} cannot be subtracted directly ({', '.join(reasons)}); "
                        "all rates are shown without computing a single delta."
                    ),
                    evidence=ev,
                    why_it_matters="Different business sectors or company sizes can face different tax rates, so a single subtraction could mislead your budget.",
                    suggested_check="Confirm which tax bracket applies to your company with each country's national revenue authority.",
                )
            )

    # 5. Unconfirmed single-sided bloc qualifiers (e.g. "observer" or "verify").
    for side_label, entries in (("Home", blocs_cmp["only_in_home"]), ("Target", blocs_cmp["only_in_target"])):
        for entry in entries:
            if entry["qualifier"] and entry["qualifier"].lower() in ("observer", "verify"):
                flags.append(
                    _make_flag(
                        rule_id="BLOC-QUALIFIER-UNCONFIRMED",
                        severity="low",
                        scope="bloc",
                        confidence="in-dossier",
                        message=(
                            f"{side_label} dossier lists '{entry['raw_value']}', which carries "
                            f"a '{entry['qualifier']}' qualifier and is absent from the partner dossier."
                        ),
                        evidence=[entry["field"]],
                        why_it_matters="Observer or unverified bloc status does not grant the trade or licensing benefits of full membership.",
                        suggested_check="Do not rely on this bloc for cross-border licensing; confirm membership status on the bloc's official registry.",
                    )
                )

    return flags


def compute_data_confidence(flags: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute the deterministic Data Confidence label from country & bloc flags only (C2).

    Purpose:
        Calculate High (0 high-severity), Medium (1–2 high-severity), or Low (3+
        high-severity) exclusively over ``country``-scope and ``bloc``-scope flags so
        corpus-wide template defects never drown out route-specific signal.

    Inputs:
        flags: Full list of Flag dicts for the route.

    Outputs:
        Score dictionary containing ``label``, ``counts`` (high/med/low/total),
        ``template_flag_count``, and explicit non-legal-risk disclaimers.

    Failure behaviour:
        Never raises.
    """
    route_flags = [f for f in flags if f.get("scope") in ("country", "bloc")]
    template_flags = [f for f in flags if f.get("scope") == "template"]

    high_n = sum(1 for f in route_flags if f.get("severity") == "high")
    med_n = sum(1 for f in route_flags if f.get("severity") == "med")
    low_n = sum(1 for f in route_flags if f.get("severity") == "low")

    if high_n == 0:
        label = "High"
    elif high_n <= 2:
        label = "Medium"
    else:
        label = "Low"

    return {
        "label": label,
        "counts": {
            "high": high_n,
            "med": med_n,
            "low": low_n,
            "total": len(route_flags),
        },
        "template_flag_count": len(template_flags),
        "note_en": (
            "Measures source-dossier data quality for this route (country & bloc flags only), "
            "never legal risk."
        ),
        "note_fr": (
            "Mesure uniquement la qualité des dossiers sources pour cet itinéraire "
            "(alertes pays et bloc), jamais le risque juridique."
        ),
    }


def collect_external_checks(
    home_slug: str,
    target_slug: str,
    shared_bloc_keys: list[str],
    all_route_blocs: set[str],
    external_checks_data: Optional[list[dict[str, Any]]] = None,
) -> list[dict[str, Any]]:
    """Filter ``data/external_checks.json`` for items relevant to this route (C3).

    Purpose:
        Keep all out-of-dossier checks (e.g. COBAC, real national regulators, bloc
        withdrawals) strictly separated from dossier facts and clearly marked
        ``status: "unverified"``.

    Inputs:
        home_slug: Home country dossier slug.
        target_slug: Target country dossier slug.
        shared_bloc_keys: Canonical bloc keys shared by home and target.
        all_route_blocs: Set of all canonical bloc keys appearing on either side.
        external_checks_data: Optional preloaded list from ``data/external_checks.json``.

    Outputs:
        List of matching external check dicts with ``confidence: "our-check"``.

    Failure behaviour:
        Returns an empty list if ``external_checks.json`` is missing or empty.
    """
    checks = (
        external_checks_data
        if external_checks_data is not None
        else load_json_data("external_checks.json")
    )
    route_countries = {home_slug, target_slug}
    matched: list[dict[str, Any]] = []

    for item in checks:
        item_countries = set(item.get("countries", []))
        item_blocs = set(item.get("blocs", []))
        if (item_countries & route_countries) or (item_blocs & set(shared_bloc_keys)):
            entry = dict(item)
            entry["confidence"] = "our-check"
            entry.setdefault("status", "unverified")
            entry.setdefault("source_url", "")
            matched.append(entry)
    return matched


def _serialise_dossier_fields(doc: dict[str, Any]) -> dict[str, Any]:
    """Serialise key provenance ``Field`` objects of a parsed dossier for ``facts.json``.

    Purpose:
        Embed every parsed field with its exact file, section, line, and raw text
        inside ``facts.json`` so renderers, dashboards, and grounding checkers can
        verify any claim.

    Inputs:
        doc: Parsed dossier dictionary from ``parser.py``.

    Outputs:
        JSON-serialisable dictionary of field representations.

    Failure behaviour:
        Never raises.
    """
    out: dict[str, Any] = {
        "slug": doc["slug"],
        "file": doc["file"],
        "sections_present": list(doc.get("sections_present", [])),
    }
    scalar_keys = (
        "country",
        "author",
        "status",
        "updated",
        "citation_key",
        "capital",
        "currency",
        "currency_name",
        "currency_code",
        "currency_bloc",
        "currency_bank",
        "currency_zone_raw",
        "central_bank",
        "data_protection",
        "energy_regulator",
        "cit",
        "vat",
        "investment_agency",
        "incentives",
    )
    for k in scalar_keys:
        fld: Optional[Field] = doc.get(k)
        if fld is not None:
            d = fld.to_dict()
            d["citation"] = fld.citation()
            out[k] = d
        else:
            out[k] = None

    for list_key in ("regional_blocs", "official_languages", "dominant_languages", "expansion_notes"):
        out[list_key] = [
            {**f.to_dict(), "citation": f.citation()} for f in doc.get(list_key, [])
        ]

    out["sectors"] = {
        sk: {**sf.to_dict(), "citation": sf.citation()}
        for sk, sf in doc.get("sectors", {}).items()
    }
    return out


def build_facts(
    home: str,
    target: str,
    sector: str,
    dossier_dir: Path | str | None = None,
    dossiers: Optional[dict[str, dict[str, Any]]] = None,
    expect_count: Optional[int] = 54,
) -> dict[str, Any]:
    """Build the complete ``facts`` payload for a cross-border route.

    Purpose:
        Wire together parsing, bloc intersection, home-vs-target comparison, scoped
        flags, external unverified checks, and Data Confidence scoring into one
        single source of truth consumed by ``render.py``, ``dashboard.py``, and
        ``summary.py``.

    Inputs:
        home: Home country slug or name.
        target: Target country slug or name.
        sector: Target sector name or alias.
        dossier_dir: Optional path to dossier directory (defaults to ``africa-regulatory/``).
        dossiers: Optional pre-parsed corpus dict to avoid re-parsing in batch runs.
        expect_count: Expected dossier count assertion when parsing corpus (pass
            ``None`` for custom test directories).

    Outputs:
        Complete JSON-serialisable ``facts`` dictionary.

    Failure behaviour:
        Raises ``ValueError`` if home, target, or sector cannot be resolved; all
        dossier-content defects are captured cleanly as flags.
    """
    if dossiers is None:
        dossiers, _, _ = parse_corpus(dossier_dir=dossier_dir, expect_count=expect_count)

    aliases = load_json_data("aliases.json")
    blocs_meta = load_json_data("blocs.json")
    sector_map = load_json_data("sector_map.json")

    home_slug = resolve_country_slug(home, dossiers)
    target_slug = resolve_country_slug(target, dossiers)
    sector_info = resolve_sector(sector, sector_map)

    home_doc = dossiers[home_slug]
    target_doc = dossiers[target_slug]

    blocs_cmp = compare_blocs(home_doc, target_doc, aliases=aliases, blocs_meta=blocs_meta)
    comparisons = {
        "regulators": compare_regulators(home_doc, target_doc, sector_info, aliases=aliases),
        "sector_steps": compare_sector_steps(home_doc, target_doc, sector_info),
        "taxes": compare_taxes(home_doc, target_doc),
        "languages": compare_languages(home_doc, target_doc),
    }

    corpus_stats = _compute_corpus_stats(dossiers)
    flags = _collect_route_flags_phase2(home_doc, target_doc, comparisons, blocs_cmp, corpus_stats)
    scores = compute_data_confidence(flags)

    template_banner = [
        {
            "rule_id": f["rule_id"],
            "affected_count": f.get("affected_count", 0),
            "corpus_total": f.get("corpus_total", corpus_stats["dossier_count"]),
            "message": f["message"],
        }
        for f in flags
        if f.get("scope") == "template"
    ]

    all_route_blocs = {
        e["canonical"] for e in blocs_cmp["home_all"] + blocs_cmp["target_all"]
    }
    our_checks = collect_external_checks(
        home_slug=home_slug,
        target_slug=target_slug,
        shared_bloc_keys=blocs_cmp["shared_keys"],
        all_route_blocs=all_route_blocs,
    )

    home_name = home_doc["country"].value if home_doc.get("country") else home_slug
    target_name = target_doc["country"].value if target_doc.get("country") else target_slug

    return {
        "meta": {
            "tool": "Passerelle",
            "tagline_en": "Cross the border, verify first.",
            "tagline_fr": "Franchir la frontière, vérifier d'abord.",
            "team": "Christopher Damian Munene, Mark Lekayia (Group 1, IBM x MC Studio Dev Day)",
            "disclaimer_en": (
                "Planning reference only — not legal, tax, or financial advice. "
                "Verify every figure and authority directly before acting."
            ),
            "disclaimer_fr": (
                "Référence de planification uniquement — ce document ne constitue pas un "
                "conseil juridique, fiscal ou financier. Vérifiez chaque élément avant d'agir."
            ),
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sector_key": sector_info["key"],
            "sector_display_en": sector_info["display_en"],
            "sector_display_fr": sector_info["display_fr"],
            "home_slug": home_slug,
            "target_slug": target_slug,
            "home_country": home_name,
            "target_country": target_name,
            "home_file": home_doc["file"],
            "target_file": target_doc["file"],
            "home_title_line": home_doc["country"].line if home_doc.get("country") else 1,
            "target_title_line": target_doc["country"].line if target_doc.get("country") else 1,
            "home_updated": home_doc["updated"].value if home_doc.get("updated") else None,
            "target_updated": target_doc["updated"].value if target_doc.get("updated") else None,
        },
        "fields": {
            "home": _serialise_dossier_fields(home_doc),
            "target": _serialise_dossier_fields(target_doc),
        },
        "comparisons": comparisons,
        "blocs": blocs_cmp,
        "flags": flags,
        "template_banner": template_banner,
        "our_checks": our_checks,
        "scores": scores,
        "corpus_stats": corpus_stats,
    }


def save_facts(facts: dict[str, Any], out_path: Path | str) -> Path:
    """Persist ``facts`` to disk as UTF-8 pretty-printed JSON.

    Purpose:
        Write ``facts.json`` so ``render.py``, ``dashboard.py``, ``summary.py``, and
        ``audit.py`` all operate on the same immutable factual ground truth.

    Inputs:
        facts: Dictionary returned by ``build_facts``.
        out_path: Destination file path.

    Outputs:
        ``Path`` to the written JSON file.

    Failure behaviour:
        Creates parent directories automatically; raises ``OSError`` only on write error.
    """
    target = Path(out_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(facts, indent=2, ensure_ascii=False), encoding="utf-8")
    return target
