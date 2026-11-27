# Passerelle — Cross-Border Launch Brief: Cameroon -> Gabon

*Cross the border, verify first.* — Christopher Damian Munene, Mark Lekayia (Group 1, IBM x MC Studio Dev Day)

> **Disclaimer / Avertissement:** Planning reference only — not legal, tax, or financial advice. Verify every figure and authority with the relevant regulator before acting.

> **Systemic Dossier Template Defects (Excluded from Route Score)**
> These defects affect most of the 54 source dossiers (template generation errors) and are separated from your route's country/bloc confidence score:
> - [V01] 54 of 54 dossiers share this defect: Section 4 Fintech row names the data protection authority as the payments and lending licensor instead of the central bank (54 of 54 dossiers). (source: cameroon.md §4, line 33; gabon.md §4, line 33)
> - [V02] 54 of 54 dossiers share this defect: Section 4 Energy & manufacturing row puts a percentage inside the Energy regulator slot instead of an authority name (54 of 54 dossiers). (source: cameroon.md §4, line 38; gabon.md §4, line 38)
> - [V03] 54 of 54 dossiers share this defect: Section 4 reuses Section 5 VAT or CIT values inside fee or regulator slots (54 of 54 dossiers). (source: cameroon.md §4, line 33; gabon.md §4, line 33)

## 0. At-a-glance

- **Route:** Cameroon (Home) -> Gabon (Target) (source: cameroon.md, line 1); (source: gabon.md, line 1)
- **Sector:** Fintech
- **Shared blocs:** African Union (source: cameroon.md §1, line 13; gabon.md §1, line 13), CEMAC (source: cameroon.md §1, line 13; gabon.md §1, line 13)
- **Verify-first flags (country & bloc):** 0 High, 5 Medium, 0 Low (5 total; template banner: 3)
- **Data Confidence:** **High** (0 High, 5 Medium, 0 Low) — Measures source-dossier data quality for this route (country & bloc flags only), never legal risk.

## 1. Regulators to engage

- **Central bank** (`Same`):
  - Cameroon: Banque des États de l'Afrique Centrale (BEAC) [normalised: `BEAC`] (source: cameroon.md §2, line 19)
  - Gabon: BEAC [normalised: `BEAC`] (source: gabon.md §2, line 19)
- **Currency** (`Same`): Cameroon: `XAF` (source: cameroon.md §1, line 12) | Gabon: `XAF` (source: gabon.md §1, line 12)
- **Data protection authority** (`Differs`):
  - Cameroon: CNPD (Commission Nationale pour la Protection des Données à Caractère Personnel) (source: cameroon.md §2, line 21)
  - Gabon: CNPD (Commission Nationale pour la Protection des Données) (source: gabon.md §2, line 21)
  - *Same acronym (CNPD) with different full names across the two dossiers* (source: cameroon.md §2, line 21; gabon.md §2, line 21)
- **Sector regulator (licensing contact)** — Central bank (primary licensing contact for payments and lending) (`Same`):
  - Cameroon: Banque des États de l'Afrique Centrale (BEAC) [normalised: `BEAC`] (source: cameroon.md §2, line 19)
    - **Body named in Section 4 (conflict flagged):** `CNPD (Commission Nationale pour la Protection des Données à Caractère Personnel) licensing for payments and lending` [FLAGGED — template defect, do not treat as fact] (source: cameroon.md §4, line 33)
  - Gabon: BEAC [normalised: `BEAC`] (source: gabon.md §2, line 19)
    - **Body named in Section 4 (conflict flagged):** `CNPD (Commission Nationale pour la Protection des Données) licensing for payments and lending` [FLAGGED — template defect, do not treat as fact] (source: gabon.md §4, line 33)

**What this means for you:** You stay under the same central bank (the public authority that manages money and approves financial services), so your main financial regulator does not change, but you still need to confirm the privacy office (the agency overseeing customer personal data) in the target country.

## 2. Sector compliance steps (First steps)

> Warning: the Section 4 row for this sector contains a known template defect (flagged below). Affected steps are marked untrusted and must not be treated as fact.

### Gabon (Target)
1. **[FLAGGED — template defect, do not treat as fact]** *"CNPD (Commission Nationale pour la Protection des Données) licensing for payments and lending"* (source: gabon.md §4, line 33)
2. AML/CFT compliance (source: gabon.md §4, line 33)
3. **[FLAGGED — template defect, do not treat as fact]** *"data protection registration (18%)"* (source: gabon.md §4, line 33)
4. consumer protection (source: gabon.md §4, line 33)

### Cameroon (Home)
1. **[FLAGGED — template defect, do not treat as fact]** *"CNPD (Commission Nationale pour la Protection des Données à Caractère Personnel) licensing for payments and lending"* (source: cameroon.md §4, line 33)
2. AML/CFT compliance (source: cameroon.md §4, line 33)
3. **[FLAGGED — template defect, do not treat as fact]** *"data protection registration (19.25%)"* (source: cameroon.md §4, line 33)
4. consumer protection (source: cameroon.md §4, line 33)

**What this means for you:** Parts of this checklist mix up the wrong agency or insert a sales-tax rate where a registration fee belongs, so treat it only as a starting prompt and confirm every step with the real licensing office.

## 3. Tax differences (CIT and VAT)

- **Corporate income tax (CIT):**
  - Cameroon: `30% (33% for some sectors)` (source: cameroon.md §5, line 44)
  - Gabon: `30%` (source: gabon.md §5, line 44)
  - **Delta (target − home):** `Same headline rate (30%)` — Caveat: variant rates present (Cameroon: 30%, 33%); no numeric delta claimed for compound cells beyond the headline (source: cameroon.md §5, line 44; gabon.md §5, line 44)
- **VAT / sales tax:**
  - Cameroon: `19.25%` (source: cameroon.md §5, line 45)
  - Gabon: `18%` (source: gabon.md §5, line 45)
  - **Delta (target − home):** `-1.25 percentage points` (source: cameroon.md §5, line 45; gabon.md §5, line 45)

**What this means for you:** At least one tax rate has multiple brackets or no single number in the dossier, so do not lock in a financial model until the local tax office confirms which rate applies to your business.

## 4. Language

- **Official languages** (`Differs`):
  - Cameroon: English, French (source: cameroon.md §1, line 14)
  - Gabon: French (source: gabon.md §1, line 14)
  - Shared official languages: French (source: cameroon.md §1, line 14; gabon.md §1, line 14)
  - Official languages in home that drop out in target: English (source: cameroon.md §1, line 14)
- **Dominant spoken / business languages** (`Differs`):
  - Cameroon: French, English, Cameroonian Pidgin, Fulfulde, Ewondo, Duala (source: cameroon.md §1, line 15)
  - Gabon: French, Fang, Myene, Punu, Nzebi (source: gabon.md §1, line 15)

**What this means for you:** Official languages change when you cross this border, so budget time and money to translate your contracts, customer screens, and government filings into the target country's official language.

## 5. Shared regional blocs

- **African Union**: Continent-wide political body backing the African Continental Free Trade Area (AfCFTA), though day-to-day company licensing still happens at the country or sub-regional level. (source: cameroon.md §1, line 13; gabon.md §1, line 13)
- **CEMAC (Central African Economic and Monetary Community)**: Shared currency zone (XAF) and single central bank (BEAC), meaning no foreign-exchange conversion risk between members and shared regional banking rules. (source: cameroon.md §1, line 13; gabon.md §1, line 13)
- **Only in home (Cameroon):** `ECOWAS (observer)` (source: cameroon.md §1, line 13)

### Bloc consistency matrix (CEMAC)

| Country | Currency | Central bank | Bloc symmetry | DPA naming | Placeholders | Flag counts | Source |
|---|---|---|---|---|---|---|---|
| Cameroon | `ok` XAF | `note` BEAC (full name) | `flag` V06 (ECOWAS (observer)) | `flag` V08 (CNPD mismatch) | `ok` 0 | `note` 0H/3M/0L (3) | (source: cameroon.md §1, line 12) |
| Central African Republic | `ok` XAF | `ok` BEAC | `ok` ok | `flag` V20 (unnamed) | `flag` 3 (§2,§3,§5) | `note` 0H/4M/0L (4) | (source: central-african-republic.md §1, line 12) |
| Chad | `ok` XAF | `ok` BEAC | `ok` ok | `flag` V20 (unnamed) | `flag` 3 (§2,§3,§5) | `note` 0H/4M/0L (4) | (source: chad.md §1, line 12) |
| Equatorial Guinea | `ok` XAF | `ok` BEAC | `ok` ok | `flag` V20 (unnamed) | `flag` 3 (§2,§3,§5) | `note` 0H/4M/0L (4) | (source: equatorial-guinea.md §1, line 12) |
| Gabon | `ok` XAF | `ok` BEAC | `ok` ok | `flag` V08 (CNPD mismatch) | `flag` 2 (§3,§5) | `note` 0H/3M/0L (3) | (source: gabon.md §1, line 12) |
| Congo (Republic) | `ok` XAF | `ok` BEAC | `ok` ok | `flag` V20 (unnamed) | `flag` 3 (§2,§3,§5) | `note` 0H/4M/0L (4) | (source: republic-of-congo.md §1, line 12) |

**What this means for you:** Sharing a regional bloc (an agreement among neighbouring countries on shared currency or trade rules) can simplify money transfers and customs, but you still need local registration in the target country.

## 6. Verify first

### Medium (5)
- **[V04 · PLACEHOLDER-S3]** (Scope: `country` | Source type: `in-dossier`): Gabon dossier contains placeholder text in section 3 (energy regulator: 'Ministry of Energy (verify current regulator)'). (source: gabon.md §3, line 25)
  - *Why it matters:* The dossier does not yet name a verified office or confirmed figure for this step.
  - *Who to ask:* Check the national government portal or Ministry of Finance/Commerce for the current official agency or rate.
- **[V04 · PLACEHOLDER-S5]** (Scope: `country` | Source type: `in-dossier`): Gabon dossier contains placeholder text in section 5 (investment promotion agency: 'Verify current agency'). (source: gabon.md §5, line 47)
  - *Why it matters:* The dossier does not yet name a verified office or confirmed figure for this step.
  - *Who to ask:* Check the national government portal or Ministry of Finance/Commerce for the current official agency or rate.
- **[V06 · BLOC-ASYMMETRY]** (Scope: `bloc` | Source type: `in-dossier`): Cameroon lists 'ECOWAS (observer)' (carries 'observer' qualifier; unconfirmed by partner dossiers). (source: cameroon.md §1, line 13)
  - *Why it matters:* Observer or single-country bloc claims do not guarantee shared trade, customs, or licensing rules.
  - *Who to ask:* Do not plan licensing around this bloc; verify full membership on the bloc's official member list.
- **[V08 · DPA-EXPANSION-MISMATCH]** (Scope: `bloc` | Source type: `in-dossier`): Data-protection acronym 'CNPD' has 2 different expansions across dossiers: 'Commission Nationale pour la Protection des Données' (Gabon) vs 'Commission Nationale pour la Protection des Données à Caractère Personnel' (Cameroon). (source: cameroon.md §2, line 21; gabon.md §2, line 21)
  - *Why it matters:* Conflicting agency names suggest the dossier entry may be templated rather than verified against national law.
  - *Who to ask:* Confirm the official legal name and active registration office of each country's privacy regulator directly.
- **[V10 · TAX-CIT-ANOMALY]** (Scope: `country` | Source type: `in-dossier`): Cameroon CIT cell '30% (33% for some sectors)' flagged (compound/multi-rate cell). (source: cameroon.md §5, line 44)
  - *Why it matters:* Multiple brackets, missing numbers, or extreme tax rates mean a simple headline figure can mislead your financial forecast.
  - *Who to ask:* Confirm the exact tax bracket for your sector with the national revenue authority.

**What this means for you:** Resolve every High flag before paying legal fees or filing applications, because each flag marks a contradiction or missing name inside the source dossiers.

## Our checks (unverified)

Items below draw on checks outside the source dossiers and are never presented as dossier facts. Status remains unverified until an official source URL is attached.

- **[EXT-01]** (Status: `unverified` | Source URL: none recorded yet): In CEMAC, banking and payment-institution licensing and supervision involve a regional banking supervisor alongside BEAC and national finance ministries; no regional banking supervisor is mentioned in any CEMAC dossier.
- **[EXT-02]** (Status: `unverified` | Source URL: none recorded yet): Confirm whether Cameroon holds ECOWAS observer status; Cameroon is a CEMAC member and ECOWAS observer status is not confirmed by partner dossiers.
- **[EXT-03]** (Status: `unverified` | Source URL: none recorded yet): Confirm the current operational national data-protection authority in both countries rather than relying on the conflicting CNPD expansions printed in the dossiers.
