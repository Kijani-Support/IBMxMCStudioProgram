# Passerelle (EN: "Gateway")

> **"Franchir la frontière, vérifier d'abord" / "Cross the border, verify first."**

**Team:** Christopher Damian Munene, Mark Lekayia — Group 1, IBM x MC Studio Dev Day.

> **Disclaimer:** Planning reference only — not legal, tax, or financial advice. Verify every figure, regulator, and tax rate directly with the relevant national or regional authority before acting.

---

## What Passerelle Does & Who We Serve

Passerelle turns the 54 country regulatory dossiers in `africa-regulatory/` (authored by Modus Chora Studio for the *Sita Sector Energy Playbook*; status: *planning reference, verify before acting*) into **sourced, plain-language cross-border launch briefs** and an **offline interactive dashboard**, while explicitly flagging what in those dossiers cannot yet be trusted.

- **Primary users:** Early-stage fintech founders in Central Africa (starting with **Cameroon → Gabon**, inside **CEMAC**) who need a clear first answer on regulators, taxes, compliance steps, and language before paying lawyers.
- **Secondary users:** Accelerator advisers and compliance leads checking which sections of a country planning draft are unverified or template-corrupted.

### Core Principles
1. **Code extracts; AI only explains** — zero figures are invented or inferred by an LLM; every calculation is deterministic Python.
2. **Every figure cites its dossier line** — provenance `(source: <file> §<section>, line <n>)` is created in `parser.py` and travels inside every `Field` object.
3. **Doubt is shown, never hidden** — systemic template errors appear in a separate banner, route/bloc contradictions drive Verify-first flags, and compound taxes are never silently reduced to a single number.
4. **Plain language first, legal vocabulary second** — every brief section ends with a jargon-free *"What this means for you"* / *"Ce que cela signifie pour vous"* takeaway.

---

## Run in 3 Commands (100% Offline, Python Standard Library)

From `Dev Day Challenge/Group 1/`:

```bash
# 1. Generate the English launch brief, facts.json, offline dashboard.html, DEMO.md, and 6-flag Demo Shortlist
python cli.py --sector fintech --home cameroon --target gabon --lang en --out brief_en.md --facts-out facts.json --dashboard --demo-out DEMO.md --shortlist

# 2. Generate the natural French launch brief (same sections & figures; original institution names preserved)
python cli.py --sector fintech --home cameroon --target gabon --lang fr --out brief_fr.md

# 3. Run the full rules audit (PASS/FAIL table across A1–A10, pytest, 54-country corpus, and offline dashboard)
python audit.py
```

Open `dashboard.html` directly in any browser (`start dashboard.html` on Windows / `open dashboard.html` on macOS) — **no server, no build step, no internet connection required**.

Works across **all 54 African countries** and **all 6 Sita sectors** (`fintech`, `healthtech`, `edtech`, `agritech`, `retail & ecommerce`, `energy & manufacturing`). Swap `--home` and `--target` to reverse any route.

---

## `in-dossier` vs `our-check` (Epistemic Boundary)

Passerelle strictly separates what the source dossiers say from external checks:

| Category | Confidence Tag | Where It Appears | Meaning |
|---|---|---|---|
| **Dossier facts & contradictions** (`V01`–`V20`) | `in-dossier` | Template banner, Sections 0–6, Bloc matrix | Directly extracted from `africa-regulatory/*.md` with file, section, line number, and raw text. |
| **External verification prompts** (`EXT-01`–`EXT-08` in `data/external_checks.json`) | `our-check` (`status: unverified`) | Dedicated **"Our checks (unverified)"** section only | Known gaps outside the dossiers (e.g. CEMAC regional banking supervision absent from all CEMAC files). Never mixed into dossier facts and carries no unsourced regulator acronyms when `source_url` is empty. |

### Data Confidence Score
Computed deterministically from **`country`-scope and `bloc`-scope flags only** (never legal risk):
- **High:** `0` high-severity country/bloc flags
- **Medium:** `1` to `2` high-severity country/bloc flags
- **Low:** `3+` high-severity country/bloc flags

Systemic template defects (`V01`, `V02`, `V03` affecting all `54/54` dossiers) are reported separately in the **Template-defect banner** so corpus-wide generator bugs never obscure route-specific signal.

---

## How Passerelle Handles Non-Math Compliance (KYC, AML/CFT, Licensing, Privacy & Language)

Numeric rules like VAT (`19.25%` → `18%`, `-1.25` percentage points) are easy to diff with arithmetic, while **non-math compliance** governs day-to-day startup operations and cannot be reduced to a subtraction. Passerelle evaluates non-math sections **structurally in code**—never hallucinating statutory rules that are absent from the dossiers:

| Non-Math Area | Plain-Language Operational Meaning | What Passerelle Checks Deterministically |
|---|---|---|
| **KYC (Know Your Customer)** | Checking who a user is before moving money (e.g., tiered onboarding from phone/ID checks for small wallets up to full national ID, selfie, and business-registry checks for higher limits). | Flags when the dossier only provides generic boilerplate instead of local ID/tier rules, and checks **language shifts** (e.g., Cameroon bilingual → Gabon French-only) that require localising KYC screens and consent flows. |
| **AML/CFT (Anti-Money Laundering / Combating Financing of Terrorism)** | Ongoing monitoring after onboarding: sanctions/PEP screening, flagging suspicious transaction patterns, keeping records, and reporting suspicious transactions via a local compliance officer to the country's Financial Intelligence Unit (FIU). | Recognises that `"AML/CFT compliance"` in §4 is verbatim boilerplate across all 54 dossiers, so it presents it as a **starting checklist prompt** rather than researched country law and points founders to the real licensing authority to confirm local FIU reporting duties. |
| **Financial Licensing** | Approval to hold customer funds, process payments, or issue credit (directly or via a licensed bank partner). | Cross-checks `data/sector_map.json` against §4 (`V01`) to stop founders from applying to a privacy regulator for a payments licence, normalises shared central banks (`BEAC`, `BCEAO`) via `data/aliases.json` (`V07`), and flags missing regional banking supervision strictly under **Our checks (unverified)**. |
| **Data Protection (Privacy)** | Registering customer personal-data handling, collecting user consent, securing ID/transaction records, and checking cross-border data storage rules. | Flags conflicting agency expansions under the same acronym (`V08`, e.g. `CNPD` across Cameroon and Gabon), placeholder-only privacy slots (`V20`, 25/54 dossiers), and leaked VAT percentages masquerading as registration fees (`V03`, 54/54 dossiers). |
| **Consumer Protection & Language** | Transparent fee disclosure before payment, working dispute/refund channels, and legally valid contracts in the target country's official language. | Splits official vs. dominant spoken/business languages at depth 0, highlights which home languages drop out on arrival (e.g., English drops out moving Cameroon → Gabon), and preserves boilerplate honesty on §4 `"consumer protection"`. |

---

## Project Architecture

| File | Purpose |
|---|---|
| `parser.py` | Loads all 54 dossiers against `_template.md` + corpus boilerplate frames; produces provenance-tagged `Field` objects and `data/corpus_profile.json`. |
| `blocs.py` | Normalises regional blocs through `data/aliases.json`, keeps qualifiers (`observer`, `dormant`, `verify`) separate, and attaches startup meanings from `data/blocs.json`. |
| `compare.py` | Compares regulators (central bank, DPA, sector regulator via `data/sector_map.json`), §4 steps, CIT/VAT (never subtracting compound cells), and depth-0 language lists. |
| `validate.py` | Lean 11-rule validation registry (`V01`–`V08`, `V10`, `V12`, `V20`) with `RULE_ERROR` isolation, shared-bloc consistency matrix, `data/flags_all.json`, and 6-flag Demo Shortlist. |
| `facts.py` | Wires parsing, comparison, blocs, validation, external checks, and Data Confidence into `facts.json`. |
| `render.py` | Renders bilingual Markdown briefs (`en` / `fr`) and `DEMO.md` strictly from `facts.json`. |
| `dashboard.py` | Generates single-file offline `dashboard.html` with Evidence Drawer, severity/rule filters, tickable checklist, CEMAC matrix, print stylesheet, and Markdown export. |
| `cli.py` | Command-line interface (`--sector`, `--home`, `--target`, `--lang`, `--out`, `--dashboard`, `--demo-out`, `--shortlist`). |
| `audit.py` | Automated rules self-check (`A1`–`A10`) printing a PASS/FAIL table and exiting non-zero on failure. |
| `data/` | `aliases.json`, `blocs.json`, `expected_currency_by_bloc.json`, `external_checks.json`, `sector_map.json`, `i18n_fr.json`, `corpus_profile.json`, `flags_all.json`. |
| `tests/` | Golden route tests (`test_golden_cameroon_gabon.py`) and validation/broken-file tests (`test_validate.py`). |
| `DEMO.md` | Generated 8-minute live demo run script and 4-minute 6-flag walkthrough from `facts.json`. |

---

## Known Limits

- **Source dossier origin:** The 54 input dossiers were generated for an Energy Playbook (`Updated: 2026-07-31`); Section 3 is energy-specific and Section 4 contains systemic slot-shift defects across all 54 files (`V01`–`V03`).
- **Compound & non-numeric tax rates:** 14 countries have compound CIT/VAT cells and 4 have non-numeric rates (`None ...`). Passerelle reports all extracted rates and equal-headline caveats rather than computing misleading deltas.
- **Unverified external checks:** Items in `data/external_checks.json` remain marked `status: unverified` until official government or central-bank URLs are attached.
- **Offline scope:** `dashboard.html` renders the generated route (and its full shared-bloc matrix) offline; switching to another route regenerates `dashboard.html` in <1 second via `cli.py --dashboard`.
- **No live legal/tax feed:** Passerelle does not query live statutory databases or provide legal advice.

---

> **Reminder:** Planning reference only — not legal, tax, or financial advice.
