# Africa Launch Comparator

Source-linked MVP comparing regulatory dossier entries for a selected sector and country pair. It reads Markdown at runtime and does not embed country facts.

## Install and run

Use Python 3.10 or newer. From this folder, create a clean virtual environment and install the pinned dependency:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

The dossier location defaults to `../../africa-regulatory/` relative to this folder. Set `AFRICA_REGULATORY_DIR` to use another read-only dossier directory.

## Data and limitations

The loader discovers country files at runtime from their Markdown title headings and excludes `README.md` and `_template.md`. Section 4 sector rows, overview labels, explicit authority labels, and tax table rows are parsed conservatively. Ambiguous claims remain as written or unspecified. Regional bloc names are shown as written; no country-specific aliases or facts are configured. Similarity is textual and the displayed threshold is 0.72. The tool is not legal or tax advice.

All implementation, configuration, tests, and generated project outputs belong in this Group 7 folder. The dossier input folder is read-only.

## Tests

Run `python -m unittest discover -s tests -v`. Tests use synthetic fixture dossiers for extraction and comparison, plus a scope snapshot check against the real dossier tree.

## Project presentation

The generated nine-slide deck is `presentation/Africa_Launch_Comparator.pptx`. To regenerate it from the current demo brief and runtime dossier files, install `presentation/requirements.txt` and run `python presentation/generate_deck.py`.
