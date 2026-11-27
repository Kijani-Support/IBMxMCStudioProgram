# Validation notes

## Runtime corpus scan

- The loader discovered 54 country dossiers, excluding the README and template.
- Parse status: 54 clean, 0 partial, 0 failed. “Clean” means the file has a title, at least the expected top-level heading structure, and section 4 sector rows parse. This does not certify that every field was interpreted semantically.
- Six distinct section 4 sector labels were discovered at runtime.
- Registered rule counts: `missing_fields` 0; `conflicting_tax_rates` 0; `rate_without_date` 103.
- Ten-flag precision sample: manually checked the first ten rate-without-date flags against the named file and line. 10/10 genuinely show a CIT or VAT rate without an effective year on that rate row. The first two are Algeria CIT (`26% (19% for production activities)`, line 44) and VAT (`19%`, line 45); the next eight are the two tax rows for Angola, Benin, Botswana, and Burkina Faso. This verifies the specific rule condition, not the legal correctness of any rate.
- The date rule recognizes explicit four-digit years. A date elsewhere in the dossier does not count as the rate row’s effective date. `None`, ranges, and nonnumeric values are not compared as numeric rates.

## Generated pair checks

- Kenya → Tanzania, Retail & ecommerce: loaded each country from its dossier; extracted the section 4 row at line 37 in both; text similarity 1.00 at threshold 0.72 (shown only as “likely equivalent”); CIT 30% vs 30% yields 0 percentage points; VAT 16% vs 18% yields +2 percentage points. Each input and result has both dossier citations. The files claim shared African Union and EAC membership. No explicit digital-services tax rate is specified; the generic section 4 mention is not promoted to a country tax figure. Four Verify First rows are generated for the two tax entries per country that lack an effective date.
- Senegal → Ghana exercised a West African pair and a distinct language profile. It loaded both dossiers and section 4 at runtime; official-language fields are French and English. The dossiers report CIT 30% vs 25% and VAT 18% vs 15%, so numeric deltas are computable from those source rows.
- Nigeria → Morocco exercised a pair with no shared regional economic organization in the overview claims. Both list African Union, so there is no pair with literally zero shared bloc claims in this corpus. Nigeria CIT is written as `30% (25% for qualifying SMEs)` and Morocco as `20–31% by bracket`, so the comparator does not compute a CIT delta; their explicit VAT rows can be compared. This is a corpus limitation, not suppressed by the comparator.

## Automated checks

- `python -m unittest discover -s tests -v`: 7 tests pass. Synthetic fixtures cover country/sector discovery, malformed files, authority/tax/language extraction, section 4, missing fields, conflicting tax entries, percentage-point differences, comparison, provenance, Markdown, source-code fact guard, and write-scope snapshots.
- The scope test snapshots the dossier tree and files outside Group 7, executes the full loader/scan/compare/report pipeline, and confirms both snapshots are unchanged. Its only temporary file is created under this group folder and removed automatically.
- Clean dependency install succeeded in a temporary Python virtual environment using `requirements.txt`. Streamlit `AppTest` rendered the app with 0 exceptions. A local listening server could not be started because sandbox socket binding is restricted; normal `streamlit run app.py` remains the documented launch command.

## Scope limitations and deviations

- The implementation is intentionally conservative but incomplete relative to the full proposed rule catalog. It registers missing-field, conflicting tax-rate, and missing-effective-year rules. Cross-dossier inconsistency, law-date/repeal/citation-quality, and sector-specific misclassification rules are not implemented; no external verification layer is present.
- Blocs are compared by exact written name. The optional alias config is not needed for runtime parsing, but alternate spellings may fail to match. Trade benefits, customs rules, establishment rights, and service implications are not inferred.
- No regulator matching aliases or country facts are embedded. Energy authority is displayed as a generic authority source, not assumed to be the selected sector regulator.
- Language extraction reports official and dominant spoken fields only. Business/commercial language remains explicitly unspecified unless separately parsed in future.
- Tax parsing covers explicit CIT/VAT table rows and preserves rate text. Digital tax prose is too generic to attribute a DST to a particular country; it is not treated as an enacted tax claim. Legislation extraction and jurisdiction splits beyond verbatim source text remain future work.
- Similarity is character-based text similarity, not legal equivalence. Common boilerplate can produce a high score; the UI labels results “likely equivalent” and shows both original texts.
- The generated demo is a reproducible artifact from runtime input, not a hand-authored country-specific template.
