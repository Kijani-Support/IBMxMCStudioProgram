"""Passerelle (EN: "Gateway") — Bilingual Markdown Brief Renderer (EN / FR).

Tagline: "Franchir la frontière, vérifier d'abord" / "Cross the border, verify first."
Team: Christopher Damian Munene, Mark Lekayia. Group 1, IBM x MC Studio Dev Day.

Purpose:
    Transform ``facts.json`` into a structured, sourced, plain-language Markdown launch
    brief in English or natural French, strictly separating dossier facts, corpus-wide
    template defects, and unverified external checks.

Inputs:
    ``facts`` dictionary produced by ``facts.py``, target language (``"en"`` or
    ``"fr"``), and ``data/i18n_fr.json`` for French text.

Outputs:
    Rendered Markdown brief string containing the disclaimer, template-defect banner,
    Section 0 (At-a-glance), Sections 1–6 (each ending with a plain-language
    "What this means for you" / "Ce que cela signifie pour vous" takeaway), and
    "Our checks (unverified)".

Failure behaviour:
    Raises ``ValueError`` for unsupported language codes; missing dossier fields render
    explicitly as not reported without crashing.
"""

from __future__ import annotations

from typing import Any, Optional

from blocs import load_json_data


def _fmt_num(val: Optional[float]) -> str:
    """Format a float cleanly without unnecessary trailing zeros.

    Purpose:
        Keep numeric formatting identical between EN and FR briefs (e.g. ``30`` not
        ``30.0``, ``19.25`` preserved, ``-1.25`` preserved) so parity checks pass.

    Inputs:
        val: Float value or ``None``.

    Outputs:
        Formatted string, or ``"N/A"`` when ``val`` is ``None``.

    Failure behaviour:
        Never raises.
    """
    if val is None:
        return "N/A"
    if float(val).is_integer():
        return str(int(val))
    return f"{val:g}"


def _cite(field_dict: Optional[dict[str, Any]]) -> str:
    """Return the inline provenance citation for a serialized Field dict.

    Purpose:
        Guarantee every rendered dossier figure and authority carries its exact
        ``(source: <file> §<section>, line <n>)`` tag on the same line (R2 / A2).

    Inputs:
        field_dict: Serialized ``Field`` dictionary (or ``None``).

    Outputs:
        Citation string, or empty string if ``field_dict`` is ``None``.

    Failure behaviour:
        Never raises.
    """
    if not field_dict:
        return ""
    if "citation" in field_dict and field_dict["citation"]:
        return str(field_dict["citation"])
    return f"(source: {field_dict['file']} §{field_dict['section']}, line {field_dict['line']})"


def _cite_pair(f1: Optional[dict[str, Any]], f2: Optional[dict[str, Any]]) -> str:
    """Combine two Field citations into one inline ``(source: ...; ...)`` tag.

    Purpose:
        Attach dual provenance on comparison rows (such as percentage-point deltas or
        shared regional blocs) without duplicating boilerplate.

    Inputs:
        f1: Home serialized ``Field`` dict (or ``None``).
        f2: Target serialized ``Field`` dict (or ``None``).

    Outputs:
        Combined citation string.

    Failure behaviour:
        Never raises.
    """
    parts: list[str] = []
    for fd in (f1, f2):
        if fd:
            parts.append(f"{fd['file']} §{fd['section']}, line {fd['line']}")
    if not parts:
        return ""
    return f"(source: {'; '.join(parts)})"


def _field_val(field_dict: Optional[dict[str, Any]], fallback: str) -> str:
    """Return a serialized Field's value text or a localized fallback.

    Purpose:
        Avoid ``None`` leaks when rendering dossiers with missing fields (R4).

    Inputs:
        field_dict: Serialized ``Field`` dict or ``None``.
        fallback: Localized fallback label (e.g. ``"Not reported in dossier"``).

    Outputs:
        Display string.

    Failure behaviour:
        Never raises.
    """
    if field_dict and field_dict.get("value"):
        return str(field_dict["value"])
    return fallback


def _en_strings() -> dict[str, Any]:
    """Return the English string bundle mirroring ``data/i18n_fr.json``.

    Purpose:
        Keep EN and FR rendering driven by the exact same key layout so both
        languages always produce identical section counts and figure placement (A8).

    Inputs:
        None.

    Outputs:
        Nested dictionary of English headings, labels, and plain-language takeaways
        satisfying the non-lawyer rule (R8).

    Failure behaviour:
        Never raises.
    """
    return {
        "title": "Passerelle — Cross-Border Launch Brief",
        "tagline": "Cross the border, verify first.",
        "disclaimer": (
            "Planning reference only — not legal, tax, or financial advice. "
            "Verify every figure and authority with the relevant regulator before acting."
        ),
        "template_banner_title": "Systemic Dossier Template Defects (Excluded from Route Score)",
        "template_banner_intro": (
            "These defects affect most of the 54 source dossiers (template generation errors) "
            "and are separated from your route's country/bloc confidence score:"
        ),
        "template_banner_item": "[{v_number}] {count} of {total} dossiers share this defect: {summary}",
        "sec0_title": "0. At-a-glance",
        "sec1_title": "1. Regulators to engage",
        "sec2_title": "2. Sector compliance steps (First steps)",
        "sec3_title": "3. Tax differences (CIT and VAT)",
        "sec4_title": "4. Language",
        "sec5_title": "5. Shared regional blocs",
        "sec6_title": "6. Verify first",
        "our_checks_title": "Our checks (unverified)",
        "our_checks_intro": (
            "Items below draw on checks outside the source dossiers and are never presented "
            "as dossier facts. Status remains unverified until an official source URL is attached."
        ),
        "what_this_means": "What this means for you",
        "labels": {
            "route": "Route",
            "sector": "Sector",
            "home": "Home",
            "target": "Target",
            "shared_blocs": "Shared blocs",
            "none": "None",
            "flags_by_severity": "Verify-first flags (country & bloc)",
            "data_confidence": "Data Confidence",
            "confidence_note": (
                "Measures source-dossier data quality for this route (country & bloc flags only), "
                "never legal risk."
            ),
            "high": "High",
            "medium": "Medium",
            "low": "Low",
            "sev_high": "High",
            "sev_med": "Medium",
            "sev_low": "Low",
            "central_bank": "Central bank",
            "currency": "Currency",
            "template_banner_short": "template banner",
            "data_protection": "Data protection authority",
            "sector_regulator": "Sector regulator (licensing contact)",
            "section4_conflict": "Body named in Section 4 (conflict flagged)",
            "normalized": "normalised",
            "same": "Same",
            "differs": "Differs",
            "uncomparable": "Uncomparable as-is",
            "same_headline_rate": "Same headline rate ({rate}%)",
            "variant_rates_caveat": "Caveat: variant rates present ({variants}); no numeric delta claimed for compound cells beyond the headline",
            "cit": "Corporate income tax (CIT)",
            "vat": "VAT / sales tax",
            "delta": "Delta (target − home)",
            "points": "percentage points",
            "all_numbers": "All rates found",
            "official_languages": "Official languages",
            "dominant_languages": "Dominant spoken / business languages",
            "dropped_languages": "Official languages in home that drop out in target",
            "added_languages": "New official languages in target",
            "shared_languages": "Shared official languages",
            "only_in_home": "Only in home",
            "only_in_target": "Only in target",
            "qualifier": "qualifier",
            "status": "Status",
            "unverified": "unverified",
            "source_url": "Source URL",
            "no_source_url": "none recorded yet",
            "evidence": "Evidence",
            "why_it_matters": "Why it matters",
            "suggested_check": "Who to ask",
            "scope": "Scope",
            "confidence": "Source type",
            "no_flags": "No country-scope or bloc-scope Verify-first flags for this route.",
            "template_flagged_warning": (
                "Warning: the Section 4 row for this sector contains a known template defect "
                "(flagged below). Affected steps are marked untrusted and must not be treated as fact."
            ),
            "step_untrusted_tag": "[FLAGGED — template defect, do not treat as fact]",
            "not_reported": "Not reported in dossier",
            "dpa_same_acronym_diff_exp": "Same acronym ({acronym}) with different full names across the two dossiers",
            "bloc_matrix_title": "Bloc consistency matrix ({bloc})",
            "matrix_country": "Country",
            "matrix_currency": "Currency",
            "matrix_cb": "Central bank",
            "matrix_blocs": "Bloc symmetry",
            "matrix_dpa": "DPA naming",
            "matrix_placeholders": "Placeholders",
            "matrix_flags": "Flag counts",
        },
        "meanings": {
            "sec1_same_cb": (
                "You stay under the same central bank (the public authority that manages money "
                "and approves financial services), so your main financial regulator does not change, "
                "but you still need to confirm the privacy office (the agency overseeing customer personal data) in the target country."
            ),
            "sec1_diff_cb": (
                "You are moving to a different central bank (the public authority that manages "
                "money and approves financial services), so plan for a fresh local licensing process in the target country."
            ),
            "sec2_flagged": (
                "Parts of this checklist mix up the wrong agency or insert a sales-tax rate where "
                "a registration fee belongs, so treat it only as a starting prompt and confirm every step with the real licensing office."
            ),
            "sec2_clean": (
                "Work through these steps in order as an early planning checklist and confirm "
                "current fees directly with each local office before spending money."
            ),
            "sec3_delta": (
                "Use the tax difference above to adjust your pricing and cash plan (corporate "
                "income tax is the share of yearly profit paid to the state, and VAT is the tax added to customer sales), then confirm rates with the local tax office."
            ),
            "sec3_uncomparable": (
                "At least one tax rate has multiple brackets or no single number in the dossier, "
                "so do not lock in a financial model until the local tax office confirms which rate applies to your business."
            ),
            "sec4_diff": (
                "Official languages change when you cross this border, so budget time and money "
                "to translate your contracts, customer screens, and government filings into the target country's official language."
            ),
            "sec4_same": (
                "Both countries use the same official languages, so you can reuse most of your "
                "contracts, onboarding screens, and official filings without full translation."
            ),
            "sec5_shared": (
                "Sharing a regional bloc (an agreement among neighbouring countries on shared "
                "currency or trade rules) can simplify money transfers and customs, but you still need local registration in the target country."
            ),
            "sec5_none": (
                "Because these countries do not share a sub-regional economic bloc (a group of "
                "neighbours with shared currency or trade rules), plan to handle licences, currency transfers, and trade paperwork country by country."
            ),
            "sec6_has_flags": (
                "Resolve every High flag before paying legal fees or filing applications, because "
                "each flag marks a contradiction or missing name inside the source dossiers."
            ),
            "sec6_clean": (
                "No country-specific or bloc-specific contradictions were found in these two "
                "dossiers, though you should still confirm current rules directly with local authorities."
            ),
        },
    }


def _confidence_label(raw_label: str, labels: dict[str, str]) -> str:
    """Translate the deterministic Data Confidence label into the output language.

    Purpose:
        Render ``High`` / ``Medium`` / ``Low`` naturally in EN or FR without altering
        the underlying deterministic threshold logic.

    Inputs:
        raw_label: ``"High"``, ``"Medium"``, or ``"Low"``.
        labels: Localized label dictionary.

    Outputs:
        Localized confidence label string.

    Failure behaviour:
        Falls back to ``raw_label`` if unrecognized.
    """
    return labels.get(raw_label.lower(), raw_label)


def _format_tax_block(
    tax_label: str,
    tcmp: dict[str, Any],
    home_name: str,
    target_name: str,
    labels: dict[str, str],
) -> list[str]:
    """Render Markdown bullet lines for one tax item (CIT or VAT).

    Purpose:
        Show home and target rates with exact provenance, list every extracted number
        on compound cells, mark compound/non-numeric cells as ``uncomparable-as-is``,
        and report a percentage-point delta strictly when both sides are single numbers.

    Inputs:
        tax_label: Localized tax name (e.g. ``"Corporate income tax (CIT)"``).
        tcmp: Tax comparison dictionary from ``compare.py``.
        home_name: Home country display name.
        target_name: Target country display name.
        labels: Localized labels dictionary.

    Outputs:
        List of Markdown lines.

    Failure behaviour:
        Never raises on missing or non-numeric fields.
    """
    lines: list[str] = []
    hf = tcmp["home_field"]
    tf = tcmp["target_field"]
    h_raw = _field_val(hf, labels["not_reported"])
    t_raw = _field_val(tf, labels["not_reported"])

    lines.append(f"- **{tax_label}:**")
    lines.append(f"  - {home_name}: `{h_raw}` {_cite(hf)}")
    lines.append(f"  - {target_name}: `{t_raw}` {_cite(tf)}")

    if tcmp["comparable"]:
        delta = tcmp["delta_pp"]
        sign = "+" if (delta is not None and delta > 0) else ""
        delta_str = f"{sign}{_fmt_num(delta)} {labels['points']}"
        lines.append(
            f"  - **{labels['delta']}:** `{delta_str}` {_cite_pair(hf, tf)}"
        )
    else:
        h_nums_str = ", ".join(f"{_fmt_num(n)}%" for n in tcmp["home_all_numbers"]) or labels["none"]
        t_nums_str = ", ".join(f"{_fmt_num(n)}%" for n in tcmp["target_all_numbers"]) or labels["none"]
        if tcmp.get("same_headline") and tcmp.get("home_headline") is not None:
            # F3: Equal headline rates with compound/variant rates get an explicit
            # same-headline callout plus a variant caveat, never a fake numeric delta.
            variant_parts = []
            if tcmp["home_compound"]:
                variant_parts.append(f"{home_name}: {h_nums_str}")
            if tcmp["target_compound"]:
                variant_parts.append(f"{target_name}: {t_nums_str}")
            variants_str = "; ".join(variant_parts) or f"{home_name}: {h_nums_str}; {target_name}: {t_nums_str}"
            headline_str = labels["same_headline_rate"].format(rate=_fmt_num(tcmp["home_headline"]))
            caveat_str = labels["variant_rates_caveat"].format(variants=variants_str)
            lines.append(
                f"  - **{labels['delta']}:** `{headline_str}` — {caveat_str} {_cite_pair(hf, tf)}"
            )
        else:
            lines.append(
                f"  - **{labels['delta']}:** `{labels['uncomparable']}` — "
                f"{labels['all_numbers']}: {home_name} [{h_nums_str}] {_cite(hf)}; "
                f"{target_name} [{t_nums_str}] {_cite(tf)}"
            )
    return lines


def render_brief(facts: dict[str, Any], lang: str = "en") -> str:
    """Render a complete Passerelle Markdown launch brief from ``facts.json``.

    Purpose:
        Produce a sourced, plain-language English or French launch brief adhering to
        all hard rules (R2 provenance on every figure, R8 non-lawyer takeaways, R9
        strict dossier vs our-check separation, C2 template banner + route confidence,
        C3 external checks section, C5 §4 conflict transparency).

    Inputs:
        facts: Dictionary produced by ``facts.build_facts``.
        lang: Output language code, ``"en"`` or ``"fr"``.

    Outputs:
        Markdown brief text as a string.

    Failure behaviour:
        Raises ``ValueError`` if ``lang`` is neither ``"en"`` nor ``"fr"``.
    """
    lang_code = lang.strip().lower()
    if lang_code not in ("en", "fr"):
        raise ValueError(f"Unsupported language '{lang}'. Use 'en' or 'fr'.")

    s = _en_strings() if lang_code == "en" else load_json_data("i18n_fr.json")
    labels = s["labels"]
    meanings = s["meanings"]

    meta = facts["meta"]
    comps = facts["comparisons"]
    regs = comps["regulators"]
    steps = comps["sector_steps"]
    taxes = comps["taxes"]
    langs = comps["languages"]
    blocs_cmp = facts["blocs"]
    scores = facts["scores"]
    flags = facts["flags"]
    template_banner = facts["template_banner"]
    our_checks = facts["our_checks"]

    home_name = meta["home_country"]
    target_name = meta["target_country"]
    sector_display = meta["sector_display_en"] if lang_code == "en" else meta["sector_display_fr"]

    out: list[str] = []

    # --- Header & mandatory disclaimer ---
    out.append(f"# {s['title']}: {home_name} -> {target_name}")
    out.append("")
    out.append(f"*{s['tagline']}* — {meta['team']}")
    out.append("")
    out.append(f"> **Disclaimer / Avertissement:** {s['disclaimer']}")
    out.append("")

    # --- Template-defect banner (C2: separate from country/bloc Data Confidence) ---
    if template_banner:
        out.append(f"> **{s['template_banner_title']}**")
        out.append(f"> {s['template_banner_intro']}")
        for item in template_banner:
            v_num = item.get("v_number") or item["rule_id"]
            matching_flag = next(
                (f for f in flags if f["rule_id"] == item["rule_id"] and f.get("evidence")),
                None,
            )
            summary_txt = item["message"]
            if lang_code == "fr":
                fr_tpl = s.get("flags_fr", {}).get(v_num)
                if fr_tpl and matching_flag:
                    params = dict(matching_flag.get("params", {}))
                    params.setdefault("affected_count", item["affected_count"])
                    params.setdefault("corpus_total", item["corpus_total"])
                    summary_txt = fr_tpl["message"].format(**params)
            line_txt = s["template_banner_item"].format(
                v_number=v_num,
                count=item["affected_count"],
                total=item["corpus_total"],
                summary=summary_txt,
            )
            # Attach matching route evidence citation on the same line so A2 holds everywhere.
            cite_str = ""
            if matching_flag and matching_flag["evidence"]:
                ev = matching_flag["evidence"]
                cite_str = " " + _cite_pair(ev[0], ev[1] if len(ev) > 1 else None)
            out.append(f"> - {line_txt}{cite_str}")
        out.append("")

    # --- Section 0: At-a-glance ---
    out.append(f"## {s['sec0_title']}")
    out.append("")
    shared_display = (
        ", ".join(
            f"{b['canonical']} {_cite_pair(b['home_entry']['field'], b['target_entry']['field'])}"
            for b in blocs_cmp["shared"]
        )
        if blocs_cmp["shared"]
        else labels["none"]
    )
    cnts = scores["counts"]
    conf_lbl = _confidence_label(scores["label"], labels)
    # F1: Route line cites the dossier title line (line 1) with no section number.
    home_title_line = meta.get("home_title_line", 1)
    target_title_line = meta.get("target_title_line", 1)
    home_meta_cite = f"(source: {meta['home_file']}, line {home_title_line})"
    target_meta_cite = f"(source: {meta['target_file']}, line {target_title_line})"

    out.append(f"- **{labels['route']}:** {home_name} ({labels['home']}) -> {target_name} ({labels['target']}) {home_meta_cite}; {target_meta_cite}")
    out.append(f"- **{labels['sector']}:** {sector_display}")
    out.append(f"- **{labels['shared_blocs']}:** {shared_display}")
    out.append(
        f"- **{labels['flags_by_severity']}:** "
        f"{cnts['high']} {labels['sev_high']}, {cnts['med']} {labels['sev_med']}, "
        f"{cnts['low']} {labels['sev_low']} ({cnts['total']} total; "
        f"{labels['template_banner_short']}: {scores['template_flag_count']})"
    )
    out.append(
        f"- **{labels['data_confidence']}:** **{conf_lbl}** "
        f"({cnts['high']} {labels['sev_high']}, {cnts['med']} {labels['sev_med']}, {cnts['low']} {labels['sev_low']}) — "
        f"{labels['confidence_note']}"
    )
    out.append("")

    # --- Section 1: Regulators to engage ---
    out.append(f"## {s['sec1_title']}")
    out.append("")
    cb = regs["central_bank"]
    dp = regs["data_protection"]
    cur = regs["currency"]
    sec_reg = regs["sector_regulator"]

    cb_status = labels["same"] if cb["same"] else labels["differs"]
    out.append(f"- **{labels['central_bank']}** (`{cb_status}`):")
    out.append(
        f"  - {home_name}: {_field_val(cb['home_field'], labels['not_reported'])} "
        f"[{labels['normalized']}: `{cb['home_canonical']}`] {_cite(cb['home_field'])}"
    )
    out.append(
        f"  - {target_name}: {_field_val(cb['target_field'], labels['not_reported'])} "
        f"[{labels['normalized']}: `{cb['target_canonical']}`] {_cite(cb['target_field'])}"
    )

    cur_status = labels["same"] if cur["same"] else labels["differs"]
    out.append(
        f"- **{labels['currency']}** (`{cur_status}`): "
        f"{home_name}: `{cur['home_code']}` {_cite(cur['home_field'])} | "
        f"{target_name}: `{cur['target_code']}` {_cite(cur['target_field'])}"
    )

    dp_status = labels["same"] if dp["same"] else labels["differs"]
    out.append(f"- **{labels['data_protection']}** (`{dp_status}`):")
    out.append(
        f"  - {home_name}: {_field_val(dp['home_field'], labels['not_reported'])} {_cite(dp['home_field'])}"
    )
    out.append(
        f"  - {target_name}: {_field_val(dp['target_field'], labels['not_reported'])} {_cite(dp['target_field'])}"
    )
    if dp["same_acronym_different_expansion"]:
        out.append(
            f"  - *{labels['dpa_same_acronym_diff_exp'].format(acronym=dp['home_acronym'])}* "
            f"{_cite_pair(dp['home_field'], dp['target_field'])}"
        )

    sec_role = sec_reg["role_en"] if lang_code == "en" else sec_reg["role_fr"]
    sec_status = labels["same"] if sec_reg["same"] else labels["differs"]
    out.append(f"- **{labels['sector_regulator']}** — {sec_role} (`{sec_status}`):")
    for side_name, side_data in ((home_name, sec_reg["home"]), (target_name, sec_reg["target"])):
        exp_f = side_data["expected_field"]
        out.append(
            f"  - {side_name}: {_field_val(exp_f, labels['not_reported'])} "
            f"[{labels['normalized']}: `{side_data['expected_canonical']}`] {_cite(exp_f)}"
        )
        if side_data["section4_conflict"] and side_data["section4_named_field"]:
            s4_f = side_data["section4_named_field"]
            out.append(
                f"    - **{labels['section4_conflict']}:** `{s4_f['value']}` "
                f"{labels['step_untrusted_tag']} {_cite(s4_f)}"
            )

    out.append("")
    cb_meaning = meanings["sec1_same_cb"] if cb["same"] else meanings["sec1_diff_cb"]
    out.append(f"**{s['what_this_means']}:** {cb_meaning}")
    out.append("")

    # --- Section 2: Sector compliance steps ---
    out.append(f"## {s['sec2_title']}")
    out.append("")
    if steps["has_template_flagged_steps"]:
        out.append(f"> {labels['template_flagged_warning']}")
        out.append("")

    for side_label, side_name, side_steps in (
        (labels["target"], target_name, steps["target_steps"]),
        (labels["home"], home_name, steps["home_steps"]),
    ):
        out.append(f"### {side_name} ({side_label})")
        if not side_steps:
            out.append(f"- {labels['not_reported']}")
        else:
            for st in side_steps:
                # Do not present template-corrupted step text as unqualified fact (C5).
                if st["template_flagged"]:
                    out.append(
                        f"{st['order']}. **{labels['step_untrusted_tag']}** *\"{st['text']}\"* {_cite(st['field'])}"
                    )
                else:
                    out.append(f"{st['order']}. {st['text']} {_cite(st['field'])}")
        out.append("")

    s2_meaning = meanings["sec2_flagged"] if steps["has_template_flagged_steps"] else meanings["sec2_clean"]
    out.append(f"**{s['what_this_means']}:** {s2_meaning}")
    out.append("")

    # --- Section 3: Tax differences ---
    out.append(f"## {s['sec3_title']}")
    out.append("")
    out.extend(_format_tax_block(labels["cit"], taxes["cit"], home_name, target_name, labels))
    out.extend(_format_tax_block(labels["vat"], taxes["vat"], home_name, target_name, labels))
    out.append("")
    tax_meaning = (
        meanings["sec3_delta"]
        if (taxes["cit"]["comparable"] and taxes["vat"]["comparable"])
        else meanings["sec3_uncomparable"]
    )
    out.append(f"**{s['what_this_means']}:** {tax_meaning}")
    out.append("")

    # --- Section 4: Language ---
    out.append(f"## {s['sec4_title']}")
    out.append("")
    h_off_str = ", ".join(f["value"] for f in langs["home_official"]) or labels["none"]
    t_off_str = ", ".join(f["value"] for f in langs["target_official"]) or labels["none"]
    h_dom_str = ", ".join(f["value"] for f in langs["home_dominant"]) or labels["none"]
    t_dom_str = ", ".join(f["value"] for f in langs["target_dominant"]) or labels["none"]

    h_off_cite = _cite(langs["home_official"][0]) if langs["home_official"] else ""
    t_off_cite = _cite(langs["target_official"][0]) if langs["target_official"] else ""
    h_dom_cite = _cite(langs["home_dominant"][0]) if langs["home_dominant"] else ""
    t_dom_cite = _cite(langs["target_dominant"][0]) if langs["target_dominant"] else ""

    off_status = labels["differs"] if langs["official_differs"] else labels["same"]
    out.append(f"- **{labels['official_languages']}** (`{off_status}`):")
    out.append(f"  - {home_name}: {h_off_str} {h_off_cite}")
    out.append(f"  - {target_name}: {t_off_str} {t_off_cite}")
    if langs["shared_official"]:
        out.append(
            f"  - {labels['shared_languages']}: {', '.join(langs['shared_official'])} "
            f"{_cite_pair(langs['home_official'][0] if langs['home_official'] else None, langs['target_official'][0] if langs['target_official'] else None)}"
        )
    if langs["dropped_official"]:
        out.append(
            f"  - {labels['dropped_languages']}: {', '.join(langs['dropped_official'])} {h_off_cite}"
        )
    if langs["added_official"]:
        out.append(
            f"  - {labels['added_languages']}: {', '.join(langs['added_official'])} {t_off_cite}"
        )

    dom_status = labels["differs"] if langs["dominant_differs"] else labels["same"]
    out.append(f"- **{labels['dominant_languages']}** (`{dom_status}`):")
    out.append(f"  - {home_name}: {h_dom_str} {h_dom_cite}")
    out.append(f"  - {target_name}: {t_dom_str} {t_dom_cite}")
    out.append("")
    lang_meaning = meanings["sec4_diff"] if langs["official_differs"] else meanings["sec4_same"]
    out.append(f"**{s['what_this_means']}:** {lang_meaning}")
    out.append("")

    # --- Section 5: Shared regional blocs ---
    out.append(f"## {s['sec5_title']}")
    out.append("")
    if blocs_cmp["shared"]:
        for b in blocs_cmp["shared"]:
            b_name = b["name_en"] if lang_code == "en" else b["name_fr"]
            b_meaning = b["meaning_en"] if lang_code == "en" else b["meaning_fr"]
            qual_notes = []
            if b["home_qualifier"]:
                qual_notes.append(f"{home_name}: {b['home_qualifier']}")
            if b["target_qualifier"]:
                qual_notes.append(f"{target_name}: {b['target_qualifier']}")
            qual_suffix = f" [{labels['qualifier']}: {', '.join(qual_notes)}]" if qual_notes else ""
            out.append(
                f"- **{b_name}**{qual_suffix}: {b_meaning} "
                f"{_cite_pair(b['home_entry']['field'], b['target_entry']['field'])}"
            )
    else:
        out.append(f"- {labels['none']}")

    if blocs_cmp["only_in_home"]:
        items = ", ".join(
            f"`{e['raw_value']}` {_cite(e['field'])}" for e in blocs_cmp["only_in_home"]
        )
        out.append(f"- **{labels['only_in_home']} ({home_name}):** {items}")
    if blocs_cmp["only_in_target"]:
        items = ", ".join(
            f"`{e['raw_value']}` {_cite(e['field'])}" for e in blocs_cmp["only_in_target"]
        )
        out.append(f"- **{labels['only_in_target']} ({target_name}):** {items}")

    # Render shared sub-regional bloc consistency matrix table(s) when present.
    bloc_matrices = facts.get("bloc_matrices", {})
    for bkey, matrix in bloc_matrices.items():
        if not matrix.get("rows"):
            continue
        out.append("")
        out.append(f"### {labels['bloc_matrix_title'].format(bloc=bkey)}")
        out.append("")
        out.append(
            f"| {labels['matrix_country']} | {labels['matrix_currency']} | {labels['matrix_cb']} | "
            f"{labels['matrix_blocs']} | {labels['matrix_dpa']} | {labels['matrix_placeholders']} | "
            f"{labels['matrix_flags']} | Source |"
        )
        out.append("|---|---|---|---|---|---|---|---|")
        for row in matrix["rows"]:
            cur_c = f"`{row['currency']['status']}` {row['currency']['label']}"
            cb_c = f"`{row['central_bank']['status']}` {row['central_bank']['label']}"
            sym_c = f"`{row['bloc_symmetry']['status']}` {row['bloc_symmetry']['label']}"
            dpa_c = f"`{row['dpa_naming']['status']}` {row['dpa_naming']['label']}"
            ph_c = f"`{row['placeholders']['status']}` {row['placeholders']['label']}"
            flg_c = f"`{row['flag_counts']['status']}` {row['flag_counts']['label']}"
            src_c = f"(source: {row['file']} §1, line 12)"
            out.append(
                f"| {row['country']} | {cur_c} | {cb_c} | {sym_c} | {dpa_c} | {ph_c} | {flg_c} | {src_c} |"
            )

    out.append("")
    has_subregional = any(b["canonical"] != "African Union" for b in blocs_cmp["shared"])
    bloc_meaning = meanings["sec5_shared"] if has_subregional else meanings["sec5_none"]
    out.append(f"**{s['what_this_means']}:** {bloc_meaning}")
    out.append("")

    # --- Section 6: Verify first (country & bloc flags grouped by severity) ---
    out.append(f"## {s['sec6_title']}")
    out.append("")
    route_flags = [f for f in flags if f.get("scope") in ("country", "bloc")]
    if not route_flags:
        out.append(f"- {labels['no_flags']}")
    else:
        for sev_key, sev_label in (
            ("high", labels["sev_high"]),
            ("med", labels["sev_med"]),
            ("low", labels["sev_low"]),
        ):
            bucket = [f for f in route_flags if f.get("severity") == sev_key]
            if not bucket:
                continue
            out.append(f"### {sev_label} ({len(bucket)})")
            for flg in bucket:
                ev_cites = "; ".join(
                    f"{e['file']} §{e['section']}, line {e['line']}" for e in flg.get("evidence", [])
                )
                cite_tag = f"(source: {ev_cites})" if ev_cites else ""
                v_num = flg.get("v_number") or flg["rule_id"]
                badge = f"{v_num} · {flg['rule_id']}" if flg.get("v_number") else flg["rule_id"]
                msg = flg["message"]
                why = flg["why_it_matters"]
                chk = flg["suggested_check"]
                if lang_code == "fr":
                    fr_tpl = s.get("flags_fr", {}).get(v_num)
                    if fr_tpl:
                        params = dict(flg.get("params", {}))
                        try:
                            msg = fr_tpl["message"].format(**params)
                            why = fr_tpl["why_it_matters"].format(**params)
                            chk = fr_tpl["suggested_check"].format(**params)
                        except KeyError:
                            pass
                out.append(
                    f"- **[{badge}]** ({labels['scope']}: `{flg['scope']}` | "
                    f"{labels['confidence']}: `{flg['confidence']}`): {msg} {cite_tag}"
                )
                out.append(f"  - *{labels['why_it_matters']}:* {why}")
                out.append(f"  - *{labels['suggested_check']}:* {chk}")
            out.append("")

    s6_meaning = meanings["sec6_has_flags"] if route_flags else meanings["sec6_clean"]
    out.append(f"**{s['what_this_means']}:** {s6_meaning}")
    out.append("")

    # --- Separate section: Our checks (unverified) per C3 & R9 ---
    out.append(f"## {s['our_checks_title']}")
    out.append("")
    out.append(s["our_checks_intro"])
    out.append("")
    if not our_checks:
        out.append(f"- {labels['none']}")
    else:
        for chk in our_checks:
            claim_txt = chk.get("claim_fr") if (lang_code == "fr" and chk.get("claim_fr")) else chk["claim"]
            src_url = chk.get("source_url") or labels["no_source_url"]
            out.append(
                f"- **[{chk['id']}]** ({labels['status']}: `{labels['unverified']}` | "
                f"{labels['source_url']}: {src_url}): {claim_txt}"
            )
    out.append("")

    return "\n".join(out)


def render_demo_md(facts: dict[str, Any]) -> str:
    """Generate ``DEMO.md`` directly from ``facts.json`` and its DEMO SHORTLIST.

    Purpose:
        Produce a repeatable 8-minute live demo script plus a 4-minute 6-flag
        walkthrough backed strictly by ``facts.json`` provenance and exact CLI
        commands (Step 4).

    Inputs:
        facts: Dictionary returned by ``facts.build_facts``.

    Outputs:
        Markdown string for ``DEMO.md``.

    Failure behaviour:
        Never raises on empty shortlists or missing optional fields.
    """
    m = facts["meta"]
    scores = facts["scores"]
    shortlist = facts.get("demo_shortlist", [])
    home_s = m["home_slug"]
    target_s = m["target_slug"]
    sector_s = m["sector_key"]
    matrices = facts.get("bloc_matrices", {})
    primary_bloc = next(iter(matrices.keys()), "regional bloc")

    lines = [
        f"# Passerelle — Live Demo Script ({m['home_country']} -> {m['target_country']} · {m['sector_display_en']})",
        "",
        f"> *{m['tagline_fr']} / {m['tagline_en']}* — {m['team']}",
        "",
        f"> **Disclaimer:** {m['disclaimer_en']}",
        "",
        "## 8-Minute Live Run Script",
        "",
        "### Minute 0–1 · Problem & Core Principles",
        "- Introduce **Passerelle**: early-stage founders expanding across borders need clear answers on regulators, taxes, and language *and* need to know which lines of a planning dossier cannot yet be trusted.",
        "- State our four principles: (1) code extracts, AI only explains; (2) every figure cites its dossier line; (3) doubt is shown, never hidden; (4) plain language first, legal vocabulary second.",
        "",
        "### Minute 1–3 · Generate the Sourced Brief (EN & FR) + Offline Dashboard",
        "Run from `Dev Day Challenge/Group 1/`:",
        "```bash",
        f"python cli.py --sector {sector_s} --home {home_s} --target {target_s} --lang en --out brief_en.md --facts-out facts.json --dashboard --shortlist",
        f"python cli.py --sector {sector_s} --home {home_s} --target {target_s} --lang fr --out brief_fr.md",
        "```",
        f"- Point to the **Template-defect banner** ({scores['template_flag_count']} systemic template flags separated from route Data Confidence) and the **Data Confidence** score: **{scores['label']}** ({scores['counts']['high']} High, {scores['counts']['med']} Medium, {scores['counts']['low']} Low — dossier quality only, never legal risk).",
        "- Show the **French brief** (`brief_fr.md`): identical section count and figures, natural French, original institution names preserved.",
        "",
        "### Minute 3–5 · Open the Offline Dashboard (`dashboard.html`)",
        "Open `dashboard.html` directly in any browser (zero server, zero internet, zero external requests):",
        "```bash",
        "start dashboard.html",
        "```",
        "- Toggle **EN / FR**, tick a step in the **First Steps Checklist**, click any **`source:` button** to open the **Evidence Drawer** showing the exact raw dossier line, and click **Export Brief (.md)**.",
        f"- Highlight the **{primary_bloc} Consistency Matrix** showing every member country side-by-side (`ok` / `note` / `flag`) to prove Passerelle validates across the entire bloc, not just two files.",
        "",
        "### Minute 5–7 · Prove Scale & Discipline (`validate.py` + `audit.py`)",
        "```bash",
        "python validate.py",
        "python audit.py",
        "```",
        "- Show `data/flags_all.json` covering all **54 dossiers**, and `audit.py` printing **PASS** on A1–A10 (zero country literals in code, 100% docstrings, 5 extra pairs + all 6 sectors, broken-file safety, zero secrets, offline dashboard).",
        "",
        "### Minute 7–8 · Swap Test, Non-Math Q&A & Close",
        "```bash",
        f"python cli.py --sector {sector_s} --home {target_s} --target {home_s} --lang en",
        "```",
        "- Point out the flipped VAT percentage-point delta and language diff, confirming nothing is hard-coded.",
        "- **Judge Q&A (How non-math sections like KYC & AML/CFT work):** Explain that while taxes are diffed numerically (never subtracting compound cells), non-math obligations—KYC (verifying customer identity before moving money), AML/CFT (ongoing monitoring, record-keeping, and reporting suspicious activity to the national Financial Intelligence Unit), licensing, privacy, and consumer protection—are checked structurally: Passerelle separates verbatim boilerplate from country-specific evidence, catches wrong-authority routing (`V01`), catches conflicting agency names (`V08`) and unnamed offices (`V20`), and turns every dossier gap into a concrete 'who to ask first' step instead of hallucinating legal thresholds.",
        "",
        "---",
        "",
        "## 4-Minute Flags Walkthrough (DEMO SHORTLIST)",
        "",
        "Walk through these 6 curated flags from `facts.json` in order — moving from corpus-wide template errors to route-specific dossier contradictions and finally unverified external checks:",
        "",
    ]

    for idx, item in enumerate(shortlist, start=1):
        lines.append(
            f"### {idx}. `[{item['rule']}]` — `{item['severity'].upper()}` · `{item['confidence']}`"
        )
        lines.append(f"- **Where:** `{item['location']}`")
        lines.append(f"- **What Passerelle caught:** {item['message']}")
        lines.append(f"- **Why it matters:** {item['why_it_matters']}")
        lines.append("")

    return "\n".join(lines)

