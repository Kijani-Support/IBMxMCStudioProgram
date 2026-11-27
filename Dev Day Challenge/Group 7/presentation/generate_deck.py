"""Build a sourced project-pitch deck from the generated Markdown brief."""
from pathlib import Path
import re
import sys

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.dossier_loader import load_all
from src.sector_extractor import extract_sectors
from src.extractors.fields import overview

BRIEF_PATH = ROOT / "docs" / "demo-brief.md"
AUDIT_PATH = ROOT / "docs" / "validation-notes.md"
OUTPUT_PATH = ROOT / "presentation" / "Africa_Launch_Comparator.pptx"

NAVY = "101B2C"
NAVY_2 = "17263A"
INK = "172337"
MUTED = "64748B"
PAPER = "F5F7FA"
WHITE = "FFFFFF"
TEAL = "21C6A3"
TEAL_DARK = "087F6B"
GOLD = "F6B94A"
CORAL = "F17D69"
LINE = "DCE3EA"
PALE_TEAL = "E2F7F1"
PALE_GOLD = "FFF4DA"


def color(value):
    return RGBColor.from_string(value)


def parse_sections(text):
    result, current = {}, None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            result[current] = []
        elif current:
            result[current].append(line)
    return result


def plain(line):
    return re.sub(r"\*\*|`|<[^>]+>", "", line).strip()


def source_after_dash(line):
    # Keep the visible dossier citation written by the report generator.
    return line.split(" — ", 1)[1].strip() if " — " in line else ""


def country_sections(lines):
    groups, current = {}, None
    for line in lines:
        if line.startswith("### "):
            current = line[4:].strip()
            groups[current] = []
        elif current:
            groups[current].append(line)
    return groups


def add_bg(slide, fill):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color(fill)
    shape.line.fill.background()
    slide.shapes._spTree.remove(shape._element)
    slide.shapes._spTree.insert(2, shape._element)


def box(slide, x, y, w, h, fill, radius=False, line=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
                                   Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color(fill)
    if line:
        shape.line.color.rgb = color(line)
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    if radius:
        shape.adjustments[0] = 0.12
    return shape


def txt(slide, x, y, w, h, value, size=16, fill=INK, bold=False,
        font="Aptos", align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP, margin=0.03):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = shape.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(margin)
    frame.margin_right = Inches(margin)
    frame.margin_top = Inches(margin)
    frame.margin_bottom = Inches(margin)
    frame.vertical_anchor = valign
    p = frame.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = str(value)
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color(fill)
    return shape


def bullet_list(slide, x, y, w, h, items, size=15, fill=INK, gap=9, bullet=TEAL):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = shape.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(0.02)
    frame.margin_right = Inches(0.02)
    frame.margin_top = Inches(0.02)
    for idx, item in enumerate(items):
        p = frame.paragraphs[0] if idx == 0 else frame.add_paragraph()
        p.space_after = Pt(gap)
        p.level = 0
        run = p.add_run()
        run.text = "•  "
        run.font.name = "Aptos"
        run.font.size = Pt(size)
        run.font.bold = True
        run.font.color.rgb = color(bullet)
        run = p.add_run()
        run.text = item
        run.font.name = "Aptos"
        run.font.size = Pt(size)
        run.font.color.rgb = color(fill)
    return shape


def header(slide, eyebrow, title, subtitle=None, dark=False):
    primary = WHITE if dark else INK
    secondary = "B4C3D2" if dark else MUTED
    txt(slide, 0.65, 0.36, 12.0, 0.28, eyebrow.upper(), 10, TEAL_DARK if not dark else TEAL, True)
    txt(slide, 0.65, 0.75, 12.0, 0.55, title, 26, primary, True)
    if subtitle:
        txt(slide, 0.68, 1.36, 11.9, 0.5, subtitle, 12, secondary)


def footer(slide, number, dark=False, citation=""):
    c = "9AAABD" if dark else MUTED
    box(slide, 0.65, 7.08, 12.0, 0.012, "344459" if dark else LINE)
    txt(slide, 0.67, 7.12, 10.8, 0.2, citation or "AFRICA LAUNCH COMPARATOR  ·  GROUP 7", 8, c)
    txt(slide, 11.8, 7.10, 0.75, 0.22, f"{number:02d}", 9, c, True, align=PP_ALIGN.RIGHT)


def slide(prs, background=PAPER):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, background)
    return s


def short(line, limit=150):
    value = plain(line)
    return value if len(value) <= limit else value[:limit - 1].rsplit(" ", 1)[0] + "…"


def compact_citation(value):
    match = re.search(r"([\w-]+\.md).*?(line \d+)", value)
    return f"{match.group(1)} {match.group(2)}" if match else value


def make_deck():
    if not BRIEF_PATH.exists() or not AUDIT_PATH.exists():
        raise FileNotFoundError("Generate docs/demo-brief.md and docs/validation-notes.md first.")
    brief_text = BRIEF_PATH.read_text(encoding="utf-8")
    audit_text = AUDIT_PATH.read_text(encoding="utf-8")
    sections = parse_sections(brief_text)
    audit = parse_sections(audit_text)
    title_line = next(line for line in brief_text.splitlines() if line.startswith("# "))[2:]
    route = title_line.split(": ", 1)[1]
    home, target = [part.strip() for part in route.split("→")]
    meta = next(line for line in brief_text.splitlines() if line.startswith("**Sector:**"))
    sector_name = re.search(r"\*\*Sector:\*\*\s*(.*?)\s*·", meta).group(1)
    dossiers = load_all()
    dossier_by_country = {d.country: d for d in dossiers}
    corpus_count = len(dossiers)
    sector_count = len({name for dossier in dossiers for name in extract_sectors(dossier)})
    tax_lines = [line for line in sections.get("Tax", []) if line.startswith("- ")]
    delta_lines = [line for line in sections.get("Executive summary", []) if "percentage points" in line]
    tax_values = [line for line in tax_lines if "**" in line and "percentage points" not in line]
    regulatory_lines = sections.get("Regulatory authorities", [])
    regulatory_groups = country_sections(regulatory_lines)
    bloc_lines = [line for line in sections.get("Shared regional blocs", []) if line.startswith("- ")]
    flag_lines = [line for line in sections.get("Verify First register", []) if re.match(r"(?:<a[^>]*>.*?</a>)?\d+\. \*\*", line)]
    audit_text_flat = "\n".join(audit_text.splitlines())
    clean_match = re.search(r"Parse status: (\d+) clean, (\d+) partial, (\d+) failed", audit_text_flat)
    rule_match = re.search(r"Registered rule counts: `missing_fields` (\d+); `conflicting_tax_rates` (\d+); `rate_without_date` (\d+)", audit_text_flat)
    precision_match = re.search(r"Ten-flag precision sample: manually checked.*?(\d+/\d+) genuinely", audit_text_flat)
    test_match = re.search(r"`python -m unittest discover -s tests -v`: (\d+) tests pass", audit_text_flat)
    disclaimer = "Not legal or tax advice. Verify dossier claims with the relevant authorities and qualified local counsel."

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    prs.core_properties.title = "Africa Launch Comparator — Project Presentation"
    prs.core_properties.subject = "Runtime dossier comparison and source-linked launch briefs"
    prs.core_properties.author = "Group 7"

    # 1 — Cover
    s = slide(prs, NAVY)
    box(s, 0.68, 0.65, 0.11, 5.95, TEAL)
    txt(s, 1.05, 0.8, 10.8, 0.32, "IBM DEV DAY  ·  GROUP 7", 11, TEAL, True)
    txt(s, 1.02, 1.55, 10.9, 1.55, "Africa Launch\nComparator", 37, WHITE, True)
    txt(s, 1.07, 3.45, 10.7, 0.72, "Turn country dossiers into a sourced, side-by-side launch brief.", 19, "C7D2DE")
    box(s, 1.05, 4.55, 5.7, 0.78, NAVY_2, True)
    txt(s, 1.3, 4.73, 5.2, 0.4, f"DEMO ROUTE   {route}   ·   {sector_name}", 12, WHITE, True)
    stats = [(str(corpus_count), "country dossiers"), (str(sector_count), "discovered sectors"), ("1", "source-first brief")]
    for i, (value, label) in enumerate(stats):
        x = 1.1 + i * 3.7
        txt(s, x, 5.9, 0.8, 0.55, value, 27, TEAL if i != 1 else GOLD, True)
        txt(s, x + 0.85, 6.02, 2.5, 0.32, label, 12, "C7D2DE")
    footer(s, 1, dark=True, citation="Sources: africa-regulatory/README.md · dossier section 4 rows · " + disclaimer)

    # 2 — Why this exists
    s = slide(prs)
    header(s, "The problem", "A country dossier is useful—until you compare two", "Launch decisions depend on differences, missing details, and evidence you can trace.")
    box(s, 0.7, 2.08, 3.82, 3.95, WHITE, True, LINE)
    txt(s, 1.0, 2.38, 3.15, 0.45, "THE FRICTION", 11, CORAL, True)
    bullet_list(s, 1.0, 2.95, 3.12, 2.7, ["Facts are spread across Markdown files", "Similar headings hide different formats", "A rate without a date needs review", "A number without a source is hard to trust"], 14, INK, 13, CORAL)
    box(s, 4.77, 2.08, 3.82, 3.95, WHITE, True, LINE)
    txt(s, 5.08, 2.38, 3.1, 0.45, "THE TOOL", 11, TEAL_DARK, True)
    bullet_list(s, 5.08, 2.95, 3.1, 2.7, ["Reads dossier files at runtime", "Discovers countries and section 4 sectors", "Keeps conflicts as separate findings", "Shows source file, heading, and line"], 14, INK, 13)
    box(s, 8.83, 2.08, 3.82, 3.95, NAVY_2, True)
    txt(s, 9.15, 2.38, 3.1, 0.45, "THE OUTPUT", 11, GOLD, True)
    bullet_list(s, 9.15, 2.95, 3.0, 2.7, ["Structured launch brief", "Comparable checklists", "Verify First register", "Markdown export with citations"], 14, WHITE, 13, GOLD)
    footer(s, 2, citation="Design intent: keep dossier facts separate from computed comparisons.")

    # 3 — Architecture
    s = slide(prs, NAVY)
    header(s, "How it works", "Runtime in. Provenance stays attached.", "No country tax rates, regulator names, languages, or bloc membership are embedded in application code.", True)
    stages = [
        ("01", "Markdown dossiers", "Read only input\nCountry files discovered by title"),
        ("02", "Line-aware parser", "Headings + tables\nSection 4 rows + labelled fields"),
        ("03", "Finding records", "Value + raw text\nFile, heading, line, confidence"),
        ("04", "Compare + flag", "Text similarity\nNumeric deltas only when clear"),
        ("05", "Brief + export", "Streamlit dashboard\nMarkdown with citations"),
    ]
    for i, (number, name, body) in enumerate(stages):
        x = 0.7 + i * 2.52
        box(s, x, 2.55, 2.2, 2.28, NAVY_2, True, "344459")
        txt(s, x + 0.18, 2.78, 0.55, 0.38, number, 16, TEAL if i < 4 else GOLD, True)
        txt(s, x + 0.18, 3.3, 1.85, 0.38, name, 15, WHITE, True)
        txt(s, x + 0.18, 3.82, 1.85, 0.76, body, 11, "C7D2DE")
        if i < len(stages) - 1:
            txt(s, x + 2.22, 3.45, 0.27, 0.35, "→", 20, TEAL, True, align=PP_ALIGN.CENTER)
    box(s, 0.72, 5.32, 11.9, 0.9, "123447", True)
    txt(s, 0.98, 5.52, 11.4, 0.45, "Every extracted value carries its source. Every computed delta cites both inputs.", 16, WHITE, True, align=PP_ALIGN.CENTER)
    footer(s, 3, True, "Implementation: app.py · src/dossier_loader.py · src/extractors/fields.py · src/report_generator.py")

    # 4 — Live demo requirements
    s = slide(prs)
    header(s, "Generated demo", f"{route}  /  {sector_name}", "Section 4 requirements are loaded independently from each country dossier.")
    requirement_lines = [line for line in sections.get("Executive summary", []) if "requirement:" in line]
    req_texts = [short(line.split(": ", 1)[1].split(" — source:", 1)[0], 210) for line in requirement_lines[:2]]
    req_sources = [source_after_dash(line) for line in requirement_lines[:2]]
    box(s, 0.72, 2.08, 5.8, 2.36, WHITE, True, LINE)
    box(s, 6.8, 2.08, 5.8, 2.36, WHITE, True, LINE)
    txt(s, 1.02, 2.32, 5.1, 0.33, home.upper(), 11, TEAL_DARK, True)
    txt(s, 7.1, 2.32, 5.1, 0.33, target.upper(), 11, TEAL_DARK, True)
    txt(s, 1.02, 2.82, 5.05, 0.88, req_texts[0] if req_texts else "Not specified in dossier", 15, INK)
    txt(s, 7.1, 2.82, 5.05, 0.88, req_texts[1] if len(req_texts) > 1 else "Not specified in dossier", 15, INK)
    txt(s, 1.02, 4.0, 5.05, 0.3, req_sources[0] if req_sources else "", 8, MUTED)
    txt(s, 7.1, 4.0, 5.05, 0.3, req_sources[1] if len(req_sources) > 1 else "", 8, MUTED)
    summary_line = next((line for line in sections.get("Executive summary", []) if "similarity" in line), "")
    similarity = re.search(r"similarity ([0-9.]+); threshold ([0-9.]+)", summary_line)
    sim = similarity.group(1) if similarity else "—"
    threshold = similarity.group(2) if similarity else "—"
    box(s, 0.72, 4.78, 5.8, 1.12, PALE_TEAL, True)
    txt(s, 1.0, 4.98, 1.2, 0.55, sim, 28, TEAL_DARK, True)
    txt(s, 2.18, 5.0, 3.95, 0.45, f"Text similarity · threshold {threshold}\nLabel: likely equivalent", 12, INK, True)
    box(s, 6.8, 4.78, 5.8, 1.12, PALE_GOLD, True)
    txt(s, 7.1, 5.0, 5.2, 0.75, "The matching text is generic boilerplate. The interface shows both source rows and avoids claiming legal equivalence.", 13, INK)
    footer(s, 4, citation=f"Sources: {req_sources[0] if req_sources else 'section 4'}  ·  {req_sources[1] if len(req_sources)>1 else 'section 4'}")

    # 5 — Tax deltas
    s = slide(prs)
    header(s, "Tax comparison", "Rates stay verbatim; deltas are computed only when clear", "Target minus home, in percentage points; both original rates and both dossier citations are shown.")
    for row_idx, kind in enumerate(("corporate income tax", "vat")):
        y = 2.05 + row_idx * 2.0
        candidates = [line for line in tax_values if f"({kind})" in line.lower()]
        delta = next((line for line in delta_lines if kind.split()[0].upper() in line.upper()), "")
        box(s, 0.72, y, 11.9, 1.62, WHITE, True, LINE)
        txt(s, 1.0, y + 0.16, 2.55, 0.3, kind.upper(), 11, MUTED, True)
        for i, line in enumerate(candidates[:2]):
            x = 1.0 + i * 3.72
            m = re.search(r"- (.*?): \*\*(.*?)\*\*", line)
            country = m.group(1) if m else (home if i == 0 else target)
            rate = m.group(2) if m else "Not specified in dossier"
            source = source_after_dash(line)
            txt(s, x, y + 0.52, 3.45, 0.34, f"{country}: {rate}", 18, INK, True)
            txt(s, x, y + 0.99, 3.45, 0.43, source, 8, MUTED)
        if delta:
            dm = re.search(r"\*\*(.*?) percentage points\*\*", delta)
            delta_value = dm.group(1) if dm else "—"
            txt(s, 8.68, y + 0.53, 3.45, 0.42, f"Δ  {delta_value} pp", 18, TEAL_DARK, True, align=PP_ALIGN.RIGHT)
            delta_sources = re.search(r"from (\S+) — ([\w-]+\.md.*?) and (\S+) — ([\w-]+\.md.*?);", delta)
            if delta_sources:
                citations = f"{compact_citation(delta_sources.group(2))} · {compact_citation(delta_sources.group(4))}"
                txt(s, 8.6, y + 1.02, 3.5, 0.4, f"Inputs: {delta_sources.group(1)} / {delta_sources.group(3)}\n{citations}", 7, MUTED, align=PP_ALIGN.RIGHT)
    box(s, 0.72, 6.15, 11.9, 0.58, NAVY_2, True)
    txt(s, 0.95, 6.25, 11.4, 0.32, "No numeric delta is produced for ranges, conflicting text, or rates that cannot be parsed unambiguously.", 12, WHITE, True, align=PP_ALIGN.CENTER)
    footer(s, 5, citation="Sources: both country dossiers · 5. Tax planning · rate rows and computed inputs cited above")

    # 6 — Authorities, language, blocs
    s = slide(prs)
    header(s, "What changes?", "Different authorities. Shared claims. Local context still matters.", "Names below are dossier claims, not a legal determination of mandate or licensing scope.")
    reg_names = [name for name in regulatory_groups if name in (home, target)]
    reg_cards = []
    for country in (home, target):
        lines = regulatory_groups.get(country, [])
        values = [short(line, 106) for line in lines if line.startswith("- ")]
        reg_cards.append((country, values))
    for i, (country, values) in enumerate(reg_cards):
        x = 0.72 + i * 6.08
        box(s, x, 2.0, 5.8, 2.17, WHITE, True, LINE)
        txt(s, x + 0.27, 2.22, 5.2, 0.34, country.upper(), 11, TEAL_DARK, True)
        raw_lines = [line for line in regulatory_groups.get(country, []) if line.startswith("- ")][:3]
        names = [short(plain(line.split(" — ", 1)[0]).removeprefix("- "), 88) for line in raw_lines]
        citations = [source_after_dash(line) for line in raw_lines]
        bullet_list(s, x + 0.27, 2.66, 5.18, 0.88, names, 10, INK, 3)
        txt(s, x + 0.28, 3.53, 5.1, 0.55, "\n".join(citations), 7, MUTED)
    lang_cards = []
    for country in (home, target):
        fields = overview(dossier_by_country[country])
        official = fields["official_languages"]
        dominant = fields["dominant_languages"]
        langs = ["Official: " + (", ".join(f.value for f in official) if official else "Not specified in dossier"),
                 "Dominant: " + (", ".join(f.value for f in dominant) if dominant else "Not specified in dossier")]
        citations = []
        for findings in (official, dominant):
            if findings:
                source = findings[0].source
                citations.append(f"{source.file} · {' › '.join(source.heading_path)} · line {source.line}")
        lang_cards.append((country, langs, citations))
    box(s, 0.72, 4.43, 5.8, 1.4, PALE_TEAL, True)
    box(s, 6.8, 4.43, 5.8, 1.4, PALE_TEAL, True)
    for i, (country, langs, citations) in enumerate(lang_cards):
        x = 1.0 + i * 6.08
        txt(s, x, 4.62, 5.15, 0.25, f"{country} · LANGUAGES", 10, TEAL_DARK, True)
        txt(s, x, 4.94, 5.17, 0.54, "\n".join(langs), 9, INK)
        txt(s, x, 5.48, 5.17, 0.25, "\n".join(citations), 6.7, MUTED)
    shared_bloc_names = [m.group(1) for line in bloc_lines if (m := re.match(r"- ([^:]+):", line))]
    bloc_citations = []
    for line in bloc_lines:
        for filename, line_no in re.findall(r"([\w-]+\.md) · .*?line (\d+)", line):
            bloc_citations.append(f"{filename} · 1. Overview · line {line_no}")
    shared_blocs = ["Shared claims: " + (", ".join(shared_bloc_names) if shared_bloc_names else "Not specified in dossier"),
                    "Sources: " + "; ".join(dict.fromkeys(bloc_citations))]
    box(s, 0.72, 6.0, 11.9, 0.72, NAVY_2, True)
    txt(s, 0.98, 6.08, 11.4, 0.55, "BLOC CLAIMS  ·  " + "\n".join(shared_blocs) + " · Membership does not exempt a business from national obligations.", 8, WHITE)
    footer(s, 6, citation="Sources: selected country dossiers · sections 1–3 · citations and excerpts appear in the exported brief")

    # 7 — Verify first
    s = slide(prs, NAVY)
    header(s, "Verify First", "A flag is a question with evidence—not a verdict", "The current registered rules focus on missing fields, conflicting tax claims, and rates without an explicit year.", True)
    total_flags = len(flag_lines)
    count_match = re.search(r"rate_without_date` (\d+)", audit_text)
    total_rate_flags = count_match.group(1) if count_match else "—"
    box(s, 0.72, 2.0, 3.1, 3.88, NAVY_2, True, "344459")
    txt(s, 1.08, 2.42, 2.3, 0.75, str(total_flags), 38, GOLD, True)
    txt(s, 1.08, 3.28, 2.2, 0.75, "pair-level flags\nfrom the demo", 15, WHITE, True)
    txt(s, 1.08, 4.65, 2.15, 0.75, f"{total_rate_flags} corpus flags\nfor rates lacking a year", 13, "C7D2DE")
    box(s, 4.2, 2.0, 8.4, 3.88, "17263A", True, "344459")
    txt(s, 4.55, 2.28, 7.7, 0.4, "DEMO REGISTER · FIRST EVIDENCE-BACKED ITEMS", 10, TEAL, True)
    for i, line in enumerate(flag_lines[:4]):
        y = 2.82 + i * 0.69
        flag_text = re.sub(r"<a[^>]*>.*?</a>", "", line)
        match = re.match(r"(\d+)\. \*\*(.*?)\*\* — (.*)", flag_text)
        content = short(match.group(2) + " — " + match.group(3), 120) if match else short(line, 120)
        citation = flag_text.split("Source: ", 1)[1].strip() if "Source: " in flag_text else ""
        box(s, 4.54, y, 7.7, 0.6, "203349", True)
        txt(s, 4.72, y + 0.04, 7.35, 0.26, content, 8.5, WHITE)
        txt(s, 4.72, y + 0.32, 7.35, 0.22, citation, 6.7, "B4C3D2")
    txt(s, 4.55, 5.65, 7.55, 0.2, "Every register row retains its dossier file, heading, line, and recommended verification.", 9, "B4C3D2")
    footer(s, 7, True, "Corpus audit: docs/validation-notes.md · demo flags: docs/demo-brief.md")

    # 8 — Validation
    s = slide(prs)
    header(s, "Validation", "Coverage was checked against the corpus and synthetic fixtures", "The scan tests structure and traceability; it does not certify the legal correctness of dossier claims.")
    clean, partial, failed = clean_match.groups() if clean_match else ("—", "—", "—")
    precision = precision_match.group(1) if precision_match else "—"
    test_count = test_match.group(1) if test_match else "—"
    metrics = [(clean, "parsed cleanly", TEAL_DARK), (f"{partial}/{failed}", "partial / failed", CORAL), (precision, "sample flags met rule", TEAL_DARK), (test_count, "automated tests passed", TEAL_DARK)]
    for i, (value, label, accent) in enumerate(metrics):
        x = 0.72 + i * 3.05
        box(s, x, 2.1, 2.78, 1.5, WHITE, True, LINE)
        txt(s, x + 0.22, 2.32, 2.3, 0.6, value, 26, accent, True)
        txt(s, x + 0.22, 3.02, 2.3, 0.28, label, 10, MUTED, True)
    rule_counts = rule_match.groups() if rule_match else ("—", "—", "—")
    box(s, 0.72, 4.02, 11.9, 1.58, NAVY_2, True)
    txt(s, 1.0, 4.25, 10.9, 0.3, "REGISTERED RULE COUNTS", 10, TEAL, True)
    txt(s, 1.0, 4.75, 10.9, 0.58, f"Missing fields  {rule_counts[0]}       Tax conflicts  {rule_counts[1]}       Rates without year  {rule_counts[2]}", 17, WHITE, True)
    txt(s, 0.78, 5.94, 11.8, 0.5, "The ten reviewed flags all point to rate rows with no explicit effective year. Review confirms the flag condition—not the accuracy of the stated rates.", 12, INK)
    footer(s, 8, citation="Source: docs/validation-notes.md · tests/test_comparator.py")

    # 9 — Limits and next steps
    s = slide(prs, NAVY)
    header(s, "What’s next", "Keep the brief cautious. Expand coverage where evidence allows.", "A transparent MVP is useful when it is clear about what it cannot determine.", True)
    columns = [
        ("NOW", ["Runtime discovery and source-linked findings", "Section 4 comparisons", "CIT / VAT extraction and cautious deltas", "Three registered Verify First rules"]),
        ("NEXT", ["Cross-dossier inconsistency rules", "Alias-backed bloc matching", "Legislation dates and citation quality", "Sector-specific licensing / DST checks"]),
        ("ALWAYS", ["No silent corrections", "No inferred licences from sector labels", "No external claim merged into dossier facts", disclaimer]),
    ]
    for i, (name, items) in enumerate(columns):
        x = 0.72 + i * 4.06
        box(s, x, 2.05, 3.75, 3.75, NAVY_2, True, "344459")
        txt(s, x + 0.25, 2.32, 3.2, 0.34, name, 11, (TEAL, GOLD, CORAL)[i], True)
        bullet_list(s, x + 0.25, 2.9, 3.15, 2.65, items, 12, WHITE, 12, (TEAL, GOLD, CORAL)[i])
    box(s, 0.72, 6.08, 11.9, 0.58, "123447", True)
    txt(s, 0.95, 6.19, 11.4, 0.3, "Run: python -m pip install -r requirements.txt  ·  streamlit run app.py", 12, WHITE, True, align=PP_ALIGN.CENTER)
    footer(s, 9, True, "Limitations and deviations: docs/validation-notes.md")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUTPUT_PATH)
    return OUTPUT_PATH


if __name__ == "__main__":
    print(make_deck())
