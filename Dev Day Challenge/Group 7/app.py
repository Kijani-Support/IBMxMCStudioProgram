"""Streamlit front end for the runtime dossier comparator."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from src.dossier_loader import load_all, dossier_dir
from src.sector_extractor import all_sector_names
from src.extractors.fields import authorities, tax, overview
from src.comparison_engine import compare
from src.anomaly_detector import scan
from src.report_generator import brief_data, to_markdown, source_label

st.set_page_config(page_title="Africa Launch Comparator", page_icon="🌍", layout="wide")
st.title("Africa Launch Comparator")
st.caption("A source-linked planning brief from the runtime country dossiers.")
st.warning("Not legal or tax advice. Dossiers are planning references; verify every claim with qualified local counsel and the relevant authorities.")

try:
    with st.spinner("Loading and analysing country dossiers…"):
        dossiers = load_all()
except (FileNotFoundError, OSError) as exc:
    st.error(f"Cannot load dossier files. Check AFRICA_REGULATORY_DIR ({dossier_dir()}): {exc}")
    st.stop()
if not dossiers:
    st.error(f"No country dossiers found in {dossier_dir()}.")
    st.stop()

countries = {d.country: d for d in dossiers}
col1, col2, col3 = st.columns(3)
home_name = col1.selectbox("Home country", sorted(countries))
target_options = [n for n in sorted(countries) if n != home_name]
target_name = col2.selectbox("Target country", target_options)
sectors = all_sector_names(dossiers)
sector = col3.selectbox("Sector", sectors)
home, target = countries[home_name], countries[target_name]
comparison = compare(home, target, sector)
all_flags, _counts = scan(dossiers)
flags = [f for f in all_flags if f["country"] in {home_name, target_name}]
tax_data = {"corporate_income_tax": [], "vat": [], "digital_taxes": []}
for country_name, dossier in [(home_name, home), (target_name, target)]:
    for kind, findings in tax(dossier).items():
        tax_data[kind].extend((country_name, f) for f in findings)
data = brief_data(home, target, sector, comparison, tax_data, flags)

st.header(f"{home_name} → {target_name}")
st.write(f"**Sector:** {sector} · **Generated:** {data['generated']}")
st.subheader("Executive summary")
if comparison["similarity"] is None:
    st.warning("Section 4 content is missing or could not be parsed for at least one country.")
else:
    st.write(f"Sector requirements are **{comparison['status'].lower()}** (text similarity {comparison['similarity']:.0%}; threshold 72%).")
    st.caption(f"Home source: {source_label(comparison['home'].source)}")
    st.caption(f"Target source: {source_label(comparison['target'].source)}")
for kind in ("corporate_income_tax", "vat"):
    pairs = tax_data[kind]
    if len(pairs) == 2:
        from src.comparison_engine import tax_delta
        delta = tax_delta(pairs[0][1], pairs[1][1])
        if delta:
            st.write(f"{kind.replace('_',' ').upper()} delta: **{delta['percentage_points']:+g} percentage points**, target minus home; inputs {delta['home_input']:g}% ({source_label(delta['sources'][0])}) and {delta['target_input']:g}% ({source_label(delta['sources'][1])}).")
st.markdown(f"Verify First flags for this pair: **{len(flags)}**; [counted from the register rows](#verify-first-register) below.")

st.subheader("Regulatory authorities")
auth_cols = st.columns(2)
for col, country_name, d in zip(auth_cols, [home_name, target_name], [home, target]):
    with col:
        st.markdown(f"**{country_name}**")
        for key, values in authorities(d).items():
            if not values:
                st.write(f"{key.replace('_',' ').title()}: Not specified in dossier")
            for f in values:
                st.write(f"{key.replace('_',' ').title()}: {f.value}")
                st.caption(source_label(f.source))
                with st.expander("Source excerpt"):
                    st.code(f.raw_text)
st.markdown("**What changes?**")
authority_rows = []
home_authorities, target_authorities = authorities(home), authorities(target)
for key in ("central_bank", "data_protection", "energy_regulator"):
    hf, tf = home_authorities[key], target_authorities[key]
    hv = "; ".join(f.value for f in hf) if hf else "Not specified in dossier"
    tv = "; ".join(f.value for f in tf) if tf else "Not specified in dossier"
    status = "Same wording" if hf and tf and [f.value.casefold() for f in hf] == [f.value.casefold() for f in tf] else "Different or missing claim"
    hs = "; ".join(source_label(f.source) for f in hf) if hf else "Not specified in dossier"
    ts = "; ".join(source_label(f.source) for f in tf) if tf else "Not specified in dossier"
    authority_rows.append({"Authority type": key.replace("_", " ").title(), "Home claim": hv, "Home source": hs, "Target claim": tv, "Target source": ts, "What changes?": status})
st.dataframe(authority_rows, hide_index=True, use_container_width=True)
st.caption("For retail and ecommerce, financial-sector regulation may become relevant when the business processes payments, holds customer funds, or operates payment services. Ordinary retail activity alone is not evidence of a central-bank licensing requirement.")

st.subheader("Sector compliance")
left, right = st.columns(2)
for col, country_name, finding in [(left, home_name, comparison["home"]), (right, target_name, comparison["target"])]:
    with col:
        st.markdown(f"**{country_name} checklist**")
        if finding:
            st.checkbox(finding.value, value=False, key=f"{country_name}-sector")
            st.caption(source_label(finding.source))
            with st.expander("Source excerpt"):
                st.code(finding.raw_text)
        else:
            st.warning("Not specified in dossier")
st.write(f"Comparison: **{comparison['status']}**" + (f" · similarity {comparison['similarity']:.2f} (threshold 0.72); matches are only likely equivalents." if comparison["similarity"] is not None else ""))

st.subheader("Tax")
for kind, pairs in tax_data.items():
    st.markdown(f"**{kind.replace('_',' ').title()}**")
    for country_name, f in pairs:
        c1, c2 = st.columns([1, 3])
        c1.write(f"{country_name}: {f.value}")
        c2.caption(source_label(f.source))
        with st.expander(f"{country_name} source excerpt — {kind}"):
            st.code(f.raw_text)
    if len(pairs) == 2 and kind in {"corporate_income_tax", "vat"}:
        from src.comparison_engine import tax_delta
        delta = tax_delta(pairs[0][1], pairs[1][1])
        if delta:
            st.info(f"Computed target minus home: {delta['percentage_points']:+g} percentage points, using {delta['home_input']:g}% ({source_label(delta['sources'][0])}) and {delta['target_input']:g}% ({source_label(delta['sources'][1])}).")
        else:
            st.caption("No numeric comparison: one or both rate texts are ambiguous or ranges.")
    elif not pairs:
        st.write("Not specified in dossier")

st.subheader("Language and localisation")
for country_name, d in [(home_name, home), (target_name, target)]:
    vals = overview(d)
    with st.expander(country_name, expanded=True):
        for key, label in [("official_languages", "Official languages"), ("dominant_languages", "Dominant spoken languages")]:
            fs = vals[key]
            if fs:
                st.write(f"{label}: " + "; ".join(f.value for f in fs))
                st.caption(source_label(fs[0].source))
            else:
                st.write(f"{label}: Not specified in dossier")
        st.write("Business and commercial languages: Not specified in dossier unless explicitly stated.")

st.subheader("Shared regional blocs")
ovs = {n: overview(d) for n, d in [(home_name, home), (target_name, target)]}
bloc_sets = {n: {f.value.casefold(): f for f in v["regional_blocs"]} for n, v in ovs.items()}
shared = set(bloc_sets[home_name]) & set(bloc_sets[target_name])
if shared:
    for key in sorted(shared):
        f1, f2 = bloc_sets[home_name][key], bloc_sets[target_name][key]
        st.write(f"**{f1.value}** — membership claimed by both dossiers.")
        st.caption(f"{home_name}: {source_label(f1.source)} · {target_name}: {source_label(f2.source)}")
        st.caption("Membership does not exempt you from national licensing, tax, consumer-protection, data-protection, or other applicable requirements.")
else:
    st.write("No shared bloc claim found. Each dossier lists:")
    for country_name in [home_name, target_name]:
        fs = ovs[country_name]["regional_blocs"]
        st.write(f"{country_name}: " + (", ".join(f.value for f in fs) if fs else "Not specified in dossier"))
        if fs:
            st.caption(source_label(fs[0].source))

st.subheader("Verify First register")
country_filter = st.multiselect("Country", [home_name, target_name], default=[home_name, target_name])
category_filter = st.multiselect("Category", sorted({f["category"] for f in flags}), default=sorted({f["category"] for f in flags}))
severity_filter = st.multiselect("Severity", ["Critical", "High", "Medium", "Low"], default=["Critical", "High", "Medium", "Low"])
visible = [f for f in flags if f["country"] in country_filter and f["category"] in category_filter and f["severity"] in severity_filter]
st.caption(f"{len(visible)} flags shown; each count refers to the filtered register rows.")
for f in visible:
    with st.expander(f"{f['severity']} · {f['country']} · {f['category']} · {f['label']}: {f['reason']}"):
        if f["entry"]:
            st.write(f"Dossier entry: {f['entry']}")
        st.write(f"Recommended verification: {f['recommendation']}")
        st.caption(source_label(f.get("source")))

st.subheader("Recommended pre-launch actions")
st.write("Verify the sourced claims with local authorities, confirm the product activities that trigger obligations, and obtain local legal and tax advice before launch.")
st.subheader("Sources and limitations")
st.write(f"Runtime input directory: `{dossier_dir()}`. Unsupported or ambiguous statements remain raw text or are marked for review. No external facts are merged.")
st.download_button("Download Markdown brief", to_markdown(data), file_name=f"{home_name.lower()}-{target_name.lower()}-launch-brief.md", mime="text/markdown")
