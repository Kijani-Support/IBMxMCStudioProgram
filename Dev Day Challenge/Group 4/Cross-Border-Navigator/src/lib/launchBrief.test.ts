import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { parseDossierMarkdown } from './dossierParser';
import { buildLaunchBrief, exportBriefToMarkdown } from './launchBrief';

const tanzaniaRaw = fs.readFileSync(
  path.resolve(process.cwd(), 'africa-regulatory/tanzania.md'),
  'utf-8',
);
const zambiaRaw = fs.readFileSync(
  path.resolve(process.cwd(), 'africa-regulatory/zambia.md'),
  'utf-8',
);

test('parses Tanzania and Zambia dossiers directly from markdown with source citations', () => {
  const tz = parseDossierMarkdown(tanzaniaRaw, 'tanzania.md');
  const zm = parseDossierMarkdown(zambiaRaw, 'zambia.md');

  assert.equal(tz.countryName, 'Tanzania');
  assert.equal(tz.overview.capital.value, 'Dodoma');
  assert.equal(tz.overview.capital.source.file, 'tanzania.md');
  assert.deepEqual(tz.overview.regionalBlocs.value, ['African Union', 'EAC', 'SADC']);
  assert.deepEqual(tz.overview.officialLanguages.value, ['Swahili', 'English']);
  assert.equal(tz.centralBank.name, 'Bank of Tanzania');
  assert.equal(tz.tax.corporateTaxRate, 30);
  assert.equal(tz.tax.vatRate, 18);

  assert.equal(zm.countryName, 'Zambia');
  assert.equal(zm.overview.capital.value, 'Lusaka');
  assert.deepEqual(zm.overview.regionalBlocs.value, ['African Union', 'SADC', 'COMESA']);
  assert.deepEqual(zm.overview.officialLanguages.value, ['English']);
  assert.equal(zm.centralBank.name, 'Bank of Zambia');
  assert.equal(zm.tax.corporateTaxRate, 30);
  assert.equal(zm.tax.vatRate, 16);
  assert.equal(zm.tax.corporateTaxNote, '35% mining');
});

test('builds complete Group 4 Agritech brief (Tanzania -> Zambia) with deltas and blocs', () => {
  const tz = parseDossierMarkdown(tanzaniaRaw, 'tanzania.md');
  const zm = parseDossierMarkdown(zambiaRaw, 'zambia.md');
  const brief = buildLaunchBrief(tz, zm, 'Agritech');

  assert.equal(brief.taxes.vat.deltaPp, -2);
  assert.equal(brief.taxes.corporateTax.deltaPp, 0);
  assert.equal(brief.languages.differs, true);
  assert.deepEqual(brief.languages.sharedOfficial, ['English']);
  assert.deepEqual(brief.languages.droppedOfficial, ['Swahili']);
  assert.deepEqual(brief.blocs.sharedBlocs, ['African Union', 'SADC']);
  assert.deepEqual(brief.blocs.homeOnlyBlocs, ['EAC']);
  assert.deepEqual(brief.blocs.targetOnlyBlocs, ['COMESA']);
  assert.equal(brief.compliance.targetSteps.length, 3);
  assert.match(brief.compliance.targetSteps[0], /Ministry of Agriculture/i);
});

test('verify-first auditor catches real template mistakes across both dossiers', () => {
  const tz = parseDossierMarkdown(tanzaniaRaw, 'tanzania.md');
  const zm = parseDossierMarkdown(zambiaRaw, 'zambia.md');
  const brief = buildLaunchBrief(tz, zm, 'Agritech');

  const ids = brief.verifyFlags.map((f) => f.id);
  assert.ok(ids.includes('zambia-bloc-mismatch'), 'Should catch Zambia WAEMU/ECOWAS/EAC mismatch');
  assert.ok(ids.includes('tanzania-bloc-mismatch'), 'Should catch Tanzania WAEMU/ECOWAS mismatch');
  assert.ok(ids.includes('tanzania-fintech-pct-bleed'), 'Should catch Tanzania 18% VAT bleed in Fintech');
  assert.ok(ids.includes('zambia-fintech-pct-bleed'), 'Should catch Zambia 16% VAT bleed in Fintech');
  assert.ok(ids.includes('tanzania-fintech-wrong-regulator'), 'Should catch PDPC listed for payments licensing');
  assert.ok(ids.includes('zambia-fintech-wrong-regulator'), 'Should catch ZICTA listed for payments licensing');
  assert.ok(ids.includes('tanzania-energy-cit-bleed'), 'Should catch 30% CIT bleed in Energy');
  assert.ok(ids.includes('zambia-Agritech-unnamed-agency'), 'Should catch unnamed Agritech statutory agency');
});

test('parses arbitrary non-hardcoded dossier with tab-separated tables', () => {
  const customMd = `Cameroon — Regulatory, Compliance and Tax Dossier
Author: Modus Chora Studio · Status: planning reference, verify before acting · Updated: 2026-07-31

1. Overview
Field\tValue
Capital\tYaoundé
Currency\tCentral African CFA franc (XAF)
Regional blocs\tAfrican Union; CEMAC; ECCAS
Official languages\tFrench, English
Dominant spoken languages\tFrench, English, Ewondo

2. Central bank and financial regulation
Central bank: Bank of Central African States (BEAC).

Data protection: ANTIC (verify).

3. Energy sector
Regulator / authority: ARSEL.

4. Sector compliance steps
Sector\tPrimary compliance steps
Agritech\tMINADER phytosanitary permit; land lease clearance; customs declaration.

5. Tax planning
Item\tValue
Standard corporate income tax\t33%
Standard VAT / sales tax\t19.25%
Investment promotion agency: API Cameroon. Incentives: Investment charter.
Tax-planning considerations: Verify OHADA rules.`;

  const cm = parseDossierMarkdown(customMd, 'cameroon.md');
  const zm = parseDossierMarkdown(zambiaRaw, 'zambia.md');
  const brief = buildLaunchBrief(cm, zm, 'Agritech');

  assert.equal(cm.countryName, 'Cameroon');
  assert.equal(cm.tax.corporateTaxRate, 33);
  assert.equal(cm.tax.vatRate, 19.25);
  assert.equal(brief.taxes.vat.deltaPp, -3.25);
  assert.equal(brief.taxes.corporateTax.deltaPp, -3);
  const md = exportBriefToMarkdown(brief);
  assert.match(md, /cameroon\.md/);
  assert.match(md, /zambia\.md/);
});
