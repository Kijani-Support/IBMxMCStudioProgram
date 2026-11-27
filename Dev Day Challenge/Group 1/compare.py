"""Passerelle (EN: "Gateway") — Home vs Target Comparison Engine.

Tagline: "Franchir la frontière, vérifier d'abord" / "Cross the border, verify first."
Team: Christopher Damian Munene, Mark Lekayia. Group 1, IBM x MC Studio Dev Day.

Purpose:
    Compare home and target dossiers across regulators (central bank, data protection
    authority, and sector regulator resolved via ``data/sector_map.json``), sector
    compliance steps, corporate income tax and VAT (never subtracting floats from
    compound or non-numeric cells), and official vs spoken/business languages.

Inputs:
    Parsed home and target dossier dicts from ``parser.py``, a target sector string,
    and reference JSON maps (``data/aliases.json``, ``data/sector_map.json``).

Outputs:
    Structured comparison dictionaries carrying full ``Field`` provenance on every
    compared figure, authority, and step.

Failure behaviour:
    Never crashes on missing fields, compound taxes, non-numeric rates, or prose
    language cells; marks uncomparable fields explicitly and preserves all raw values.
"""

from __future__ import annotations

import re
from typing import Any, Optional

from blocs import load_json_data
from parser import Field, extract_acronym_and_expansion

# Regex detecting percentages leaked into fee/regulator slots inside Section 4 rows.
PERCENT_RE = re.compile(r"\d+(?:\.\d+)?\s*%")


def normalise_central_bank(raw_name: Optional[str], aliases: dict[str, Any]) -> Optional[str]:
    """Normalise a central bank name through ``data/aliases.json``.

    Purpose:
        Reconcile acronym-only vs full-name spellings (e.g. ``BEAC`` vs its full
        French name) purely through data so no code hard-codes bank names.

    Inputs:
        raw_name: Raw central bank string extracted from Section 2.
        aliases: Loaded ``data/aliases.json`` dictionary.

    Outputs:
        Canonical central bank identifier, or ``None`` if input is empty.

    Failure behaviour:
        Never raises; returns the trimmed raw string when not present in the alias map.
    """
    if not raw_name or not raw_name.strip():
        return None
    cb_map = {k.lower(): v for k, v in aliases.get("central_banks", {}).items()}
    cleaned = raw_name.strip()
    return cb_map.get(cleaned.lower(), cleaned)


def resolve_sector(sector_arg: str, sector_map: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """Resolve a user-supplied sector argument against ``data/sector_map.json``.

    Purpose:
        Map CLI sector strings (including short aliases like ``retail`` or ``energy``)
        to their canonical Sita sector key and primary licensing slot metadata.

    Inputs:
        sector_arg: Sector name passed by the user or CLI.
        sector_map: Optional preloaded ``sector_map.json`` dictionary.

    Outputs:
        Sector metadata dictionary including ``key``, ``display_en``, ``display_fr``,
        ``dossier_row_key``, ``licensing_section``, and ``licensing_slot``.

    Failure behaviour:
        Raises ``ValueError`` listing valid sectors when ``sector_arg`` is unrecognised.
    """
    smap = sector_map if sector_map is not None else load_json_data("sector_map.json")
    aliases = {k.lower(): v for k, v in smap.get("aliases", {}).items()}
    lookup = sector_arg.strip().lower()
    canonical_key = aliases.get(lookup)
    if canonical_key is None or canonical_key not in smap.get("sectors", {}):
        valid = ", ".join(sorted(smap.get("sectors", {}).keys()))
        raise ValueError(f"Unknown sector '{sector_arg}'. Valid sectors: {valid}")
    info = dict(smap["sectors"][canonical_key])
    info["key"] = canonical_key
    return info


def _field_dict(fld: Optional[Field]) -> Optional[dict[str, Any]]:
    """Safely serialise an optional ``Field`` into a dictionary with citation.

    Purpose:
        Keep provenance serialization concise and null-safe across all comparators.

    Inputs:
        fld: Optional ``Field`` instance.

    Outputs:
        Dict with all Field attributes plus ``citation``, or ``None``.

    Failure behaviour:
        Never raises.
    """
    if fld is None:
        return None
    data = fld.to_dict()
    data["citation"] = fld.citation()
    return data


def _extract_sector_regulator_side(
    doc: dict[str, Any],
    sector_info: dict[str, Any],
    aliases: dict[str, Any],
) -> dict[str, Any]:
    """Determine the expected sector regulator vs the body named in Section 4 (C5).

    Purpose:
        Read the licensing contact specified by ``data/sector_map.json`` (e.g. §2
        central bank for fintech, §3 energy regulator for energy) and compare it
        against the first licensing clause in the Section 4 row so conflicts are
        explicitly shown instead of silently trusting corrupted §4 text.

    Inputs:
        doc: Parsed dossier dictionary.
        sector_info: Resolved sector metadata from ``data/sector_map.json``.
        aliases: Loaded ``data/aliases.json`` dictionary.

    Outputs:
        Dictionary containing ``expected_field``, ``expected_canonical``,
        ``section4_named_field``, ``section4_conflict``, and ``conflict_reason``.

    Failure behaviour:
        Never raises on missing sections or rows; returns ``None`` fields safely.
    """
    slot = sector_info["licensing_slot"]
    row_key = sector_info["dossier_row_key"]
    s4_steps: list[Field] = doc.get("sector_steps", {}).get(row_key, [])
    s4_first: Optional[Field] = s4_steps[0] if s4_steps else None

    expected_field: Optional[Field] = None
    expected_canonical: Optional[str] = None
    conflict = False
    conflict_reason: Optional[str] = None

    if slot == "central_bank":
        expected_field = doc.get("central_bank")
        expected_canonical = normalise_central_bank(
            expected_field.value if expected_field else None, aliases
        )
        # Check whether Section 4 names a different body (specifically the DPA or a
        # placeholder) in the payments/lending licensing slot instead of the central bank.
        if s4_first is not None:
            dp_field = doc.get("data_protection")
            first_text = s4_first.value
            cb_raw = expected_field.value if expected_field else ""
            names_cb = bool(
                (cb_raw and cb_raw.lower() in first_text.lower())
                or (expected_canonical and expected_canonical.lower() in first_text.lower())
            )
            names_dpa = bool(dp_field and dp_field.value and dp_field.value in first_text)
            if names_dpa and not names_cb:
                conflict = True
                conflict_reason = (
                    "Section 4 names the data protection authority in the payments/lending "
                    "licensing slot instead of the central bank."
                )
            elif not names_cb:
                conflict = True
                conflict_reason = (
                    "Section 4 first step does not match the central bank mapped in sector_map.json."
                )

    elif slot == "energy_regulator":
        expected_field = doc.get("energy_regulator")
        expected_canonical = expected_field.value if expected_field else None
        if s4_first is not None:
            cit_field = doc.get("cit")
            first_text = s4_first.value
            # Detect a CIT rate leaked into the "Energy regulator: <rate>" slot.
            if (cit_field and cit_field.value and cit_field.value in first_text) or PERCENT_RE.search(
                first_text
            ):
                conflict = True
                conflict_reason = (
                    "Section 4 places a tax percentage inside the Energy regulator slot "
                    "instead of the Section 3 energy authority."
                )
            elif expected_canonical and expected_canonical.lower() not in first_text.lower():
                conflict = True
                conflict_reason = (
                    "Section 4 energy regulator step does not match the Section 3 authority."
                )

    else:
        # Sectors whose primary licensing contact originates directly in Section 4.
        expected_field = s4_first
        expected_canonical = s4_first.value if s4_first else None

    return {
        "expected_field": _field_dict(expected_field),
        "expected_canonical": expected_canonical,
        "section4_named_field": _field_dict(s4_first),
        "section4_conflict": conflict,
        "conflict_reason": conflict_reason,
    }


def compare_regulators(
    home_doc: dict[str, Any],
    target_doc: dict[str, Any],
    sector_info: dict[str, Any],
    aliases: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Compare currency, central bank, data protection authority, and sector regulator.

    Purpose:
        Produce a side-by-side home vs target comparison of regulatory bodies with
        alias normalisation, DPA acronym/expansion matching, and C5 sector-regulator
        conflict detection.

    Inputs:
        home_doc: Parsed home country dossier dict.
        target_doc: Parsed target country dossier dict.
        sector_info: Resolved sector metadata dict from ``resolve_sector``.
        aliases: Optional loaded ``data/aliases.json`` dictionary.

    Outputs:
        Dictionary containing ``currency``, ``central_bank``, ``data_protection``,
        and ``sector_regulator`` comparison blocks.

    Failure behaviour:
        Never raises; handles missing regulator fields cleanly with ``None`` values.
    """
    alias_data = aliases if aliases is not None else load_json_data("aliases.json")
    cb_display = alias_data.get("central_bank_display", {})

    # Currency comparison
    h_cc = home_doc.get("currency_code")
    t_cc = target_doc.get("currency_code")
    currency_cmp = {
        "home_code": h_cc.value if h_cc else None,
        "target_code": t_cc.value if t_cc else None,
        "home_field": _field_dict(home_doc.get("currency")),
        "target_field": _field_dict(target_doc.get("currency")),
        "same": bool(h_cc and t_cc and h_cc.value == t_cc.value),
    }

    # Central bank comparison (normalised via aliases.json)
    h_cb = home_doc.get("central_bank")
    t_cb = target_doc.get("central_bank")
    h_cb_canon = normalise_central_bank(h_cb.value if h_cb else None, alias_data)
    t_cb_canon = normalise_central_bank(t_cb.value if t_cb else None, alias_data)
    cb_same = bool(h_cb_canon and t_cb_canon and h_cb_canon == t_cb_canon)
    central_bank_cmp = {
        "home_field": _field_dict(h_cb),
        "target_field": _field_dict(t_cb),
        "home_canonical": h_cb_canon,
        "target_canonical": t_cb_canon,
        "home_display": cb_display.get(h_cb_canon, h_cb_canon) if h_cb_canon else None,
        "target_display": cb_display.get(t_cb_canon, t_cb_canon) if t_cb_canon else None,
        "same": cb_same,
        "raw_differs": bool(h_cb and t_cb and h_cb.value != t_cb.value),
    }

    # Data protection authority comparison (detect same acronym with different expansions)
    h_dp = home_doc.get("data_protection")
    t_dp = target_doc.get("data_protection")
    h_pair = extract_acronym_and_expansion(h_dp.value) if (h_dp and h_dp.value) else None
    t_pair = extract_acronym_and_expansion(t_dp.value) if (t_dp and t_dp.value) else None
    h_acr, h_exp = h_pair if h_pair else (None, None)
    t_acr, t_exp = t_pair if t_pair else (None, None)

    same_acronym_diff_exp = bool(
        h_acr and t_acr and h_acr.upper() == t_acr.upper() and h_exp != t_exp
    )
    dpa_same = bool(
        h_dp and t_dp and h_dp.value.strip().lower() == t_dp.value.strip().lower()
    )
    data_protection_cmp = {
        "home_field": _field_dict(h_dp),
        "target_field": _field_dict(t_dp),
        "home_acronym": h_acr,
        "target_acronym": t_acr,
        "home_expansion": h_exp,
        "target_expansion": t_exp,
        "same": dpa_same,
        "same_acronym_different_expansion": same_acronym_diff_exp,
    }

    # Sector regulator comparison via sector_map.json (C5)
    h_sec = _extract_sector_regulator_side(home_doc, sector_info, alias_data)
    t_sec = _extract_sector_regulator_side(target_doc, sector_info, alias_data)
    sec_same = bool(
        h_sec["expected_canonical"]
        and t_sec["expected_canonical"]
        and h_sec["expected_canonical"] == t_sec["expected_canonical"]
    )
    sector_reg_cmp = {
        "sector_key": sector_info["key"],
        "licensing_section": sector_info["licensing_section"],
        "licensing_slot": sector_info["licensing_slot"],
        "role_en": sector_info["role_en"],
        "role_fr": sector_info["role_fr"],
        "home": h_sec,
        "target": t_sec,
        "same": sec_same,
        "any_section4_conflict": bool(h_sec["section4_conflict"] or t_sec["section4_conflict"]),
    }

    return {
        "currency": currency_cmp,
        "central_bank": central_bank_cmp,
        "data_protection": data_protection_cmp,
        "sector_regulator": sector_reg_cmp,
    }


def _annotate_sector_steps(doc: dict[str, Any], sector_key: str) -> list[dict[str, Any]]:
    """Annotate ordered Section 4 compliance steps with template-defect flags (C5).

    Purpose:
        Split the Section 4 row into an ordered list of steps and tag individual
        steps whose text suffers from a known template generation error (such as DPA
        as payments licensor, leaked VAT rate in a fee slot, or leaked CIT rate in an
        energy regulator slot) so the renderer never presents corrupted text as fact.

    Inputs:
        doc: Parsed dossier dictionary.
        sector_key: Canonical lowercase sector key.

    Outputs:
        List of step dictionaries with ``order``, ``text``, ``field``,
        ``template_flagged``, ``flag_reason``, and ``is_boilerplate``.

    Failure behaviour:
        Returns an empty list if the sector row is absent.
    """
    steps: list[Field] = doc.get("sector_steps", {}).get(sector_key, [])
    dp_val = doc["data_protection"].value if doc.get("data_protection") else ""
    vat_val = doc["vat"].value if doc.get("vat") else ""
    cit_val = doc["cit"].value if doc.get("cit") else ""

    annotated: list[dict[str, Any]] = []
    for idx, step in enumerate(steps, start=1):
        txt = step.value
        txt_lower = txt.lower()
        flagged = False
        reason: Optional[str] = None

        # Detect systemic template defects at the individual step level (C5).
        if (
            sector_key == "fintech"
            and "licensing for payments and lending" in txt_lower
            and dp_val
            and dp_val in txt
        ):
            flagged = True
            reason = "Template defect: names the data protection authority as payments/lending licensor instead of the central bank."
        elif (
            "data protection registration" in txt_lower
            and vat_val
            and f"({vat_val})" in txt
        ):
            flagged = True
            reason = "Template defect: leaks the Section 5 VAT rate into a data-protection registration fee slot."
        elif (
            sector_key == "energy & manufacturing"
            and "energy regulator:" in txt_lower
            and cit_val
            and cit_val in txt
        ):
            flagged = True
            reason = "Template defect: leaks the Section 5 corporate income tax rate into the energy regulator slot."

        annotated.append(
            {
                "order": idx,
                "text": txt,
                "field": _field_dict(step),
                "is_boilerplate": bool(step.is_boilerplate),
                "template_flagged": flagged,
                "flag_reason": reason,
            }
        )
    return annotated


def compare_sector_steps(
    home_doc: dict[str, Any],
    target_doc: dict[str, Any],
    sector_info: dict[str, Any],
) -> dict[str, Any]:
    """Build ordered Section 4 'First steps' lists for home and target.

    Purpose:
        Supply Section 2 of the brief with provenance-tagged, template-checked first
        steps split from the Section 4 sector row.

    Inputs:
        home_doc: Parsed home country dossier dict.
        target_doc: Parsed target country dossier dict.
        sector_info: Resolved sector metadata dict.

    Outputs:
        Dictionary with ``home_row``, ``target_row``, ``home_steps``, ``target_steps``,
        and ``has_template_flagged_steps``.

    Failure behaviour:
        Never raises; returns empty step lists if the sector row is missing.
    """
    row_key = sector_info["dossier_row_key"]
    h_steps = _annotate_sector_steps(home_doc, row_key)
    t_steps = _annotate_sector_steps(target_doc, row_key)
    has_flagged = any(s["template_flagged"] for s in h_steps + t_steps)
    return {
        "sector_key": row_key,
        "home_row": _field_dict(home_doc.get("sectors", {}).get(row_key)),
        "target_row": _field_dict(target_doc.get("sectors", {}).get(row_key)),
        "home_steps": h_steps,
        "target_steps": t_steps,
        "has_template_flagged_steps": has_flagged,
    }


def _compare_single_tax(
    home_field: Optional[Field],
    target_field: Optional[Field],
) -> dict[str, Any]:
    """Compare one tax item (CIT or VAT) without ever subtracting from compound cells.

    Purpose:
        Extract the headline (first) number and all numbers on each side, mark any
        compound or non-numeric cell as ``uncomparable-as-is``, and compute
        ``delta_pp = target - home`` ONLY when both sides are single clean numbers.

    Inputs:
        home_field: Section 5 tax ``Field`` for the home country.
        target_field: Section 5 tax ``Field`` for the target country.

    Outputs:
        Tax comparison dictionary with provenance, headline values, all extracted
        numbers, comparability status, and optional percentage-point delta.

    Failure behaviour:
        Never raises on missing, compound, or non-numeric cells.
    """
    h_nums: list[float] = list(home_field.meta.get("numbers", [])) if home_field else []
    t_nums: list[float] = list(target_field.meta.get("numbers", [])) if target_field else []

    h_compound = bool(home_field.meta.get("is_compound", False)) if home_field else False
    t_compound = bool(target_field.meta.get("is_compound", False)) if target_field else False
    h_non_numeric = (home_field is None) or (len(h_nums) == 0)
    t_non_numeric = (target_field is None) or (len(t_nums) == 0)

    h_headline = h_nums[0] if h_nums else None
    t_headline = t_nums[0] if t_nums else None

    # Compute delta strictly when BOTH sides are single clean numeric percentages.
    comparable = (
        not h_compound
        and not t_compound
        and not h_non_numeric
        and not t_non_numeric
        and len(h_nums) == 1
        and len(t_nums) == 1
    )
    delta_pp: Optional[float] = round(t_nums[0] - h_nums[0], 4) if comparable else None
    same_headline = bool(
        h_headline is not None and t_headline is not None and h_headline == t_headline
    )

    return {
        "home_field": _field_dict(home_field),
        "target_field": _field_dict(target_field),
        "home_headline": h_headline,
        "target_headline": t_headline,
        "same_headline": same_headline,
        "home_all_numbers": h_nums,
        "target_all_numbers": t_nums,
        "home_compound": h_compound,
        "target_compound": t_compound,
        "home_non_numeric": h_non_numeric,
        "target_non_numeric": t_non_numeric,
        "comparable": comparable,
        "status": "comparable" if comparable else "uncomparable-as-is",
        "delta_pp": delta_pp,
    }


def compare_taxes(
    home_doc: dict[str, Any],
    target_doc: dict[str, Any],
) -> dict[str, Any]:
    """Compare corporate income tax (CIT) and VAT between home and target.

    Purpose:
        Provide Section 3 tax comparisons with provenance, compound-cell protection,
        and exact percentage-point deltas where valid.

    Inputs:
        home_doc: Parsed home country dossier dict.
        target_doc: Parsed target country dossier dict.

    Outputs:
        Dictionary with ``cit`` and ``vat`` comparison records.

    Failure behaviour:
        Never raises; delegates safely to ``_compare_single_tax``.
    """
    return {
        "cit": _compare_single_tax(home_doc.get("cit"), target_doc.get("cit")),
        "vat": _compare_single_tax(home_doc.get("vat"), target_doc.get("vat")),
    }


def _normalise_lang_token(raw: str) -> str:
    """Extract a clean comparison key for a single language entry.

    Purpose:
        Compare official and spoken languages reliably even when an entry includes a
        qualifier such as ``French (de facto)`` or ``French (business/administration)``.

    Inputs:
        raw: Single language string split at parenthesis depth 0.

    Outputs:
        Lowercased base language string.

    Failure behaviour:
        Never raises.
    """
    base = re.sub(r"\([^)]*\)", "", raw).strip().lower()
    return base or raw.strip().lower()


def _is_prose_language_cell(fields: list[Field]) -> bool:
    """Detect whether a language list contains a prose summary rather than plain items.

    Purpose:
        Identify cells like ``"11 official languages (...)"`` or
        ``"No official language"`` so downstream renderers and validators present
        them transparently without misreading them as a single language name.

    Inputs:
        fields: List of ``Field`` objects for official or dominant languages.

    Outputs:
        ``True`` if any entry appears to be a prose clause rather than a bare language.

    Failure behaviour:
        Never raises.
    """
    prose_markers = ("official language", "working language", "state language", "and others", "in business")
    for f in fields:
        low = f.value.lower()
        if any(m in low for m in prose_markers):
            return True
    return False


def compare_languages(
    home_doc: dict[str, Any],
    target_doc: dict[str, Any],
) -> dict[str, Any]:
    """Compare official and dominant spoken/business languages between home and target.

    Purpose:
        Show which official languages are shared, which drop out on arrival in the
        target country, and which new ones appear, while preserving provenance and
        treating real linguistic differences as neutral information (C1).

    Inputs:
        home_doc: Parsed home country dossier dict.
        target_doc: Parsed target country dossier dict.

    Outputs:
        Dictionary with ``home_official``, ``target_official``, ``home_dominant``,
        ``target_dominant``, ``shared_official``, ``dropped_official``,
        ``added_official``, ``official_differs``, ``dominant_differs``, and
        ``has_prose_cell``.

    Failure behaviour:
        Never raises on empty or prose-formatted language lists.
    """
    h_off: list[Field] = home_doc.get("official_languages", [])
    t_off: list[Field] = target_doc.get("official_languages", [])
    h_dom: list[Field] = home_doc.get("dominant_languages", [])
    t_dom: list[Field] = target_doc.get("dominant_languages", [])

    h_off_map = {_normalise_lang_token(f.value): f.value for f in h_off}
    t_off_map = {_normalise_lang_token(f.value): f.value for f in t_off}

    shared_official = [h_off_map[k] for k in h_off_map if k in t_off_map]
    dropped_official = [h_off_map[k] for k in h_off_map if k not in t_off_map]
    added_official = [t_off_map[k] for k in t_off_map if k not in h_off_map]

    h_dom_keys = {_normalise_lang_token(f.value) for f in h_dom}
    t_dom_keys = {_normalise_lang_token(f.value) for f in t_dom}

    return {
        "home_official": [_field_dict(f) for f in h_off],
        "target_official": [_field_dict(f) for f in t_off],
        "home_dominant": [_field_dict(f) for f in h_dom],
        "target_dominant": [_field_dict(f) for f in t_dom],
        "shared_official": shared_official,
        "dropped_official": dropped_official,
        "added_official": added_official,
        "official_differs": set(h_off_map.keys()) != set(t_off_map.keys()),
        "dominant_differs": h_dom_keys != t_dom_keys,
        "has_prose_cell": _is_prose_language_cell(h_off + t_off + h_dom + t_dom),
    }
