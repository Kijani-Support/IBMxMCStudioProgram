# Group 4: Cross-Border Navigator

## IBM Dev Day Challenge

**Project:** Cross-Border Navigator  
**Use Case:** Cross-Border Agritech Expansion  
**Demonstration Route:** Tanzania → Zambia  
**Team Members:**
- FAKII MOHAMMED
- EMMANUEL KAI

---

## 1. Project Overview

Cross-Border Navigator is an AI-assisted regulatory and market-entry planning tool designed to help businesses understand the requirements involved in expanding into another African country.

The platform compares country-specific regulatory and business information to generate a structured cross-border launch brief. It helps users identify important differences, potential compliance requirements, and issues that should be verified before entering a new market.

For the challenge demonstration, the application explores an agritech business expanding from Tanzania into Zambia.

## 2. Problem Statement

Businesses expanding across African borders often face fragmented regulatory information, different tax systems, licensing requirements, languages, and regional trade arrangements.

Finding and comparing this information manually can be time-consuming and may result in missed regulatory considerations.

Businesses need a practical way to:
- Understand regulatory differences between countries.
- Identify sector-specific compliance considerations.
- Compare tax and business requirements.
- Understand regional trade arrangements.
- Identify information that requires confirmation from official authorities.
- Organize market-entry research into an actionable brief.

## 3. Our Solution

Cross-Border Navigator transforms country regulatory dossiers into a structured launch-planning brief.

Users select a source country, destination country, and business sector. The application processes the available country information and presents a comparison of relevant market-entry considerations.

The solution emphasizes transparency by identifying information that needs further verification instead of presenting every extracted detail as confirmed legal advice.

## 4. Key Features

### Country-to-Country Comparison
Compare regulatory and business information between a source country and a destination country.

### Sector-Specific Compliance
Highlight regulatory considerations relevant to the selected business sector, including agritech.

### Tax Comparison
Present available corporate income tax and value-added tax information for comparison.

### Languages and Regional Trade Context
Show relevant language information and regional economic community considerations.

### Launch Brief Generation
Organize the comparison into a structured brief to support market-entry planning.

### Verify First Flags
Highlight information that requires confirmation before a business makes operational, financial, or legal decisions.

### Source-Based Country Dossiers
Use Markdown country dossiers as the information source, making it possible to update or extend country information without redesigning the application.

## 5. Demonstration: Tanzania to Zambia

The demonstration uses an agritech expansion scenario:

| Area | Tanzania | Zambia |
|---|---|---|
| Corporate Income Tax | 30% | 30% |
| Value Added Tax | 18% | 16% |
| Languages | Swahili and English | English |
| Regional Trade Context | EAC and SADC | COMESA and SADC |

The application uses these inputs to illustrate how differences and shared regional arrangements can be surfaced in a launch brief.

**Important:** These figures and country details are demonstration inputs from the project's country dossiers. They should be independently checked against current official sources before being relied upon for actual business decisions.

## 6. How It Works

1. **Select countries:** Choose the source and destination countries.
2. **Select a sector:** Specify the business sector, such as agritech.
3. **Load country dossiers:** The application reads the relevant Markdown regulatory information.
4. **Compare information:** The system identifies differences and shared characteristics.
5. **Generate the launch brief:** Relevant findings are organized into sections.
6. **Review verification flags:** Check items requiring confirmation before proceeding.

## 7. Technology Stack

The project uses:

- **React** – User interface development.
- **TypeScript** – Application logic and type safety.
- **Vite** – Development server and build tooling.
- **Markdown** – Country regulatory dossier format.
- **Node.js** – Development environment and supporting tooling.

## 8. Project Structure

```text
Cross-Border-Navigator/
├── africa-regulatory/
│   ├── tanzania.md
│   └── zambia.md
├── src/
│   ├── components/
│   │   ├── BriefOverviewStrip.tsx
│   │   ├── BriefSections.tsx
│   │   ├── DossierDrawer.tsx
│   │   ├── ImportDossierModal.tsx
│   │   ├── RouteControlBar.tsx
│   │   ├── SourceTag.tsx
│   │   └── VerifyFirstPanel.tsx
│   ├── lib/
│   │   ├── dossierParser.ts
│   │   ├── launchBrief.test.ts
│   │   ├── launchBrief.ts
│   │   └── types.ts
│   ├── App.tsx
│   ├── index.css
│   └── main.tsx
├── index.html
├── package.json
├── package-lock.json
├── server.ts
├── tsconfig.json
└── vite.config.ts
```

## 9. Getting Started

### Prerequisites

Install:
- Node.js
- npm

### Installation

Clone the repository:

```bash
git clone https://github.com/Kijani-Support/IBMxMCStudioProgram.git
```

Navigate to the application directory:

```bash
cd "IBMxMCStudioProgram/Dev Day Challenge/Group 4/Cross-Border-Navigator"
```

Install dependencies:

```bash
npm install
```

### Run the Development Server

```bash
npm run dev
```

Open the local URL displayed in your terminal to access the application.

### Build for Production

```bash
npm run build
```

## 10. Potential Users

Cross-Border Navigator is designed to support:
- Agritech startups expanding into new African markets.
- Small and medium-sized enterprises.
- Business development and market-entry teams.
- Trade and investment support organizations.
- Consultants conducting preliminary regulatory research.

## 11. Future Improvements

Potential next steps include:

- Expanding the country dossier library to cover more African markets.
- Integrating official government and regulatory data sources.
- Adding source links, publication dates, and verification timestamps.
- Improving automated regulatory change monitoring.
- Supporting additional sectors beyond agritech.
- Exporting launch briefs into PDF and other business-ready formats.
- Introducing user accounts and saved market-entry assessments.

## 12. Disclaimer

Cross-Border Navigator is a market-entry research and planning aid. It does not replace professional legal, tax, customs, or regulatory advice.

Regulatory requirements, tax rates, licensing rules, and trade arrangements may change. Users should verify all relevant information with the appropriate government agencies, regulators, and qualified professionals before making business decisions.

## 13. Acknowledgement

Developed by **Group 4** for the **IBM Dev Day Challenge**.

**Cross-Border Navigator – Making African Market Expansion Easier to Understand.**