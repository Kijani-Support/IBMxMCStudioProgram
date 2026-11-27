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

from blocs import compare_blocs, extract_canonical_blocs, load_json_data
from compare import (
    compare_languages,
    compare_regulators,
    compare_sector_steps,
    compare_taxes,
    resolve_sector,
)
from parser import Field, parse_corpus
from validate import (
    build_bloc_consistency_matrix,
    build_demo_shortlist,
    run_validation_registry,
)


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
    expected_currency = load_json_data("expected_currency_by_bloc.json")

    # Build shared sub-regional bloc consistency matrices (e.g. all 6 CEMAC members).
    subregional_shared = [
        b["canonical"] for b in blocs_cmp["shared"] if b["canonical"] != "African Union"
    ]
    bloc_matrices: dict[str, dict[str, Any]] = {}
    bloc_member_slugs: set[str] = {home_slug, target_slug}
    for bkey in subregional_shared:
        matrix = build_bloc_consistency_matrix(
            bkey,
            dossiers,
            aliases=aliases,
            expected_currency=expected_currency,
        )
        if matrix["member_count"] > 0:
            bloc_matrices[bkey] = matrix
            bloc_member_slugs.update(r["slug"] for r in matrix["rows"])

    # Run the lean validation rule registry across the full corpus with route context.
    val_context = {
        "home_slug": home_slug,
        "target_slug": target_slug,
        "sector_key": sector_info["key"],
        "shared_blocs": blocs_cmp["shared_keys"],
        "bloc_member_slugs": bloc_member_slugs,
        "aliases": aliases,
        "expected_currency": expected_currency,
    }
    flags = run_validation_registry(dossiers, context=val_context)
    scores = compute_data_confidence(flags)

    template_banner = [
        {
            "rule_id": f["rule_id"],
            "v_number": f["v_number"],
            "affected_count": f.get("affected_count", 0),
            "corpus_total": corpus_stats["dossier_count"],
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
    demo_shortlist = build_demo_shortlist(flags, our_checks, limit=6)

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
        "bloc_matrices": bloc_matrices,
        "flags": flags,
        "template_banner": template_banner,
        "our_checks": our_checks,
        "demo_shortlist": demo_shortlist,
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
