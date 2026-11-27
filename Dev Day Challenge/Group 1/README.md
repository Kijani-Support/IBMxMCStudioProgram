# Passerelle (EN: "Gateway")

> **"Franchir la frontière, vérifier d'abord" / "Cross the border, verify first."**

- **Team:** Christopher Damian Munene, Mark Lekayia — Group 1, IBM x MC Studio Dev Day.
- **What we do:** Turn country regulatory dossiers into sourced, plain-language cross-border launch briefs, and flag what in those dossiers cannot yet be trusted.
- **Who we serve:** Early-stage fintech founders in Central Africa (starting with Cameroon to Gabon, inside CEMAC) who need a first answer on regulators, tax, and language before paying lawyers; plus accelerator advisers and compliance leads checking which parts of a planning draft are unverified.
- **Core principles:**
  1. Code extracts; AI only explains.
  2. Every figure cites its dossier line (`(source: <file> §<section>, line <n>)`).
  3. Doubt is shown, never hidden.
  4. Plain language first, legal vocabulary second.
- **Data source:** 54 country dossiers in `africa-regulatory/` (authored by Modus Chora Studio for the Sita Sector Energy Playbook; status: *planning reference, verify before acting*). Section 3 is energy-specific and treated as context.

> **Disclaimer:** Planning reference only — not legal, tax, or financial advice. Verify every figure and authority with the relevant national or regional regulator before acting.

## Current Status — Phase 1 (Parser & Corpus Profile)

Run the template-driven parser across all 54 dossiers and regenerate `data/corpus_profile.json`:

```bash
python parser.py
```
