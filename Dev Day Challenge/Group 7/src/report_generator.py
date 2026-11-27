from datetime import date
from .extractors.fields import authorities, overview

DISCLAIMER = "This launch brief is a planning aid, not legal or tax advice. Dossiers are planning references; verify all claims with qualified local counsel and the relevant authorities before acting."


def source_label(source):
    if source is None:
        return "Not specified in dossier"
    return f"{source.file} · {' › '.join(source.heading_path)} · line {source.line}"


def brief_data(home, target, sector, comparison, tax_rows, flags):
    return {"home": home, "target": target, "sector": sector, "generated": date.today().isoformat(),
            "comparison": comparison, "tax": tax_rows, "flags": flags,
            "authorities": {home.country: authorities(home), target.country: authorities(target)},
            "overview": {home.country: overview(home), target.country: overview(target)}}


def to_markdown(data):
    out = [f"# Africa Launch Comparator: {data['home'].country} → {data['target'].country}",
           f"**Sector:** {data['sector']} · **Generated:** {data['generated']}", "", f"> {DISCLAIMER}", "", "## Executive summary", ""]
    comp = data["comparison"]
    out.append(f"Sector compliance comparison: **{comp['status']}** (similarity {comp['similarity']:.2f}; threshold 0.72; computed from {source_label(comp['home'].source)} and {source_label(comp['target'].source)}).") if comp["similarity"] is not None else out.append("Sector compliance comparison: **Missing or unclear**.")
    if comp["similarity"] is not None:
        out.append(f"- Home requirement: {comp['home'].value} — source: {source_label(comp['home'].source)}")
        out.append(f"- Target requirement: {comp['target'].value} — source: {source_label(comp['target'].source)}")
    from .comparison_engine import tax_delta
    for kind in ("corporate_income_tax", "vat"):
        pairs = data["tax"].get(kind, [])
        if len(pairs) == 2:
            delta = tax_delta(pairs[0][1], pairs[1][1])
            if delta:
                out.append(f"- {kind.replace('_',' ').upper()} delta (target minus home): **{delta['percentage_points']:+g} percentage points**, from {delta['home_input']:g}% — {source_label(delta['sources'][0])} and {delta['target_input']:g}% — {source_label(delta['sources'][1])}; see Tax for the cited input excerpts.")
    out.append(f"- Verify First flags for this pair: **{len(data['flags'])}**, counted from the [register rows](#verify-first-register) below.")
    out += ["", "## Regulatory authorities", ""]
    for country, fields in data["authorities"].items():
        out.append(f"### {country}")
        for key, findings in fields.items():
            out.append(f"- {key.replace('_',' ').title()}: " + ("; ".join(f"{f.value} — {source_label(f.source)}" for f in findings) if findings else "Not specified in dossier"))
            for f in findings:
                out.append(f"  - Source excerpt: `{f.raw_text}`")
    home_authorities = data["authorities"][data["home"].country]
    target_authorities = data["authorities"][data["target"].country]
    out += ["", "### What changes?", ""]
    for key in ("central_bank", "data_protection", "energy_regulator"):
        hf, tf = home_authorities[key], target_authorities[key]
        hv = "; ".join(f.value for f in hf) if hf else "Not specified in dossier"
        tv = "; ".join(f.value for f in tf) if tf else "Not specified in dossier"
        status = "Same wording" if hf and tf and [f.value.casefold() for f in hf] == [f.value.casefold() for f in tf] else "Different or missing claim"
        hs = "; ".join(source_label(f.source) for f in hf) if hf else "Not specified in dossier"
        ts = "; ".join(source_label(f.source) for f in tf) if tf else "Not specified in dossier"
        out.append(f"- {key.replace('_',' ').title()}: {status}. Home: {hv} — {hs}. Target: {tv} — {ts}.")
    out += ["", "## Sector compliance", "", f"- Home: {comp['home'].value if comp['home'] else 'Not specified in dossier'} — {source_label(comp['home'].source) if comp['home'] else 'Not specified in dossier'}",
            f"- Target: {comp['target'].value if comp['target'] else 'Not specified in dossier'} — {source_label(comp['target'].source) if comp['target'] else 'Not specified in dossier'}", ""]
    if comp["home"]:
        out.append(f"  - Source excerpt: `{comp['home'].raw_text}`")
    if comp["target"]:
        out.append(f"  - Source excerpt: `{comp['target'].raw_text}`")
    out += ["", "## Tax", ""]
    for kind, pairs in data["tax"].items():
        for country, finding in pairs:
            out.append(f"- {country}: **{finding.value}** ({kind.replace('_',' ')}) — {source_label(finding.source)}")
            out.append(f"  - Source excerpt: `{finding.raw_text}`")
        if len(pairs) == 2:
            from .comparison_engine import tax_delta
            delta = tax_delta(pairs[0][1], pairs[1][1])
            if delta:
                out.append(f"- Computed target minus home: **{delta['percentage_points']:+g} percentage points** from {delta['home_input']:g}% ({source_label(delta['sources'][0])}) and {delta['target_input']:g}% ({source_label(delta['sources'][1])}).")
    out += ["", "## Language and localisation", ""]
    for country, fields in data["overview"].items():
        out.append(f"### {country}")
        for key in ("official_languages", "dominant_languages"):
            fs = fields[key]
            out.append(f"- {key.replace('_',' ').title()}: " + ("; ".join(f"{f.value} — {source_label(f.source)}" for f in fs) if fs else "Not specified in dossier"))
            for f in fs:
                out.append(f"  - Source excerpt: `{f.raw_text}`")
        out.append("- Business and commercial languages: Not specified in dossier unless explicitly stated.")
    out += ["", "## Shared regional blocs", ""]
    home_blocs = {f.value.casefold(): f for f in data["overview"][data["home"].country]["regional_blocs"]}
    target_blocs = {f.value.casefold(): f for f in data["overview"][data["target"].country]["regional_blocs"]}
    for key in sorted(set(home_blocs) & set(target_blocs)):
        a, b = home_blocs[key], target_blocs[key]
        out.append(f"- {a.value}: claimed by both — {data['home'].country}: {source_label(a.source)}; {data['target'].country}: {source_label(b.source)}. Membership does not exempt from national licensing, tax, consumer protection, or data protection.")
        out.append(f"  - Source excerpts: `{a.raw_text}` · `{b.raw_text}`")
    if not set(home_blocs) & set(target_blocs):
        out.append("No shared bloc claim found. Membership lists:")
        for country, blocs in ((data["home"].country, home_blocs), (data["target"].country, target_blocs)):
            out.append(f"- {country}: " + ("; ".join(f"{f.value} — {source_label(f.source)}" for f in blocs.values()) if blocs else "Not specified in dossier"))
    out += ["", "## Verify First register", ""]
    if not data["flags"]:
        out.append("No evidence-backed flags were generated for this pair.")
    for i, flag in enumerate(data["flags"], 1):
        src = source_label(flag.get("source"))
        out.append(f"<a id=\"flag-{i}\"></a>{i}. **{flag['severity']} · {flag['country']} · {flag['label']}** — {flag['reason']} Recommended verification: {flag['recommendation']} Source: {src}")
        if flag.get("entry"):
            out.append(f"   Dossier entry: `{flag['entry']}`")
    out += ["", "## Recommended pre-launch actions", "", "1. Verify each listed claim with the named local regulator or revenue authority.", "2. Confirm whether the described product activities trigger licensing or registration.", "3. Obtain local legal and tax advice before launch.", "", "## Sources and limitations", "", "Findings reflect only the loaded dossiers. Missing or ambiguous fields remain unspecified or require review.", "", f"**Disclaimer:** {DISCLAIMER}"]
    return "\n".join(out)
