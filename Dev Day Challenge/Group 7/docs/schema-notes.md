# Dossier schema notes

These notes were written before application code, after inspecting `africa-regulatory/README.md`, `_template.md`, and the complete Kenya, Tanzania, Senegal, Uganda, Morocco, and Comoros dossiers. The input tree contains 54 country dossiers plus `_template.md` and `README.md` (56 Markdown files total).

## Actual files and country names

- Country dossiers are lowercase Markdown files named with a slug, for example `cote-divoire.md`, `democratic-republic-of-congo.md`, and `sao-tome-and-principe.md`.
- The filename is not a reliable display name. Use the first-level heading (`# Kenya — Regulatory, Compliance and Tax Dossier`) as the primary country name; derive the display name from the text before the em dash. Retain filename as the stable identifier and cite the filename.
- Exclude `_template.md` and `README.md` from country discovery. The README calls the corpus 54 countries; enumerating all Markdown files without exclusions yields 56.

## Heading hierarchy and section 4

- Dossiers use a level-one title followed by six level-two sections numbered `1. Overview` through `6. Expansion notes`.
- Section 4 is titled `Sector compliance steps`. Current observed dossiers represent the six Sita Sector names as rows in a Markdown table (`Sector` / `Primary compliance steps`), not as subsection headings. Sector names include Fintech, Healthtech, Edtech, Agritech, Retail & ecommerce, and Energy & manufacturing.
- The template describes a table but does not define its exact table schema. Extract rows only within section 4, preserving cell text and line provenance. For malformed tables, headings, or prose, retain the section as raw text and mark extraction for review; do not invent missing rows.

## How fields are expressed

- Central bank and data-protection authority are usually labelled prose in section 2 (`Central bank:` / `Data protection:`). Names and guidance often share a paragraph.
- Energy regulator/authority is labelled prose in section 3. Section 4 sometimes repeats regulator claims, but those rows are sector compliance text, not authoritative regulator records.
- CIT and VAT are usually rows in a two-column Markdown table in section 5. Some rates include ranges, parenthetical qualifications, `None`, or verification notes; preserve exact rate text. Broader tax discussion (including withholding and possible digital taxes) is prose and frequently generic or not country-specific. Do not promote hypothetical or generic mentions to a documented DST rate.
- Languages and blocs are typically semicolon-separated values in the section 1 overview table. Section 6 may repeat them in prose. Separate only fields explicitly labelled `Official languages`, `Dominant spoken languages`, or `Regional blocs`; do not infer business/commercial language from official languages.
- Legislation may be embedded in prose and tables; no consistent legislation schema was observed. Avoid extracting a legal act/date unless an explicit name and date/status can be tied together.

## Variations and anomalies observed

- Kenya and Tanzania share a consistent heading and table skeleton, but section 4 embeds percent figures in fintech and energy compliance text (e.g. `data protection registration (16%)`, `Energy regulator: 30%`). These percentages are not reliable evidence of fees or tax rates; keep them as raw compliance text and flag the suspicious numeric content for review rather than treating as tax facts.
- Senegal uses the same skeleton while presenting French/WAEMU context and acronym-heavy authority names; this confirms field values should remain verbatim and aliases must be generic configuration only.
- Morocco's CIT value is a range with bracket qualification; Comoros explicitly writes `None (verify sales-tax regime)` for VAT and contains the same kind of percentage embedded in section 4. Numeric rate parsing must reject `None` and avoid converting ranges to a single rate.
- Some bloc entries include parenthetical status such as `dormant`, `observer`, or an alternate name (`WAEMU (UEMOA)`). Preserve the complete written claim; canonical aliases should never erase it.
- The README's matrix is a separate summary with snapshot caveats and must not substitute for dossier citations or values.

## Extraction strategy and boundaries

- Parse Markdown with a small line-aware parser suitable for headings, paragraphs, and pipe tables. Track 1-based line numbers and heading path for every Finding.
- Discover countries only from dossier files and the title line. Discover sectors dynamically from section 4 table rows across loaded dossiers. A small keyword/alias configuration may aid generic sector matching and regional-bloc name normalization; it must contain no country facts.
- Extract section 4 rows deterministically from tables. Keep raw section and raw row text, and use conservative fuzzy comparison with a visible threshold; likely matches remain labelled “likely equivalent.”
- Extract central bank, data protection, and energy/sector authority only from explicit labels or clear labelled prose. Do not infer an authority from a sector or country name. Tax extraction is limited to explicitly labelled tax rows and explicit tax-rate claims; preserve conflicts as lists and parse a numeric rate only when unambiguous. A range is not a single numeric rate.
- Extract languages and blocs from explicitly labelled overview fields. Keep lists and written forms. Do not assign business/commercial language unless expressly stated. Do not infer membership, trade benefits, customs treatment, exemptions, or legal requirements from bloc membership.
- For unsupported layouts or ambiguous claims, retain raw text, mark Needs review, and display “Not specified in dossier” when absent. Never silently reconcile contradictions or replace dossier claims with external information.
- Provenance is mandatory: file, heading path, line span or excerpt for every finding; all derived values retain every contributing source.

## Input location and scope

The dossier directory is `../../africa-regulatory/` relative to this Group 7 folder (resolved from the repository root). It is outside the group folder and is read-only. The application should use one configurable input path (environment variable with this default) and documentation should preserve that location. All generated code, configuration, tests, and outputs belong under `Dev Day Challenge/Group 7/` only.

## Assumptions to preserve

- A dossier title is the most dependable display-name source; filename slug is the stable key.
- “Business” and “commercial” language are separate from the source's official and dominant spoken language fields and will remain unspecified unless dossier text explicitly supplies them.
- An explicit absent/`None` statement is distinct from a missing section or an unmentioned field.
- Numeric text in an unrelated section (especially section 4) is not necessarily a tax or fee and must remain attached to its own claim category.
- The dossiers are planning references and can contain errors. The tool reports what they say and points to verification; it does not certify legal or tax correctness.
