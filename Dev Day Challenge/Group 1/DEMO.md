# Passerelle — Live Demo Script (Cameroon -> Gabon · Fintech)

> *Franchir la frontière, vérifier d'abord. / Cross the border, verify first.* — Christopher Damian Munene, Mark Lekayia (Group 1, IBM x MC Studio Dev Day)

> **Disclaimer:** Planning reference only — not legal, tax, or financial advice. Verify every figure and authority directly before acting.

## 8-Minute Live Run Script

### Minute 0–1 · Problem & Core Principles
- Introduce **Passerelle**: early-stage founders expanding across borders need clear answers on regulators, taxes, and language *and* need to know which lines of a planning dossier cannot yet be trusted.
- State our four principles: (1) code extracts, AI only explains; (2) every figure cites its dossier line; (3) doubt is shown, never hidden; (4) plain language first, legal vocabulary second.

### Minute 1–3 · Generate the Sourced Brief (EN & FR) + Offline Dashboard
Run from `Dev Day Challenge/Group 1/`:
```bash
python cli.py --sector fintech --home cameroon --target gabon --lang en --out brief_en.md --facts-out facts.json --dashboard --shortlist
python cli.py --sector fintech --home cameroon --target gabon --lang fr --out brief_fr.md
```
- Point to the **Template-defect banner** (3 systemic template flags separated from route Data Confidence) and the **Data Confidence** score: **High** (0 High, 5 Medium, 0 Low — dossier quality only, never legal risk).
- Show the **French brief** (`brief_fr.md`): identical section count and figures, natural French, original institution names preserved.

### Minute 3–5 · Open the Offline Dashboard (`dashboard.html`)
Open `dashboard.html` directly in any browser (zero server, zero internet, zero external requests):
```bash
start dashboard.html
```
- Toggle **EN / FR**, tick a step in the **First Steps Checklist**, click any **`source:` button** to open the **Evidence Drawer** showing the exact raw dossier line, and click **Export Brief (.md)**.
- Highlight the **CEMAC Consistency Matrix** showing every member country side-by-side (`ok` / `note` / `flag`) to prove Passerelle validates across the entire bloc, not just two files.

### Minute 5–7 · Prove Scale & Discipline (`validate.py` + `audit.py`)
```bash
python validate.py
python audit.py
```
- Show `data/flags_all.json` covering all **54 dossiers**, and `audit.py` printing **PASS** on A1–A10 (zero country literals in code, 100% docstrings, 5 extra pairs + all 6 sectors, broken-file safety, zero secrets, offline dashboard).

### Minute 7–8 · Swap Test & Close
```bash
python cli.py --sector fintech --home gabon --target cameroon --lang en
```
- Point out the flipped VAT percentage-point delta and language diff, confirming nothing is hard-coded.

---

## 4-Minute Flags Walkthrough (DEMO SHORTLIST)

Walk through these 6 curated flags from `facts.json` in order — moving from corpus-wide template errors to route-specific dossier contradictions and finally unverified external checks:

### 1. `[V01]` — `HIGH` · `in-dossier`
- **Where:** `cameroon.md §4, line 33; gabon.md §4, line 33`
- **What Passerelle caught:** Section 4 Fintech row names the data protection authority as the payments and lending licensor instead of the central bank (54 of 54 dossiers).
- **Why it matters:** Asking a privacy office for a payment licence wastes time because central banks handle financial licensing.

### 2. `[V03]` — `HIGH` · `in-dossier`
- **Where:** `cameroon.md §4, line 33; gabon.md §4, line 33`
- **What Passerelle caught:** Section 4 reuses Section 5 VAT or CIT values inside fee or regulator slots (54 of 54 dossiers).
- **Why it matters:** A sales-tax or profit-tax percentage is not a registration fee, so budgeting from Section 4 would be wrong.

### 3. `[V08]` — `MED` · `in-dossier`
- **Where:** `cameroon.md §2, line 21; gabon.md §2, line 21`
- **What Passerelle caught:** Data-protection acronym 'CNPD' has 2 different expansions across dossiers: 'Commission Nationale pour la Protection des Données' (Gabon) vs 'Commission Nationale pour la Protection des Données à Caractère Personnel' (Cameroon).
- **Why it matters:** Conflicting agency names suggest the dossier entry may be templated rather than verified against national law.

### 4. `[V10]` — `MED` · `in-dossier`
- **Where:** `cameroon.md §5, line 44`
- **What Passerelle caught:** Cameroon CIT cell '30% (33% for some sectors)' flagged (compound/multi-rate cell).
- **Why it matters:** Multiple brackets, missing numbers, or extreme tax rates mean a simple headline figure can mislead your financial forecast.

### 5. `[V06]` — `MED` · `in-dossier`
- **Where:** `cameroon.md §1, line 13`
- **What Passerelle caught:** Cameroon lists 'ECOWAS (observer)' (carries 'observer' qualifier; unconfirmed by partner dossiers).
- **Why it matters:** Observer or single-country bloc claims do not guarantee shared trade, customs, or licensing rules.

### 6. `[EXT-01]` — `MED` · `our-check`
- **Where:** `data/external_checks.json (unverified, outside dossier)`
- **What Passerelle caught:** In CEMAC, banking and payment-institution licensing and supervision involve a regional banking supervisor alongside BEAC and national finance ministries; no regional banking supervisor is mentioned in any CEMAC dossier.
- **Why it matters:** Highlights an institutional gap absent from the dossiers while keeping external knowledge strictly labelled unverified.
