# IBM Dev Day Challenge — Cross-Border Launch Navigator

> **Updated:** 2026-11-27 · **Build time:** 1 h 30 min · **Demo:** 15 min per group · **Groups:** 7

This is a **new challenge, separate from the earlier builds** in `IBM Dev Day (Drop Your Folder Here)/`. Do not continue, copy or reuse code from those projects. Every group starts from an empty folder.

## The problem

A startup that already operates in one African country wants to launch in a second one. Before it spends money on lawyers, it needs a fast first answer to: *who regulates us there, what do we have to do to comply, how is the tax different, and what language do we work in?*

The repo already holds that raw material: **54 country dossiers** in [`africa-regulatory/`](../africa-regulatory/README.md), all written to the same template. But nobody can read two dossiers side by side and pull out what matters for one sector in a few minutes.

**Your job in 90 minutes:** build a tool that does it.

## What your tool must do

Input: a **sector**, a **home country** and a **target country**.
Output: a **launch brief** that shows, for the target country compared with the home country:

1. **Regulators to engage**: central bank, data protection authority, and the sector regulator.
2. **Sector compliance steps** for the chosen sector (from section 4 of the dossier).
3. **Tax differences**: corporate income tax and VAT, home vs target.
4. **Language**: official and business languages, and whether they differ from home.
5. **Shared regional blocs** (EAC, SADC, ECOWAS, WAEMU, CEMAC…) and what that means for the move.
6. **"Verify first" flags**: entries in the dossiers that look wrong, inconsistent or incomplete. The dossiers are planning drafts and **do contain mistakes**. Finding them is part of the score.

The tool must read the dossier markdown files directly. No hard-coding the answers for your country pair.

## Group assignments

Each group gets a new sector and route.

| Group | Sector | Home → Target | Bloc angle |
|---|---|---|---|
| Group 1 | Fintech | Cameroon → Gabon | Inside CEMAC (shared central bank) |
| Group 2 | Healthtech | Kenya → Rwanda | Inside EAC, language shift |
| Group 3 | Edtech | Zambia → Malawi | Inside SADC, minors' data |
| Group 4 | Agritech | Tanzania → Zambia | EAC to SADC, cross-border produce |
| Group 5 | Retail & ecommerce | Côte d'Ivoire → Senegal | Inside WAEMU (shared currency) |
| Group 6 | Energy & manufacturing | Morocco → Benin | North Africa to WAEMU, no shared bloc |
| Group 7 | Retail & ecommerce | Kenya → Tanzania | Inside EAC, digital-service tax |

## Rules

- Build only inside your group's folder: `Dev Day Challenge/Group N/`.
- Any stack is fine: a CLI, a web page, a notebook or an app. IBM tools (watsonx.ai, Granite models, IBM Cloud) earn the stretch points below.
- Libraries and frameworks are fine. Code from earlier Dev Day builds is not.
- Commit and push before the 90 minutes end. Whatever is pushed at the 90-minute mark is what you demo.
- Every figure in your brief must show which dossier it came from.

## Stretch goals (if you finish early)

- Works for **any** pair of the 54 countries, not just yours.
- Uses watsonx.ai or a Granite model to write a plain-language summary of the brief, without inventing figures that aren't in the dossiers.
- Exports the brief as a one-page PDF or Markdown file.

## Schedule

| Block | Duration | What happens |
|---|---|---|
| Challenge briefing | 5 min | This page walked through, and questions answered |
| Build activity | **1 h 30 min (90 min)** | Groups build the Navigator for their assigned route |
| Demos | **15 min per group** | 7 groups, in group order |

### Demo slots (15 min each)

| Slot | Group | Starts at (after build ends) |
|---|---|---|
| 1 | Group 1 — Fintech, Cameroon → Gabon | +0:00 |
| 2 | Group 2 — Healthtech, Kenya → Rwanda | +0:15 |
| 3 | Group 3 — Edtech, Zambia → Malawi | +0:30 |
| 4 | Group 4 — Agritech, Tanzania → Zambia | +0:45 |
| 5 | Group 5 — Retail & ecommerce, Côte d'Ivoire → Senegal | +1:00 |
| 6 | Group 6 — Energy & manufacturing, Morocco → Benin | +1:15 |
| 7 | Group 7 — Retail & ecommerce, Kenya → Tanzania | +1:30 |

All 7 demos take **1 h 45 min**. With the briefing, the session runs **3 h 20 min** without breaks.

### Each 15-minute demo

| Minutes | Content |
|---|---|
| 0–8 | Live run: generate the launch brief for your route |
| 8–12 | Your "verify first" flags: what's wrong or doubtful in the dossiers, and how your tool caught it |
| 12–15 | Q&A and changeover to the next group |

Demos are hard-stopped at 15 minutes. Have your tool loaded before your slot.

## How demos are scored

| Criterion | Points |
|---|---|
| Brief is correct and complete for all 6 required outputs | 30 |
| Reads the dossiers (not hard-coded); every figure has its source | 20 |
| Quality of "verify first" flags (real mistakes found) | 20 |
| Clarity of the brief for a non-lawyer founder | 15 |
| Demo delivered within 15 minutes | 5 |
| Stretch goals | 10 |
| **Total** | **100** |

> The dossiers and your briefs are planning references, not legal, tax or financial advice.
