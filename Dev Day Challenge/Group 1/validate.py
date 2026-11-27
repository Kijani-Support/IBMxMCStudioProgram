"""Passerelle (EN: "Gateway") — Lean Validation Rule Registry & Bloc Matrix.

Tagline: "Franchir la frontière, vérifier d'abord" / "Cross the border, verify first."
Team: Christopher Damian Munene, Mark Lekayia. Group 1, IBM x MC Studio Dev Day.

Purpose:
    Execute the lean Passerelle validation rule registry (V01, V02, V03, V04, V05,
    V06, V07, V08, V10, V12, V20) across the parsed 54-dossier corpus, isolate any
    rule error as ``RULE_ERROR`` without crashing, build shared-bloc consistency
    matrices, persist corpus-wide results to ``data/flags_all.json``, and assemble
    a route-level DEMO SHORTLIST.

Inputs:
    Full parsed corpus dictionary from ``parser.py``, reference JSON files in
    ``data/``, and optional route context (home slug, target slug, shared blocs).

Outputs:
    Structured Flag dictionaries carrying ``rule_id``, ``v_number``, ``severity``,
    ``scope``, ``confidence``, ``message``, ``evidence``, ``why_it_matters``,
    ``suggested_check``, ``affected_count``, ``countries``, and ``params`` for FR
    rendering; plus bloc consistency matrices and ``data/flags_all.json``.

Failure behaviour:
    Any exception inside an individual validation rule is caught, recorded as a
    ``RULE_ERROR`` flag, and skipped so the pipeline never crashes on bad inputs.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Optional

from blocs import extract_canonical_blocs, load_json_data
from compare import normalise_central_bank
from parser import Field, extract_acronym_and_expansion, parse_corpus

# Placeholder regex shared across V04 and V20.
PLACEHOLDER_RE = re.compile(r"\b(verify|tbd|n/a)\b", re.IGNORECASE)

# Percentage matcher used by V02 and V03.
PERCENT_RE = re.compile(r"\d+(?:\.\d+)?\s*%")


def _ser_field(fld: Optional[Field]) -> Optional[dict[str, Any]]:
    """Convert an optional ``Field`` into a JSON-ready dict with inline citation.

    Purpose:
        Guarantee every Flag evidence item preserves exact file, section, line,
        and raw-line provenance created in ``parser.py`` (R2).

    Inputs:
        fld: Optional ``Field`` instance.

    Outputs:
        Dictionary with all ``Field`` attributes plus ``citation``, or ``None``.

    Failure behaviour:
        Never raises.
    """
    if fld is None:
        return None
    d = fld.to_dict()
    d["citation"] = fld.citation()
    return d


def _build_flag(
    rule_id: str,
    v_number: str,
    severity: str,
    scope: str,
    confidence: str,
    message: str,
    evidence: list[Optional[dict[str, Any]]],
    why_it_matters: str,
    suggested_check: str,
    affected_count: int,
    countries: list[str],
    params: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Build a canonical Passerelle Flag dictionary.

    Purpose:
        Enforce a single consistent schema across all validation rules, including
        ``v_number``, ``scope``, ``confidence``, ``affected_count``, ``countries``,
        and optional ``params`` for rule-keyed French rendering (F4, F6).

    Inputs:
        rule_id: Descriptive rule identifier.
        v_number: Rule code (e.g. ``"V01"``, ``"V08"``, or ``"RULE_ERROR"``).
        severity: ``"high"``, ``"med"``, or ``"low"``.
        scope: ``"template"``, ``"country"``, or ``"bloc"``.
        confidence: ``"in-dossier"`` or ``"our-check"``.
        message: Concise English description.
        evidence: List of serialized ``Field`` dicts.
        why_it_matters: Plain-language sentence explaining founder impact.
        suggested_check: Actionable guidance on whom to ask.
        affected_count: Count of dossiers affected by this finding.
        countries: Sorted list of affected country slugs.
        params: Optional dictionary of interpolation values for French templates.

    Outputs:
        Flag dictionary ready for ``facts.json`` and ``data/flags_all.json``.

    Failure behaviour:
        Never raises.
    """
    return {
        "rule_id": rule_id,
        "v_number": v_number,
        "severity": severity,
        "scope": scope,
        "confidence": confidence,
        "message": message,
        "evidence": [e for e in evidence if e is not None],
        "why_it_matters": why_it_matters,
        "suggested_check": suggested_check,
        "affected_count": affected_count,
        "countries": sorted(set(countries)),
        "params": params or {},
    }


def _country_label(doc: dict[str, Any]) -> str:
    """Return a dossier's display country name or slug fallback.

    Purpose:
        Format country names in flag messages dynamically from parsed dossiers
        without any hard-coded country strings (R1).

    Inputs:
        doc: Parsed dossier dict.

    Outputs:
        Display country string.

    Failure behaviour:
        Never raises.
    """
    cf: Optional[Field] = doc.get("country")
    return cf.value if (cf and cf.value) else doc.get("slug", "unknown")


def _route_slugs(context: dict[str, Any]) -> Optional[set[str]]:
    """Return the active route ``{home_slug, target_slug}`` set, or ``None`` in corpus mode.

    Purpose:
        Let rules distinguish route-scoped output (focusing evidence on the active
        pair and shared blocs) from full corpus-wide runs.

    Inputs:
        context: Validation context dict.

    Outputs:
        Set of active route slugs, or ``None`` when running corpus-wide.

    Failure behaviour:
        Never raises.
    """
    h = context.get("home_slug")
    t = context.get("target_slug")
    if h and t:
        return {h, t}
    return None


def rule_v01_dpa_as_licensor(
    dossiers: dict[str, dict[str, Any]],
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    """V01 [high, template]: Section 4 Fintech row names the DPA as payments licensor.

    Purpose:
        Detect dossiers where the Section 4 Fintech compliance row puts the privacy
        regulator in the payments/lending licensing slot instead of the central bank,
        collapsing all corpus hits into ONE template flag.

    Inputs:
        dossiers: Full parsed dossier corpus.
        context: Validation context dictionary.

    Outputs:
        Zero or one collapsed ``V01`` Flag dictionary.

    Failure behaviour:
        Skips dossiers missing Section 2 DPA or Section 4 Fintech rows cleanly.
    """
    # Real-world mistake caught: A fintech founder applies to a data-protection office
    # for a payments or lending licence instead of the central bank / banking supervisor.
    affected: list[str] = []
    evidence: list[dict[str, Any]] = []
    route = _route_slugs(context)
    total = len(dossiers)

    for slug, doc in sorted(dossiers.items()):
        dp: Optional[Field] = doc.get("data_protection")
        fintech: Optional[Field] = doc.get("sectors", {}).get("fintech")
        if dp and fintech and dp.value and dp.value in fintech.value:
            if "licensing for payments" in fintech.value.lower():
                affected.append(slug)
                if route is None or slug in route:
                    ev = _ser_field(fintech)
                    if ev:
                        evidence.append(ev)

    if not affected:
        return []

    # In route mode, keep only the route's own evidence (falling back to first 2 if empty).
    if route is not None and not evidence:
        for slug in affected[:2]:
            ev = _ser_field(dossiers[slug]["sectors"].get("fintech"))
            if ev:
                evidence.append(ev)

    return [
        _build_flag(
            rule_id="S4-DPA-AS-LICENSOR",
            v_number="V01",
            severity="high",
            scope="template",
            confidence="in-dossier",
            message=(
                f"Section 4 Fintech row names the data protection authority as the "
                f"payments and lending licensor instead of the central bank "
                f"({len(affected)} of {total} dossiers)."
            ),
            evidence=evidence if route is not None else evidence[:5],
            why_it_matters="Asking a privacy office for a payment licence wastes time because central banks handle financial licensing.",
            suggested_check="Ask the central bank (or regional banking supervisor), not the privacy regulator, about payment and lending licensing.",
            affected_count=len(affected),
            countries=affected,
            params={"affected_count": len(affected), "corpus_total": total},
        )
    ]


def rule_v02_percent_in_energy_regulator(
    dossiers: dict[str, dict[str, Any]],
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    """V02 [high, template]: Percentage inside the Section 4 Energy regulator slot.

    Purpose:
        Detect dossiers where the Section 4 Energy & manufacturing row writes a
        percentage inside the ``Energy regulator: ...`` slot instead of naming a
        regulator, collapsed into ONE template flag.

    Inputs:
        dossiers: Full parsed dossier corpus.
        context: Validation context dictionary.

    Outputs:
        Zero or one collapsed ``V02`` Flag dictionary.

    Failure behaviour:
        Skips dossiers without an Energy & manufacturing row cleanly.
    """
    # Real-world mistake caught: A founder reads "Energy regulator: 30%" in Section 4
    # and misses the real energy authority listed in Section 3.
    affected: list[str] = []
    evidence: list[dict[str, Any]] = []
    route = _route_slugs(context)
    total = len(dossiers)

    for slug, doc in sorted(dossiers.items()):
        energy_steps: list[Field] = doc.get("sector_steps", {}).get("energy & manufacturing", [])
        if not energy_steps:
            continue
        first_step = energy_steps[0]
        cit: Optional[Field] = doc.get("cit")
        # Catch both explicit percentages ("30%") and non-numeric CIT cells leaked into
        # the "Energy regulator:" slot (e.g. "None at federal level...").
        has_pct_or_cit = bool(
            PERCENT_RE.search(first_step.value)
            or (cit and cit.value and cit.value.lower() in first_step.value.lower())
        )
        if "energy regulator:" in first_step.value.lower() and has_pct_or_cit:
            affected.append(slug)
            if route is None or slug in route:
                ev = _ser_field(first_step)
                if ev:
                    evidence.append(ev)

    if not affected:
        return []

    return [
        _build_flag(
            rule_id="S4-PERCENT-IN-ENERGY-SLOT",
            v_number="V02",
            severity="high",
            scope="template",
            confidence="in-dossier",
            message=(
                f"Section 4 Energy & manufacturing row puts a percentage inside the "
                f"Energy regulator slot instead of an authority name "
                f"({len(affected)} of {total} dossiers)."
            ),
            evidence=evidence if route is not None else evidence[:5],
            why_it_matters="A tax percentage is not an agency name, so reading Section 4 alone hides the real energy regulator.",
            suggested_check="Use the energy regulator named in Section 3 and confirm its current licensing mandate directly.",
            affected_count=len(affected),
            countries=affected,
            params={"affected_count": len(affected), "corpus_total": total},
        )
    ]


def rule_v03_leaked_tax_in_section4(
    dossiers: dict[str, dict[str, Any]],
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    """V03 [high, template]: Section 4 percentage matches Section 5 VAT or CIT.

    Purpose:
        Catch template column-shift errors where Section 5 VAT leaks into the
        Section 4 Fintech registration-fee slot or Section 5 CIT leaks into the
        Section 4 Energy regulator slot, collapsed into ONE template flag.

    Inputs:
        dossiers: Full parsed dossier corpus.
        context: Validation context dictionary.

    Outputs:
        Zero or one collapsed ``V03`` Flag dictionary.

    Failure behaviour:
        Safely handles dossiers with non-numeric or missing VAT/CIT cells.
    """
    # Real-world mistake caught: A startup budgets 18% or 19.25% as a "data protection
    # registration fee" when that number is actually the country's VAT rate leaked from §5.
    affected: list[str] = []
    evidence: list[dict[str, Any]] = []
    route = _route_slugs(context)
    total = len(dossiers)

    for slug, doc in sorted(dossiers.items()):
        vat: Optional[Field] = doc.get("vat")
        cit: Optional[Field] = doc.get("cit")
        fintech: Optional[Field] = doc.get("sectors", {}).get("fintech")
        energy: Optional[Field] = doc.get("sectors", {}).get("energy & manufacturing")

        vat_leaked = bool(
            fintech
            and vat
            and vat.value
            and f"({vat.value})" in fintech.value
            and "data protection registration" in fintech.value.lower()
        )
        cit_leaked = bool(
            energy
            and cit
            and cit.value
            and f"energy regulator: {cit.value.lower()}" in energy.value.lower()
        )
        if vat_leaked or cit_leaked:
            affected.append(slug)
            if route is None or slug in route:
                if vat_leaked and fintech:
                    ev = _ser_field(fintech)
                    if ev:
                        evidence.append(ev)
                elif cit_leaked and energy:
                    ev = _ser_field(energy)
                    if ev:
                        evidence.append(ev)

    if not affected:
        return []

    return [
        _build_flag(
            rule_id="S4-TAX-LEAKED-FROM-S5",
            v_number="V03",
            severity="high",
            scope="template",
            confidence="in-dossier",
            message=(
                f"Section 4 reuses Section 5 VAT or CIT values inside fee or regulator "
                f"slots ({len(affected)} of {total} dossiers)."
            ),
            evidence=evidence if route is not None else evidence[:5],
            why_it_matters="A sales-tax or profit-tax percentage is not a registration fee, so budgeting from Section 4 would be wrong.",
            suggested_check="Ask the national data-protection authority or sector ministry for its current published fee schedule.",
            affected_count=len(affected),
            countries=affected,
            params={"affected_count": len(affected), "corpus_total": total},
        )
    ]


def rule_v04_placeholders(
    dossiers: dict[str, dict[str, Any]],
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    """V04 [med, country]: Placeholder text ('verify', 'TBD', 'N/A') in value cells.

    Purpose:
        Surface unresearched placeholder strings in dossier value cells, emitting
        at most ONE flag per dossier per section so output stays concise.

    Inputs:
        dossiers: Full parsed dossier corpus.
        context: Validation context dictionary.

    Outputs:
        List of ``V04`` Flag dicts (one per dossier per affected section).

    Failure behaviour:
        Skips missing fields without crashing.
    """
    # Real-world mistake caught: A founder treats a placeholder cell ("Verify current
    # agency") as a complete plan and discovers too late that no regulator was identified.
    flags: list[dict[str, Any]] = []
    route = _route_slugs(context)
    target_slugs = sorted(route) if route is not None else sorted(dossiers.keys())

    # Scan value slots in sections 1, 2, 3, and 5 (Section 4 inherits §2/§5 placeholders
    # via the template bug already captured by V01–V03 and V20).
    scan_keys = (
        ("capital", "capital"),
        ("currency", "currency"),
        ("central_bank", "central bank"),
        ("data_protection", "data protection authority"),
        ("energy_regulator", "energy regulator"),
        ("cit", "corporate income tax"),
        ("vat", "VAT / sales tax"),
        ("investment_agency", "investment promotion agency"),
        ("incentives", "incentives"),
    )

    for slug in target_slugs:
        doc = dossiers.get(slug)
        if not doc:
            continue
        cname = _country_label(doc)
        by_section: dict[str, list[tuple[str, Field]]] = defaultdict(list)

        for key, label in scan_keys:
            fld: Optional[Field] = doc.get(key)
            if fld and fld.value and PLACEHOLDER_RE.search(fld.value):
                by_section[fld.section].append((label, fld))

        for bf in doc.get("regional_blocs", []):
            if PLACEHOLDER_RE.search(bf.value):
                by_section[bf.section].append(("regional blocs", bf))

        for sec, hits in sorted(by_section.items()):
            details = "; ".join(f"{lbl}: '{f.value}'" for lbl, f in hits)
            ev = [_ser_field(f) for _, f in hits]
            flags.append(
                _build_flag(
                    rule_id=f"PLACEHOLDER-S{sec}",
                    v_number="V04",
                    severity="med",
                    scope="country",
                    confidence="in-dossier",
                    message=f"{cname} dossier contains placeholder text in section {sec} ({details}).",
                    evidence=ev,
                    why_it_matters="The dossier does not yet name a verified office or confirmed figure for this step.",
                    suggested_check="Check the national government portal or Ministry of Finance/Commerce for the current official agency or rate.",
                    affected_count=1,
                    countries=[slug],
                    params={"country": cname, "section": sec, "detail": details},
                )
            )

    return flags


def rule_v05_currency_matches_bloc(
    dossiers: dict[str, dict[str, Any]],
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    """V05 [high, bloc]: Currency code differs from monetary-union expected code.

    Purpose:
        Verify that every dossier claiming membership in a monetary union listed in
        ``data/expected_currency_by_bloc.json`` carries one of that union's expected
        ISO currency codes.

    Inputs:
        dossiers: Full parsed dossier corpus.
        context: Validation context containing ``aliases`` and ``expected_currency``.

    Outputs:
        List of ``V05`` Flag dicts for any mismatching member.

    Failure behaviour:
        Skips countries with no monetary-union membership or missing currency safely.
    """
    # Real-world mistake caught: A startup assumes single-currency settlement inside a
    # monetary union when the dossier actually lists the wrong currency code.
    aliases = context.get("aliases") or load_json_data("aliases.json")
    expected_map = context.get("expected_currency") or load_json_data(
        "expected_currency_by_bloc.json"
    )
    scope_slugs = context.get("bloc_member_slugs")
    target_slugs = sorted(scope_slugs) if scope_slugs is not None else sorted(dossiers.keys())
    flags: list[dict[str, Any]] = []

    for slug in target_slugs:
        doc = dossiers.get(slug)
        if not doc:
            continue
        cname = _country_label(doc)
        cc_field: Optional[Field] = doc.get("currency_code")
        actual_code = cc_field.value if cc_field else "<MISSING>"
        blocs = extract_canonical_blocs(doc, aliases)

        for entry in blocs:
            canon = entry["canonical"]
            if entry["qualifier"] in ("observer", "dormant", "verify"):
                continue
            exp_info = expected_map.get(canon)
            if not exp_info:
                continue
            expected_codes = exp_info.get("currencies", [])
            if expected_codes and actual_code not in expected_codes:
                flags.append(
                    _build_flag(
                        rule_id="CURRENCY-BLOC-MISMATCH",
                        v_number="V05",
                        severity="high",
                        scope="bloc",
                        confidence="in-dossier",
                        message=(
                            f"{cname} lists currency '{actual_code}' but belongs to {canon}, "
                            f"whose expected currency is {'/'.join(expected_codes)}."
                        ),
                        evidence=[_ser_field(doc.get("currency")), entry["field"]],
                        why_it_matters="A wrong currency code breaks foreign-exchange assumptions and payment-rail planning.",
                        suggested_check="Confirm the legal tender and monetary-union status with the central bank.",
                        affected_count=1,
                        countries=[slug],
                        params={
                            "country": cname,
                            "actual": actual_code,
                            "bloc": canon,
                            "expected": "/".join(expected_codes),
                        },
                    )
                )

    return flags


def rule_v06_bloc_symmetry(
    dossiers: dict[str, dict[str, Any]],
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    """V06 [med, bloc]: Bloc membership asymmetry based on corpus evidence.

    Purpose:
        Flag unconfirmed membership claims (blocs carrying ``observer`` or ``verify``
        qualifiers, or singleton non-AU blocs with no partner corroboration in the
        corpus), restricted to the active route and shared blocs in route mode.

    Inputs:
        dossiers: Full parsed dossier corpus.
        context: Validation context containing ``aliases`` and optional route keys.

    Outputs:
        List of ``V06`` Flag dicts.

    Failure behaviour:
        Handles dossiers with empty bloc lists safely.
    """
    # Real-world mistake caught: A founder assumes cross-border free-movement or trade
    # rights from an unconfirmed observer-status bloc claim that partner dossiers do not share.
    aliases = context.get("aliases") or load_json_data("aliases.json")
    route = _route_slugs(context)
    scope_slugs = route if route is not None else set(dossiers.keys())

    # Count full-member (non-observer, non-verify) corpus support per canonical bloc.
    bloc_members: dict[str, list[str]] = defaultdict(list)
    doc_blocs: dict[str, list[dict[str, Any]]] = {}
    for slug, doc in sorted(dossiers.items()):
        entries = extract_canonical_blocs(doc, aliases)
        doc_blocs[slug] = entries
        for e in entries:
            if not e["qualifier"] or e["qualifier"].lower() not in ("observer", "verify"):
                bloc_members[e["canonical"]].append(slug)

    flags: list[dict[str, Any]] = []
    for slug in sorted(scope_slugs):
        doc = dossiers.get(slug)
        if not doc:
            continue
        cname = _country_label(doc)
        for entry in doc_blocs.get(slug, []):
            qual = (entry["qualifier"] or "").lower()
            canon = entry["canonical"]
            # Flag either an unconfirmed observer/verify qualifier OR a singleton bloc
            # claimed by only 1 dossier in the entire 54-country corpus.
            is_unconfirmed_qual = qual in ("observer", "verify")
            is_singleton_bloc = len(bloc_members.get(canon, [])) == 1 and canon != "African Union"
            if is_unconfirmed_qual or is_singleton_bloc:
                reason = (
                    f"carries '{entry['qualifier']}' qualifier"
                    if is_unconfirmed_qual
                    else "listed by only 1 dossier across all 54 countries"
                )
                flags.append(
                    _build_flag(
                        rule_id="BLOC-ASYMMETRY",
                        v_number="V06",
                        severity="med",
                        scope="bloc",
                        confidence="in-dossier",
                        message=(
                            f"{cname} lists '{entry['raw_value']}' ({reason}; unconfirmed "
                            "by partner dossiers)."
                        ),
                        evidence=[entry["field"]],
                        why_it_matters="Observer or single-country bloc claims do not guarantee shared trade, customs, or licensing rules.",
                        suggested_check="Do not plan licensing around this bloc; verify full membership on the bloc's official member list.",
                        affected_count=1,
                        countries=[slug],
                        params={"country": cname, "detail": entry["raw_value"]},
                    )
                )

    return flags


def rule_v07_central_bank_siblings(
    dossiers: dict[str, dict[str, Any]],
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    """V07 [med, bloc]: Central bank differs from monetary-union siblings after aliases.

    Purpose:
        Confirm that every member of a shared-central-bank monetary union normalises
        through ``data/aliases.json`` to the union's expected central bank, flagging
        any sibling that diverges.

    Inputs:
        dossiers: Full parsed dossier corpus.
        context: Validation context containing ``aliases`` and ``expected_currency``.

    Outputs:
        List of ``V07`` Flag dicts for any diverging monetary-union member.

    Failure behaviour:
        Skips blocs without a shared central bank safely.
    """
    # Real-world mistake caught: A dossier inside a single-central-bank monetary union
    # names the wrong monetary authority, sending founders to a non-existent national bank.
    aliases = context.get("aliases") or load_json_data("aliases.json")
    expected_map = context.get("expected_currency") or load_json_data(
        "expected_currency_by_bloc.json"
    )
    scope_slugs = context.get("bloc_member_slugs")
    target_slugs = sorted(scope_slugs) if scope_slugs is not None else sorted(dossiers.keys())
    flags: list[dict[str, Any]] = []

    for slug in target_slugs:
        doc = dossiers.get(slug)
        if not doc:
            continue
        cname = _country_label(doc)
        cb_field: Optional[Field] = doc.get("central_bank")
        cb_canon = normalise_central_bank(cb_field.value if cb_field else None, aliases)
        for entry in extract_canonical_blocs(doc, aliases):
            canon = entry["canonical"]
            if entry["qualifier"] in ("observer", "dormant", "verify"):
                continue
            exp_cb = (expected_map.get(canon) or {}).get("central_bank")
            if exp_cb and cb_canon != exp_cb:
                flags.append(
                    _build_flag(
                        rule_id="CENTRAL-BANK-BLOC-DIFF",
                        v_number="V07",
                        severity="med",
                        scope="bloc",
                        confidence="in-dossier",
                        message=(
                            f"{cname} normalises to central bank '{cb_canon or '<MISSING>'}' "
                            f"instead of expected {canon} central bank '{exp_cb}'."
                        ),
                        evidence=[_ser_field(cb_field), entry["field"]],
                        why_it_matters="Different central banks mean separate financial licensing rules and currency oversight.",
                        suggested_check="Confirm the governing central bank directly with the monetary union or Ministry of Finance.",
                        affected_count=1,
                        countries=[slug],
                        params={
                            "country": cname,
                            "actual": cb_canon or "<MISSING>",
                            "bloc": canon,
                            "expected": exp_cb,
                        },
                    )
                )

    return flags


def rule_v08_dpa_acronym_expansions(
    dossiers: dict[str, dict[str, Any]],
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    """V08 [med, bloc]: Same DPA acronym expanded differently across dossiers (F2).

    Purpose:
        Detect when two or more dossiers share the same data-protection acronym
        (such as ``CNPD``) with conflicting full expansions. In route mode, restricts
        checks to the active route pair and their shared blocs; corpus-wide counts
        are produced when running without route scope (``data/flags_all.json``).

    Inputs:
        dossiers: Full parsed dossier corpus.
        context: Validation context with optional ``home_slug``, ``target_slug``,
            and ``bloc_member_slugs``.

    Outputs:
        List of ``V08`` Flag dicts (severity ``med`` per F2).

    Failure behaviour:
        Ignores dossiers whose DPA cell carries no extractable acronym.
    """
    # Real-world mistake caught: Two dossiers reuse the same privacy-regulator acronym
    # with different legal names, signalling copy-pasted template entries instead of real law.
    route = _route_slugs(context)
    if route is not None:
        scope_slugs = set(route) | set(context.get("bloc_member_slugs") or set())
    else:
        scope_slugs = set(dossiers.keys())

    # Group (acronym -> expansion -> [(slug, Field)]) within the active scope.
    by_acronym: dict[str, dict[str, list[tuple[str, Field]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for slug in sorted(scope_slugs):
        doc = dossiers.get(slug)
        if not doc:
            continue
        dp: Optional[Field] = doc.get("data_protection")
        if not dp or not dp.value:
            continue
        pair = extract_acronym_and_expansion(dp.value)
        if pair is None:
            continue
        acr, exp = pair
        by_acronym[acr.upper()][exp].append((slug, dp))

    flags: list[dict[str, Any]] = []
    for acr, exp_map in sorted(by_acronym.items()):
        if len(exp_map) < 2:
            continue
        all_hits = [item for hits in exp_map.values() for item in hits]
        involved_slugs = [slug for slug, _ in all_hits]
        if route is not None and not (set(involved_slugs) & route):
            continue

        detail_parts = [
            f"'{exp}' ({', '.join(_country_label(dossiers[s]) for s, _ in hits)})"
            for exp, hits in sorted(exp_map.items())
        ]
        detail_str = " vs ".join(detail_parts)
        ev = [_ser_field(f) for _, f in all_hits]
        flags.append(
            _build_flag(
                rule_id="DPA-EXPANSION-MISMATCH",
                v_number="V08",
                severity="med",
                scope="bloc",
                confidence="in-dossier",
                message=(
                    f"Data-protection acronym '{acr}' has {len(exp_map)} different "
                    f"expansions across dossiers: {detail_str}."
                ),
                evidence=ev,
                why_it_matters="Conflicting agency names suggest the dossier entry may be templated rather than verified against national law.",
                suggested_check="Confirm the official legal name and active registration office of each country's privacy regulator directly.",
                affected_count=len(set(involved_slugs)),
                countries=involved_slugs,
                params={"acronym": acr, "detail": detail_str},
            )
        )

    return flags


def rule_v10_tax_anomalies(
    dossiers: dict[str, dict[str, Any]],
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    """V10 [high if 0 or >40, else med, country]: Out-of-range, compound, or non-numeric tax.

    Purpose:
        Flag any Section 5 CIT or VAT cell that is non-numeric, compound/multi-rate,
        zero, or above 40%, assigning ``high`` severity to out-of-range figures and
        ``med`` severity to compound/non-numeric cells.

    Inputs:
        dossiers: Full parsed dossier corpus.
        context: Validation context dictionary.

    Outputs:
        List of ``V10`` Flag dicts.

    Failure behaviour:
        Safely skips missing CIT/VAT cells (which are caught by V12).
    """
    # Real-world mistake caught: A founder plugs a compound ("30% (33% for some sectors)")
    # or outlier (50% CIT) figure straight into a financial model and misprices their product.
    route = _route_slugs(context)
    target_slugs = sorted(route) if route is not None else sorted(dossiers.keys())
    flags: list[dict[str, Any]] = []

    for slug in target_slugs:
        doc = dossiers.get(slug)
        if not doc:
            continue
        cname = _country_label(doc)
        for tax_label, key in (("CIT", "cit"), ("VAT", "vat")):
            tf: Optional[Field] = doc.get(key)
            if tf is None:
                continue
            nums: list[float] = list(tf.meta.get("numbers", []))
            is_compound = bool(tf.meta.get("is_compound", False))
            out_of_range = any(n == 0 or n > 40 for n in nums)
            non_numeric = len(nums) == 0

            if not (out_of_range or is_compound or non_numeric):
                continue

            reasons: list[str] = []
            if out_of_range:
                reasons.append("rate is 0% or above 40%")
            if non_numeric:
                reasons.append("non-numeric rate")
            elif is_compound:
                reasons.append("compound/multi-rate cell")

            sev = "high" if out_of_range else "med"
            reason_str = ", ".join(reasons)
            flags.append(
                _build_flag(
                    rule_id=f"TAX-{tax_label}-ANOMALY",
                    v_number="V10",
                    severity=sev,
                    scope="country",
                    confidence="in-dossier",
                    message=f"{cname} {tax_label} cell '{tf.value}' flagged ({reason_str}).",
                    evidence=[_ser_field(tf)],
                    why_it_matters="Multiple brackets, missing numbers, or extreme tax rates mean a simple headline figure can mislead your financial forecast.",
                    suggested_check="Confirm the exact tax bracket for your sector with the national revenue authority.",
                    affected_count=1,
                    countries=[slug],
                    params={
                        "country": cname,
                        "tax": tax_label,
                        "detail": tf.value,
                        "reason": reason_str,
                    },
                )
            )

    return flags


def rule_v12_missing_structure(
    dossiers: dict[str, dict[str, Any]],
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    """V12 [high, country]: Missing section, required table row, or required slot.

    Purpose:
        Convert parser ``parse_notes`` for missing sections, missing required fields,
        or missing Section 4 rows into ``high``-severity Verify-first flags so
        malformed dossiers never crash the tool (R4).

    Inputs:
        dossiers: Full parsed dossier corpus.
        context: Validation context dictionary.

    Outputs:
        List of ``V12`` Flag dicts.

    Failure behaviour:
        Never raises even on completely empty parsed dossiers.
    """
    # Real-world mistake caught: A truncated or corrupted dossier silently omits the tax
    # or regulator section, making a risky market look clean when data is actually missing.
    route = _route_slugs(context)
    target_slugs = sorted(route) if route is not None else sorted(dossiers.keys())
    structural_kinds = {
        "missing_section",
        "missing_field",
        "missing_sector_rows",
        "read_error",
        "missing_value",
    }
    flags: list[dict[str, Any]] = []

    for slug in target_slugs:
        doc = dossiers.get(slug)
        if not doc:
            continue
        cname = _country_label(doc)
        structural_notes = [
            n for n in doc.get("parse_notes", []) if n.get("kind") in structural_kinds
        ]
        if not structural_notes:
            continue

        summary = "; ".join(n["message"] for n in structural_notes)
        ev = [
            _ser_field(
                Field(
                    value=n["message"],
                    file=n["file"],
                    section=str(n["section"]),
                    line=int(n["line"]),
                    raw=n.get("raw", ""),
                )
            )
            for n in structural_notes
        ]
        flags.append(
            _build_flag(
                rule_id="MISSING-STRUCTURE",
                v_number="V12",
                severity="high",
                scope="country",
                confidence="in-dossier",
                message=f"{cname} dossier has missing required sections or fields: {summary}",
                evidence=ev,
                why_it_matters="Missing sections or table rows leave gaps in the launch brief that could hide mandatory licences or taxes.",
                suggested_check="Inspect the raw dossier file and obtain missing regulatory data directly from national authorities.",
                affected_count=1,
                countries=[slug],
                params={"country": cname, "detail": summary},
            )
        )

    return flags


def _is_unnamed_dpa(dp_field: Optional[Field]) -> bool:
    """Return True when the Section 2 data-protection cell is placeholder-only.

    Purpose:
        Distinguish dossiers that name an actual authority (even with a verify note)
        from dossiers that say only ``"Verify national authority"`` or ``"verify"``.

    Inputs:
        dp_field: Section 2 ``data_protection`` ``Field`` or ``None``.

    Outputs:
        Boolean indicating whether no DPA is named.

    Failure behaviour:
        Never raises.
    """
    if dp_field is None or not dp_field.value.strip():
        return True
    low = dp_field.value.strip().lower()
    return low in ("verify national authority", "verify", "tbd", "n/a") or low.startswith(
        "verify national"
    )


def rule_v20_unnamed_dpa(
    dossiers: dict[str, dict[str, Any]],
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    """V20 [med, country]: No data-protection authority named (placeholder only).

    Purpose:
        Identify dossiers whose Section 2 data-protection slot is a bare placeholder
        (e.g. ``Verify national authority``) and report the corpus-wide ``N of 54``
        prevalence alongside the affected country flag.

    Inputs:
        dossiers: Full parsed dossier corpus.
        context: Validation context dictionary.

    Outputs:
        List of ``V20`` Flag dicts (one per affected country in scope).

    Failure behaviour:
        Never raises on missing DPA fields.
    """
    # Real-world mistake caught: Almost half the dossiers leave privacy regulation as
    # "Verify national authority", leaving consumer-data startups with zero contact info.
    total = len(dossiers)
    unnamed_all = [slug for slug, doc in sorted(dossiers.items()) if _is_unnamed_dpa(doc.get("data_protection"))]
    corpus_n = len(unnamed_all)
    if not unnamed_all:
        return []

    route = _route_slugs(context)
    scope_slugs = sorted(route) if route is not None else unnamed_all
    flags: list[dict[str, Any]] = []

    for slug in scope_slugs:
        if slug not in unnamed_all:
            continue
        doc = dossiers[slug]
        cname = _country_label(doc)
        dp_f = doc.get("data_protection")
        flags.append(
            _build_flag(
                rule_id="DPA-UNNAMED",
                v_number="V20",
                severity="med",
                scope="country",
                confidence="in-dossier",
                message=(
                    f"{cname} names no data-protection authority (placeholder only; "
                    f"{corpus_n} of {total} dossiers share this gap)."
                ),
                evidence=[_ser_field(dp_f)],
                why_it_matters="Without a named privacy regulator, you cannot confirm where to register customer personal-data handling.",
                suggested_check="Ask the Ministry of Digital Economy or Telecommunications which agency enforces personal-data rules.",
                affected_count=corpus_n,
                countries=[slug],
                params={
                    "country": cname,
                    "affected_count": corpus_n,
                    "corpus_total": total,
                },
            )
        )

    return flags


# Ordered lean validation rule registry (Step 1: V01-V08, V10, V12, V20).
RULE_REGISTRY: list[tuple[str, Callable[[dict[str, dict[str, Any]], dict[str, Any]], list[dict[str, Any]]]]] = [
    ("V01", rule_v01_dpa_as_licensor),
    ("V02", rule_v02_percent_in_energy_regulator),
    ("V03", rule_v03_leaked_tax_in_section4),
    ("V04", rule_v04_placeholders),
    ("V05", rule_v05_currency_matches_bloc),
    ("V06", rule_v06_bloc_symmetry),
    ("V07", rule_v07_central_bank_siblings),
    ("V08", rule_v08_dpa_acronym_expansions),
    ("V10", rule_v10_tax_anomalies),
    ("V12", rule_v12_missing_structure),
    ("V20", rule_v20_unnamed_dpa),
]


def run_validation_registry(
    dossiers: dict[str, dict[str, Any]],
    context: Optional[dict[str, Any]] = None,
    registry: Optional[list[tuple[str, Callable]]] = None,
) -> list[dict[str, Any]]:
    """Run every rule in the registry with exception isolation (``RULE_ERROR``).

    Purpose:
        Execute all configured validation functions against the parsed corpus,
        catching any unexpected exception as a ``RULE_ERROR`` flag so a single
        buggy rule never aborts a brief run.

    Inputs:
        dossiers: Full parsed dossier corpus.
        context: Optional route/reference context dictionary.
        registry: Optional custom rule list (defaults to ``RULE_REGISTRY``).

    Outputs:
        Combined list of Flag dictionaries from all rules.

    Failure behaviour:
        Never raises; failed rules emit a ``RULE_ERROR`` flag and execution continues.
    """
    ctx = dict(context or {})
    ctx.setdefault("aliases", load_json_data("aliases.json"))
    ctx.setdefault("expected_currency", load_json_data("expected_currency_by_bloc.json"))
    rules = registry if registry is not None else RULE_REGISTRY

    all_flags: list[dict[str, Any]] = []
    for v_num, fn in rules:
        try:
            produced = fn(dossiers, ctx)
            all_flags.extend(produced)
        except Exception as exc:  # noqa: BLE001 — explicit rule isolation per spec
            all_flags.append(
                _build_flag(
                    rule_id="RULE_ERROR",
                    v_number="RULE_ERROR",
                    severity="med",
                    scope="country",
                    confidence="in-dossier",
                    message=f"Validation rule {v_num} ({fn.__name__}) raised {type(exc).__name__}: {exc}",
                    evidence=[],
                    why_it_matters="One automated validation check could not finish and was skipped safely.",
                    suggested_check="Review the relevant dossier section manually and report the error to engineering.",
                    affected_count=0,
                    countries=[],
                    params={"detail": f"{v_num} ({type(exc).__name__})"},
                )
            )
    return all_flags


def build_bloc_consistency_matrix(
    bloc_key: str,
    dossiers: dict[str, dict[str, Any]],
    aliases: Optional[dict[str, Any]] = None,
    expected_currency: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Build a member-by-member consistency matrix for one regional bloc.

    Purpose:
        Evaluate every member dossier of ``bloc_key`` across six columns (currency,
        central bank, bloc symmetry, DPA naming, placeholders, and country/bloc flag
        counts) with ``ok`` | ``note`` | ``flag`` statuses and line evidence.

    Inputs:
        bloc_key: Canonical regional bloc key (e.g. ``"CEMAC"``).
        dossiers: Full parsed dossier corpus.
        aliases: Optional loaded ``data/aliases.json``.
        expected_currency: Optional loaded ``data/expected_currency_by_bloc.json``.

    Outputs:
        Matrix dict containing ``bloc``, ``member_count``, and ordered ``rows``.

    Failure behaviour:
        Returns an empty ``rows`` list if no dossier belongs to ``bloc_key``.
    """
    alias_data = aliases if aliases is not None else load_json_data("aliases.json")
    exp_map = (
        expected_currency
        if expected_currency is not None
        else load_json_data("expected_currency_by_bloc.json")
    )

    member_slugs: list[str] = []
    for slug, doc in sorted(dossiers.items()):
        blocs = extract_canonical_blocs(doc, alias_data)
        if any(
            e["canonical"] == bloc_key
            and (e["qualifier"] or "").lower() not in ("observer", "verify")
            for e in blocs
        ):
            member_slugs.append(slug)

    if not member_slugs:
        return {"bloc": bloc_key, "member_count": 0, "rows": []}

    # Run all rules across the bloc members (with full corpus visible).
    member_set = set(member_slugs)
    bloc_ctx = {
        "aliases": alias_data,
        "expected_currency": exp_map,
        "bloc_member_slugs": member_set,
    }
    corpus_flags = run_validation_registry(dossiers, bloc_ctx)
    # Index non-template flags by country slug.
    flags_by_slug: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for flg in corpus_flags:
        if flg["scope"] == "template":
            continue
        for cslug in flg.get("countries", []):
            if cslug in member_set:
                flags_by_slug[cslug].append(flg)

    # Detect modal raw central-bank spelling inside the bloc so full-name vs acronym
    # differences show cleanly as a 'note' even when V07 passes after normalisation.
    raw_cb_counts: dict[str, int] = defaultdict(int)
    for slug in member_slugs:
        cb_f = dossiers[slug].get("central_bank")
        if cb_f and cb_f.value:
            raw_cb_counts[cb_f.value] += 1
    modal_cb_raw = max(raw_cb_counts.items(), key=lambda kv: kv[1])[0] if raw_cb_counts else ""

    rows: list[dict[str, Any]] = []
    for slug in member_slugs:
        doc = dossiers[slug]
        cname = _country_label(doc)
        mflags = flags_by_slug.get(slug, [])

        # Column 1: Currency (V05)
        v05_hits = [f for f in mflags if f["v_number"] == "V05"]
        cc_val = doc["currency_code"].value if doc.get("currency_code") else "MISSING"
        cur_cell = {
            "status": "flag" if v05_hits else "ok",
            "label": cc_val,
            "evidence": [_ser_field(doc.get("currency"))],
        }

        # Column 2: Central bank (V07 + raw spelling note)
        v07_hits = [f for f in mflags if f["v_number"] == "V07"]
        cb_f = doc.get("central_bank")
        cb_canon = normalise_central_bank(cb_f.value if cb_f else None, alias_data) or "MISSING"
        if v07_hits:
            cb_status, cb_label = "flag", f"{cb_canon} (differs)"
        elif cb_f and cb_f.value != modal_cb_raw:
            cb_status, cb_label = "note", f"{cb_canon} (full name)"
        else:
            cb_status, cb_label = "ok", cb_canon
        cb_cell = {
            "status": cb_status,
            "label": cb_label,
            "evidence": [_ser_field(cb_f)],
        }

        # Column 3: Bloc symmetry (V06)
        v06_hits = [f for f in mflags if f["v_number"] == "V06"]
        if v06_hits:
            details = ", ".join(f["params"].get("detail", "") for f in v06_hits)
            sym_cell = {
                "status": "flag",
                "label": f"V06 ({details})",
                "evidence": [e for f in v06_hits for e in f["evidence"]],
            }
        else:
            b_ev = [_ser_field(doc["regional_blocs"][0])] if doc.get("regional_blocs") else []
            sym_cell = {"status": "ok", "label": "ok", "evidence": b_ev}

        # Column 4: DPA naming (V08 / V20)
        v08_hits = [f for f in mflags if f["v_number"] == "V08"]
        v20_hits = [f for f in mflags if f["v_number"] == "V20"]
        dp_f = doc.get("data_protection")
        if v08_hits:
            acr = v08_hits[0]["params"].get("acronym", "DPA")
            dpa_cell = {
                "status": "flag",
                "label": f"V08 ({acr} mismatch)",
                "evidence": [_ser_field(dp_f)],
            }
        elif v20_hits:
            dpa_cell = {
                "status": "flag",
                "label": "V20 (unnamed)",
                "evidence": [_ser_field(dp_f)],
            }
        else:
            dpa_cell = {
                "status": "ok",
                "label": dp_f.value if dp_f else "MISSING",
                "evidence": [_ser_field(dp_f)],
            }

        # Column 5: Placeholders (V04)
        v04_hits = [f for f in mflags if f["v_number"] == "V04"]
        if len(v04_hits) >= 2:
            ph_status = "flag"
        elif len(v04_hits) == 1:
            ph_status = "note"
        else:
            ph_status = "ok"
        ph_secs = ",".join(f"§{f['params'].get('section', '?')}" for f in v04_hits)
        ph_cell = {
            "status": ph_status,
            "label": f"{len(v04_hits)} ({ph_secs})" if v04_hits else "0",
            "evidence": [e for f in v04_hits for e in f["evidence"]],
        }

        # Column 6: Flag counts (country + bloc scope)
        h_n = sum(1 for f in mflags if f["severity"] == "high")
        m_n = sum(1 for f in mflags if f["severity"] == "med")
        l_n = sum(1 for f in mflags if f["severity"] == "low")
        cnt_status = "flag" if h_n > 0 else ("note" if m_n > 0 else "ok")
        cnt_cell = {
            "status": cnt_status,
            "label": f"{h_n}H/{m_n}M/{l_n}L ({len(mflags)})",
            "counts": {"high": h_n, "med": m_n, "low": l_n, "total": len(mflags)},
        }

        rows.append(
            {
                "slug": slug,
                "country": cname,
                "file": doc["file"],
                "currency": cur_cell,
                "central_bank": cb_cell,
                "bloc_symmetry": sym_cell,
                "dpa_naming": dpa_cell,
                "placeholders": ph_cell,
                "flag_counts": cnt_cell,
            }
        )

    return {"bloc": bloc_key, "member_count": len(rows), "rows": rows}


def build_demo_shortlist(
    flags: list[dict[str, Any]],
    our_checks: list[dict[str, Any]],
    limit: int = 6,
) -> list[dict[str, Any]]:
    """Select the top 6 most illustrative route flags for the live demo walkthrough.

    Purpose:
        Curate a concise shortlist mixing the strongest in-dossier flags (template,
        bloc, and country scope) with the top external ``our-check`` item so judges
        immediately see provenance, rule IDs, and epistemic separation.

    Inputs:
        flags: Route Flag dictionaries from ``run_validation_registry``.
        our_checks: Matching external checks from ``data/external_checks.json``.
        limit: Maximum number of shortlist items (default 6).

    Outputs:
        Ordered list of up to ``limit`` shortlist dicts with ``rule``, ``location``,
        ``message``, ``why_it_matters``, ``confidence``, and ``severity``.

    Failure behaviour:
        Never raises; returns fewer than ``limit`` items if fewer flags exist.
    """
    # Priority ordering highlights distinct failure classes for the 4-minute walkthrough.
    v_priority = {
        "V01": 1,
        "V03": 2,
        "V08": 3,
        "V10": 4,
        "V06": 5,
        "V04": 6,
        "V12": 0,
        "V05": 2,
        "V07": 4,
        "V20": 7,
        "V02": 8,
    }
    ordered = sorted(flags, key=lambda f: (v_priority.get(f["v_number"], 99), f["rule_id"]))

    shortlist: list[dict[str, Any]] = []
    seen_rules: set[str] = set()
    # Reserve 1 slot for an unverified external our-check item when available.
    dossier_cap = limit - 1 if our_checks else limit

    for flg in ordered:
        if len(shortlist) >= dossier_cap:
            break
        if flg["v_number"] in seen_rules and len(ordered) > dossier_cap:
            continue
        seen_rules.add(flg["v_number"])
        ev_locs = "; ".join(
            f"{e['file']} §{e['section']}, line {e['line']}" for e in flg.get("evidence", [])[:2]
        )
        shortlist.append(
            {
                "rule": flg["v_number"],
                "rule_id": flg["rule_id"],
                "severity": flg["severity"],
                "scope": flg["scope"],
                "confidence": flg["confidence"],
                "location": ev_locs or "corpus-wide",
                "message": flg["message"],
                "why_it_matters": flg["why_it_matters"],
            }
        )

    if our_checks and len(shortlist) < limit:
        top_ext = our_checks[0]
        shortlist.append(
            {
                "rule": top_ext["id"],
                "rule_id": "EXTERNAL-CHECK",
                "severity": "med",
                "scope": "bloc",
                "confidence": "our-check",
                "location": "data/external_checks.json (unverified, outside dossier)",
                "message": top_ext["claim"],
                "why_it_matters": "Highlights an institutional gap absent from the dossiers while keeping external knowledge strictly labelled unverified.",
            }
        )

    return shortlist[:limit]


def run_corpus_validation(
    dossier_dir: Path | str | None = None,
    expect_count: Optional[int] = 54,
    out_path: Path | str | None = None,
) -> dict[str, Any]:
    """Run all 11 validation rules across all 54 dossiers and write ``data/flags_all.json``.

    Purpose:
        Produce the full corpus-wide audit dataset consumed by the dashboard and
        judges to verify Passerelle works uniformly across all 54 countries.

    Inputs:
        dossier_dir: Optional override dossier directory.
        expect_count: Expected dossier count assertion (default 54).
        out_path: Optional destination JSON path (defaults to ``data/flags_all.json``).

    Outputs:
        Payload dictionary containing summary counts by rule and severity, plus all
        corpus flags.

    Failure behaviour:
        Raises only if ``dossier_dir`` is invalid or count assertion fails; rule
        errors become ``RULE_ERROR`` entries.
    """
    dossiers, _, _ = parse_corpus(dossier_dir=dossier_dir, expect_count=expect_count)
    flags = run_validation_registry(dossiers, context={})

    by_rule: dict[str, int] = defaultdict(int)
    by_sev: dict[str, int] = defaultdict(int)
    by_scope: dict[str, int] = defaultdict(int)
    for flg in flags:
        by_rule[flg["v_number"]] += 1
        by_sev[flg["severity"]] += 1
        by_scope[flg["scope"]] += 1

    payload = {
        "dossier_count": len(dossiers),
        "total_flags": len(flags),
        "counts_by_rule": dict(sorted(by_rule.items())),
        "counts_by_severity": dict(sorted(by_sev.items())),
        "counts_by_scope": dict(sorted(by_scope.items())),
        "flags": flags,
    }

    target = (
        Path(out_path)
        if out_path is not None
        else Path(__file__).resolve().parent / "data" / "flags_all.json"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def print_demo_shortlist(shortlist: list[dict[str, Any]]) -> None:
    """Print the 6-item DEMO SHORTLIST in a readable console layout.

    Purpose:
        Give presenters a ready-to-read walkthrough table at the end of a validation
        or CLI run.

    Inputs:
        shortlist: List of shortlist dictionaries returned by ``build_demo_shortlist``.

    Outputs:
        None (writes to stdout).

    Failure behaviour:
        Never raises.
    """
    print("\n=== DEMO SHORTLIST (Top Route Flags) ===")
    for idx, item in enumerate(shortlist, start=1):
        print(
            f"{idx}. [{item['rule']}] ({item['severity']} | {item['confidence']}) "
            f"@ {item['location']}"
        )
        print(f"   Finding: {item['message']}")
        print(f"   Why it matters: {item['why_it_matters']}")


def main() -> None:
    """Run corpus-wide validation, save ``data/flags_all.json``, and print summary.

    Purpose:
        Standalone script entry point for Step 1 verification.

    Inputs:
        None.

    Outputs:
        Writes ``data/flags_all.json`` and prints rule counts to stdout.

    Failure behaviour:
        Exits non-zero only if the dossier directory is missing or count != 54.
    """
    payload = run_corpus_validation(expect_count=54)
    print(f"Validated {payload['dossier_count']} dossiers -> {payload['total_flags']} flags saved to data/flags_all.json")
    print("Counts by rule:", payload["counts_by_rule"])
    print("Counts by severity:", payload["counts_by_severity"])
    print("Counts by scope:", payload["counts_by_scope"])


if __name__ == "__main__":
    main()
