import {
  CountryDossier,
  LaunchBrief,
  RegulatorComparisonRow,
  SectorName,
  VerifyFlag,
} from './types';

const KNOWN_BLOC_TOKENS = [
  'WAEMU',
  'UEMOA',
  'ECOWAS',
  'EAC',
  'SADC',
  'COMESA',
  'CEMAC',
  'IGAD',
  'ECCAS',
  'AMU',
  'UMA',
];

function normalizeBlocToken(bloc: string): string {
  return bloc.trim().toUpperCase();
}

function getBlocsInText(text: string): string[] {
  const upper = text.toUpperCase();
  return KNOWN_BLOC_TOKENS.filter((token) =>
    new RegExp(`\\b${token}\\b`, 'i').test(upper),
  );
}

export function cleanAuthorityName(raw: string): string {
  return raw
    .replace(/;\s*verify[^)]*\)/gi, ')')
    .replace(/;\s*verify.*$/i, '')
    .replace(/\(\s*\)/g, '')
    .trim();
}

export function auditSingleDossier(
  dossier: CountryDossier,
  activeSector: SectorName,
): VerifyFlag[] {
  const flags: VerifyFlag[] = [];
  const file = dossier.fileName;
  const country = dossier.countryName;

  // 1. Check Section 4 Fintech for VAT/Tax percentage bleed & wrong licensing authority
  const fintechEntry = dossier.sectorCompliance['Fintech'];
  if (fintechEntry) {
    const pctMatch = fintechEntry.rawText.match(/data protection registration\s*\((\d+(?:\.\d+)?)%\)/i);
    if (pctMatch) {
      const leakedPct = Number(pctMatch[1]);
      const matchesVat = dossier.tax.vatRate !== null && leakedPct === dossier.tax.vatRate;
      flags.push({
        id: `${dossier.id}-fintech-pct-bleed`,
        country,
        fileName: file,
        severity: 'critical',
        category: 'template-bleed',
        sectorScope: 'Fintech',
        title: `VAT rate (${leakedPct}%) leaked into Fintech data protection registration`,
        explanation: matchesVat
          ? `Section 4 writes "data protection registration (${leakedPct}%)", which matches ${country}'s Standard VAT rate (${dossier.tax.vatRaw} in §5). Data protection registration is not a ${leakedPct}% turnover/VAT tax.`
          : `Section 4 writes "data protection registration (${leakedPct}%)", an unexplained percentage likely injected by template variable substitution.`,
        recommendation: `Verify actual statutory registration fees with ${cleanAuthorityName(dossier.dataProtection.name)} rather than budgeting ${leakedPct}%.`,
        source: fintechEntry.source,
      });
    }

    const dpCoreName = dossier.dataProtection.name.split(/[;(]/)[0].trim();
    if (
      dpCoreName &&
      dpCoreName !== 'Not specified' &&
      fintechEntry.rawText.toLowerCase().includes(dpCoreName.toLowerCase()) &&
      /licensing for payments and lending/i.test(fintechEntry.rawText)
    ) {
      flags.push({
        id: `${dossier.id}-fintech-wrong-regulator`,
        country,
        fileName: file,
        severity: 'critical',
        category: 'wrong-regulator',
        sectorScope: 'Fintech',
        title: `Data protection body (${dpCoreName}) listed for Fintech payments/lending licensing`,
        explanation: `Section 4 names "${dpCoreName}" for "licensing for payments and lending", contradicting Section 2 which states that ${dossier.centralBank.name} is the central bank responsible for payment and lending licensing.`,
        recommendation: `Engage ${dossier.centralBank.name} for payment/lending licenses and ${dpCoreName} separately for data protection compliance.`,
        source: fintechEntry.source,
      });
    }
  }

  // 2. Check Section 4 Energy & manufacturing for Corporate Tax percentage bleed
  const energyEntry = dossier.sectorCompliance['Energy & manufacturing'];
  if (energyEntry) {
    const energyLeakMatch = energyEntry.rawText.match(/Energy regulator:\s*(\d+(?:\.\d+)?%[^;]*)/i);
    if (energyLeakMatch) {
      flags.push({
        id: `${dossier.id}-energy-cit-bleed`,
        country,
        fileName: file,
        severity: 'critical',
        category: 'template-bleed',
        sectorScope: 'Energy & manufacturing',
        title: `Corporate tax rate (${energyLeakMatch[1].trim()}) substituted for Energy regulator name`,
        explanation: `Section 4 states "Energy regulator: ${energyLeakMatch[1].trim()}", which is ${country}'s corporate income tax value from Section 5 (${dossier.tax.corporateTaxRaw}) instead of Section 3's named authority (${dossier.energySector.regulator}).`,
        recommendation: `Use ${dossier.energySector.regulator} (from §3) as the energy regulator and treat ${energyLeakMatch[1].trim()} strictly as corporate tax (§5).`,
        source: energyEntry.source,
      });
    }
  }

  // 3. Check Section 2 regional harmonisation boilerplate vs Section 1 declared blocs
  if (dossier.regionalHarmonisationNote) {
    const mentionedBlocs = getBlocsInText(dossier.regionalHarmonisationNote.value);
    const declaredBlocs = dossier.overview.regionalBlocs.value.map(normalizeBlocToken);
    const mismatched = mentionedBlocs.filter((b) => !declaredBlocs.includes(b));
    if (mismatched.length > 0) {
      flags.push({
        id: `${dossier.id}-bloc-mismatch`,
        country,
        fileName: file,
        severity: 'critical',
        category: 'bloc-mismatch',
        sectorScope: 'All',
        title: `Section 2 cites regional blocs (${mismatched.join(', ')}) that ${country} does not belong to`,
        explanation: `Section 2 references "${mismatched.join('/')}" harmonisation, but Section 1 lists ${country}'s actual blocs as: ${dossier.overview.regionalBlocs.value.join(', ')}. This is unedited regional boilerplate.`,
        recommendation: `Ignore ${mismatched.join('/')} framework claims for ${country}; verify rules strictly under ${dossier.overview.regionalBlocs.value.join(', ')}.`,
        source: dossier.regionalHarmonisationNote.source,
      });
    }
  }

  // 4. Check generic / unnamed statutory authorities in Section 4 (especially for Agritech, Healthtech, Edtech, Retail)
  const activeCompliance = dossier.sectorCompliance[activeSector];
  if (activeCompliance) {
    const genericPatterns = [
      { regex: /Ministry of Agriculture and plant-health authority/i, label: 'unnamed Ministry of Agriculture & plant-health authority' },
      { regex: /Ministry of Health\b/i, label: 'generic Ministry of Health / medicines board' },
      { regex: /Ministry of Education\b/i, label: 'generic Ministry of Education' },
      { regex: /National revenue authority/i, label: 'unnamed national revenue authority & consumer-protection authority' },
    ];
    for (const pat of genericPatterns) {
      if (pat.regex.test(activeCompliance.rawText)) {
        flags.push({
          id: `${dossier.id}-${activeSector}-unnamed-agency`,
          country,
          fileName: file,
          severity: 'warning',
          category: 'incomplete-agency',
          sectorScope: activeSector,
          title: `${activeSector} regulator is a generic placeholder (${pat.label})`,
          explanation: `Unlike Central Bank (§2) or Energy (§3), Section 4 does not name ${country}'s actual statutory ${activeSector.toLowerCase()} agencies, permit categories, or fee schedules.`,
          recommendation: `Confirm the exact statutory agency name, phytosanitary/sector permit fees, and timelines with ${dossier.tax.investmentAgency.value} or local counsel before filing.`,
          source: activeCompliance.source,
        });
        break;
      }
    }
  }

  // 5. Check explicit "verify" markers in Data Protection & Tax considerations
  if (/verify/i.test(dossier.dataProtection.rawText)) {
    flags.push({
      id: `${dossier.id}-dp-verify`,
      country,
      fileName: file,
      severity: 'warning',
      category: 'verify-marker',
      sectorScope: 'All',
      title: `Data protection authority status unconfirmed (${dossier.dataProtection.name})`,
      explanation: `Section 2 explicitly flags "${dossier.dataProtection.name}" and warns to confirm the current regulator and registration thresholds before launching.`,
      recommendation: `Confirm whether registration thresholds apply to your customer/farmer data workflows in ${country}.`,
      source: dossier.dataProtection.source,
    });
  }

  if (/verify per treaty|where enacted|verify against/i.test(dossier.tax.considerations.value)) {
    flags.push({
      id: `${dossier.id}-tax-treaty-generic`,
      country,
      fileName: file,
      severity: 'info',
      category: 'verify-marker',
      sectorScope: 'All',
      title: `Withholding tax (5–15%) & digital-service tax rules are generic ranges`,
      explanation: `Section 5 provides a generic "commonly 5–15%, verify per treaty" range and mentions "digital-service taxes where enacted" without ${country}-specific statutory rates.`,
      recommendation: `Verify actual ${country} dividend/service withholding rates and any bilateral tax treaty before structuring cross-border invoicing.`,
      source: dossier.tax.considerations.source,
    });
  }

  // 6. Citation key playbook bleed
  if (
    dossier.citationKey &&
    /Energy Playbook/i.test(dossier.citationKey.value) &&
    activeSector !== 'Energy & manufacturing'
  ) {
    flags.push({
      id: `${dossier.id}-citation-energy-playbook`,
      country,
      fileName: file,
      severity: 'info',
      category: 'citation-bleed',
      sectorScope: 'All',
      title: `Dossier citation key references "Sita Sector Energy Playbook"`,
      explanation: `The header citation line instructs citing this file in the "Sita Sector Energy Playbook", confirming the underlying template originated from an energy-focused draft.`,
      recommendation: `Treat non-energy sector rows in §4 as baseline scaffolding requiring primary verification.`,
      source: dossier.citationKey.source,
    });
  }

  return flags;
}

function buildSectorFounderAction(
  sector: SectorName,
  home: CountryDossier,
  target: CountryDossier,
): string {
  const targetEntry = target.sectorCompliance[sector];
  if (sector === 'Fintech') {
    return `Engage ${target.centralBank.name} for payment/lending licensing (do not rely on §4's data-protection swap).`;
  }
  if (sector === 'Energy & manufacturing') {
    return `Engage ${target.energySector.regulator} (§3) for generation/licensing thresholds rather than §4's CIT figure.`;
  }
  if (sector === 'Agritech') {
    return `Identify ${target.countryName}'s exact national agriculture & phytosanitary authority before moving produce across the border.`;
  }
  if (sector === 'Healthtech') {
    return `Confirm Ministry of Health and national medicines/pharmacy board approvals in ${target.countryName}.`;
  }
  if (sector === 'Edtech') {
    return `Verify curriculum accreditation and minors' data protection rules in ${target.countryName}.`;
  }
  if (targetEntry) {
    return `Engage ${targetEntry.firstLineRegulator} and ${target.countryName}'s national revenue/consumer authorities.`;
  }
  return `Confirm primary sector regulator in ${target.countryName} (home baseline: ${home.countryName}).`;
}

function formatDeltaSummary(
  homeRate: number | null,
  targetRate: number | null,
  metricLabel: string,
): { deltaPp: number | null; summary: string } {
  if (homeRate === null || targetRate === null) {
    return { deltaPp: null, summary: 'Compare raw dossier rates (non-numeric)' };
  }
  const diff = Number((targetRate - homeRate).toFixed(2));
  if (diff === 0) {
    return { deltaPp: 0, summary: `Same headline ${metricLabel} rate (0 pp difference)` };
  }
  const sign = diff > 0 ? '+' : '';
  const direction = diff > 0 ? 'higher' : 'lower';
  return {
    deltaPp: diff,
    summary: `${sign}${diff} pp (${Math.abs(diff)} percentage points ${direction} in target)`,
  };
}

export function buildLaunchBrief(
  home: CountryDossier,
  target: CountryDossier,
  sector: SectorName,
): LaunchBrief {
  const homeSec = home.sectorCompliance[sector];
  const targetSec = target.sectorCompliance[sector];

  // Determine accurate sector regulator name (resolving template swaps for Fintech/Energy while citing source)
  const resolveSectorRegulator = (d: CountryDossier) => {
    if (sector === 'Fintech') {
      return {
        name: `${d.centralBank.name} (Central Bank; §4 erroneously lists DP body)`,
        detail: d.sectorCompliance['Fintech']?.rawText || d.centralBank.rawText,
        source: d.centralBank.source,
      };
    }
    if (sector === 'Energy & manufacturing') {
      return {
        name: d.energySector.regulator,
        detail: d.energySector.rawText,
        source: d.energySector.source,
      };
    }
    const entry = d.sectorCompliance[sector];
    return {
      name: entry ? entry.firstLineRegulator : 'Not specified in dossier',
      detail: entry ? entry.rawText : 'No compliance steps found for this sector',
      source: entry ? entry.source : d.centralBank.source,
    };
  };

  const homeSectorReg = resolveSectorRegulator(home);
  const targetSectorReg = resolveSectorRegulator(target);

  const regulators: RegulatorComparisonRow[] = [
    {
      role: 'Central Bank & Financial',
      homeName: home.centralBank.name,
      homeDetail: home.centralBank.rawText,
      homeSource: home.centralBank.source,
      targetName: target.centralBank.name,
      targetDetail: target.centralBank.rawText,
      targetSource: target.centralBank.source,
      founderAction:
        home.centralBank.name === target.centralBank.name
          ? `Shared regional central bank (${target.centralBank.name}) — verify cross-border passporting rules.`
          : `Separate central bank jurisdiction (${target.centralBank.name}); plan FX repatriation & payment rules for ${target.overview.currency.value}.`,
    },
    {
      role: 'Data Protection Authority',
      homeName: home.dataProtection.name,
      homeDetail: home.dataProtection.rawText,
      homeSource: home.dataProtection.source,
      targetName: target.dataProtection.name,
      targetDetail: target.dataProtection.rawText,
      targetSource: target.dataProtection.source,
      founderAction: `Confirm registration thresholds and operational status with ${cleanAuthorityName(target.dataProtection.name)} before collecting user data.`,
    },
    {
      role: `Sector Regulator (${sector})`,
      homeName: homeSectorReg.name,
      homeDetail: homeSectorReg.detail,
      homeSource: homeSectorReg.source,
      targetName: targetSectorReg.name,
      targetDetail: targetSectorReg.detail,
      targetSource: targetSectorReg.source,
      founderAction: buildSectorFounderAction(sector, home, target),
    },
    {
      role: 'Investment Promotion Agency',
      homeName: home.tax.investmentAgency.value,
      homeDetail: `Incentives: ${home.tax.incentives.value.join('; ') || 'See dossier'}`,
      homeSource: home.tax.investmentAgency.source,
      targetName: target.tax.investmentAgency.value,
      targetDetail: `Incentives: ${target.tax.incentives.value.join('; ') || 'See dossier'}`,
      targetSource: target.tax.investmentAgency.source,
      founderAction: `Contact ${target.tax.investmentAgency.value} early for subsidiary registration and incentive eligibility.`,
    },
  ];

  // Compliance checklist
  const targetSteps = targetSec?.steps ?? [];
  const homeSteps = homeSec?.steps ?? [];
  const founderChecklist = targetSteps.map((step) => {
    const isCrossBorder = /cross-border|export|customs|phytosanitary/i.test(step);
    const isGenericAuthority = /Ministry|authority|bureau|board|regulator/i.test(step);
    return {
      step,
      status: isCrossBorder
        ? ('cross-border' as const)
        : isGenericAuthority
          ? ('verify-authority' as const)
          : ('new-requirement' as const),
      source: targetSec.source,
    };
  });

  // Tax deltas
  const citDelta = formatDeltaSummary(
    home.tax.corporateTaxRate,
    target.tax.corporateTaxRate,
    'corporate tax',
  );
  const vatDelta = formatDeltaSummary(home.tax.vatRate, target.tax.vatRate, 'VAT');

  // Languages
  const homeOff = home.overview.officialLanguages.value;
  const targetOff = target.overview.officialLanguages.value;
  const sharedOfficial = homeOff.filter((l) =>
    targetOff.some((t) => t.toLowerCase() === l.toLowerCase()),
  );
  const droppedOfficial = homeOff.filter(
    (l) => !targetOff.some((t) => t.toLowerCase() === l.toLowerCase()),
  );
  const addedOfficial = targetOff.filter(
    (l) => !homeOff.some((h) => h.toLowerCase() === l.toLowerCase()),
  );
  const differs = droppedOfficial.length > 0 || addedOfficial.length > 0;

  let shiftSummary = 'Identical official business languages';
  if (differs) {
    if (sharedOfficial.length > 0 && addedOfficial.length === 0) {
      shiftSummary = `Narrows to ${targetOff.join(', ')} (${droppedOfficial.join(', ')} not official in target)`;
    } else if (sharedOfficial.length > 0) {
      shiftSummary = `Partial overlap (${sharedOfficial.join(', ')}); new official language: ${addedOfficial.join(', ')}`;
    } else {
      shiftSummary = `Complete language shift: ${homeOff.join(', ')} → ${targetOff.join(', ')}`;
    }
  }

  const operationalImpact =
    sharedOfficial.length > 0 && droppedOfficial.length > 0
      ? `Your ${sharedOfficial.join('/')} commercial contracts, corporate filings, and B2B terms transfer directly to ${target.countryName}. However, ${droppedOfficial.join('/')} regulatory filings, consumer/farmer contracts, or product labels used in ${home.countryName} do not have official status in ${target.countryName}; consider local translation into ${target.overview.dominantSpokenLanguages.value.filter((l) => !targetOff.includes(l)).slice(0, 3).join(', ')} for field adoption.`
      : sharedOfficial.length === 0
        ? `No shared official language between ${home.countryName} (${homeOff.join(', ')}) and ${target.countryName} (${targetOff.join(', ')}). Expect full legal translation of incorporation docs, contracts, regulatory submissions, and product labels.`
        : `Both ${home.countryName} and ${target.countryName} operate officially in ${sharedOfficial.join(', ')}. Legal documentation and regulatory filings do not require official-language translation.`;

  // Regional Blocs
  const homeBlocs = home.overview.regionalBlocs.value;
  const targetBlocs = target.overview.regionalBlocs.value;
  const sharedBlocs = homeBlocs.filter((b) =>
    targetBlocs.some((t) => normalizeBlocToken(t) === normalizeBlocToken(b)),
  );
  const homeOnlyBlocs = homeBlocs.filter(
    (b) => !targetBlocs.some((t) => normalizeBlocToken(t) === normalizeBlocToken(b)),
  );
  const targetOnlyBlocs = targetBlocs.filter(
    (b) => !homeBlocs.some((h) => normalizeBlocToken(h) === normalizeBlocToken(b)),
  );

  const nonAuShared = sharedBlocs.filter((b) => !/african union/i.test(b));
  const nonAuHomeOnly = homeOnlyBlocs.filter((b) => !/african union/i.test(b));
  const nonAuTargetOnly = targetOnlyBlocs.filter((b) => !/african union/i.test(b));

  const corridorSummary =
    nonAuShared.length > 0
      ? `${nonAuHomeOnly.length > 0 ? nonAuHomeOnly.join('/') + ' → ' : ''}Shared ${nonAuShared.join(', ')}${nonAuTargetOnly.length > 0 ? ' · Target also in ' + nonAuTargetOnly.join('/') : ''}`
      : `No shared sub-regional trade bloc (${homeBlocs.join(', ')} vs ${targetBlocs.join(', ')})`;

  const blocImplications: LaunchBrief['blocs']['implications'] = [];

  if (nonAuShared.length > 0) {
    blocImplications.push({
      kind: 'shared',
      title: `Shared framework: ${nonAuShared.join(', ')}`,
      detail:
        sector === 'Agritech'
          ? `Both ${home.countryName} and ${target.countryName} belong to ${nonAuShared.join(', ')}. Regional customs tariff preferences, sanitary/phytosanitary (SPS) harmonization, and cross-border agricultural corridor protocols under ${nonAuShared.join(', ')} are your primary legal lever—verify certificate-of-origin eligibility.`
          : `Both ${home.countryName} and ${target.countryName} sit inside ${nonAuShared.join(', ')}, creating a shared framework for customs duties, cross-border data flows, and professional recognition (§6).`,
    });
  } else {
    blocImplications.push({
      kind: 'exit',
      title: `No shared sub-regional trade bloc`,
      detail: `${home.countryName} (${homeBlocs.join(', ')}) and ${target.countryName} (${targetBlocs.join(', ')}) share only the continental African Union umbrella. Expect standard third-country tariffs, import permits, and separate local compliance.`,
    });
  }

  if (nonAuHomeOnly.length > 0) {
    blocImplications.push({
      kind: 'exit',
      title: `Leaving ${nonAuHomeOnly.join(', ')} jurisdiction`,
      detail: `${target.countryName} is NOT a member of ${nonAuHomeOnly.join(', ')}. Any ${nonAuHomeOnly.join('/')} regional permits, customs-union exemptions, or mutual-recognition licenses from ${home.countryName} stop at the border.`,
    });
  }

  if (nonAuTargetOnly.length > 0) {
    blocImplications.push({
      kind: 'entry',
      title: `Entering ${nonAuTargetOnly.join(', ')} market`,
      detail: `${target.countryName} participates in ${nonAuTargetOnly.join(', ')} (which ${home.countryName} does not). Establishing a local subsidiary in ${target.countryName} can unlock ${nonAuTargetOnly.join('/')} regional trade access, but requires meeting ${nonAuTargetOnly.join('/')} rules of origin.`,
    });
  }

  // Combine single-dossier audits + bilateral cross-border check
  const homeFlags = auditSingleDossier(home, sector);
  const targetFlags = auditSingleDossier(target, sector);
  const bilateralFlags: VerifyFlag[] = [];

  if (nonAuHomeOnly.length > 0 && nonAuTargetOnly.length > 0 && nonAuShared.length > 0) {
    bilateralFlags.push({
      id: `bilateral-${home.id}-${target.id}-overlap`,
      country: `${home.countryName} → ${target.countryName}`,
      fileName: `${home.fileName} · ${target.fileName}`,
      severity: 'warning',
      category: 'cross-border-gap',
      sectorScope: 'All',
      title: `Overlapping bloc split (${nonAuHomeOnly.join('/')} vs ${nonAuTargetOnly.join('/')}; shared ${nonAuShared.join('/')})`,
      explanation: `Moving from ${home.countryName} to ${target.countryName} crosses out of ${nonAuHomeOnly.join('/')} into ${nonAuTargetOnly.join('/')}, with only ${nonAuShared.join('/')} in common. Section 6 does not specify which bloc's customs/SPS regime governs bilateral shipments.`,
      recommendation:
        sector === 'Agritech'
          ? `Declare produce exports under ${nonAuShared.join('/')} Certificate of Origin & SPS protocols rather than ${nonAuHomeOnly.join('/')} rules so customs clearance at the border isn't rejected.`
          : `Confirm whether your target entity leverages ${nonAuShared.join('/')} protocols vs bilateral customs rules.`,
      source: target.overview.regionalBlocs.source,
    });
  }

  const severityOrder = { critical: 0, warning: 1, info: 2 };
  const verifyFlags = [...homeFlags, ...targetFlags, ...bilateralFlags].sort((a, b) => {
    const aMatchesSector = a.sectorScope === sector || a.sectorScope === 'All' ? 0 : 1;
    const bMatchesSector = b.sectorScope === sector || b.sectorScope === 'All' ? 0 : 1;
    if (aMatchesSector !== bMatchesSector) return aMatchesSector - bMatchesSector;
    return severityOrder[a.severity] - severityOrder[b.severity];
  });

  return {
    home,
    target,
    sector,
    regulators,
    compliance: {
      homeSteps,
      homeRaw: homeSec?.rawText || 'Not specified',
      homeSource: homeSec?.source || home.centralBank.source,
      targetSteps,
      targetRaw: targetSec?.rawText || 'Not specified',
      targetSource: targetSec?.source || target.centralBank.source,
      targetRegulator: targetSectorReg.name,
      preambleWarning: target.sectorPreamble?.value || null,
      preambleSource: target.sectorPreamble?.source,
      founderChecklist,
    },
    taxes: {
      corporateTax: {
        homeRaw: home.tax.corporateTaxRaw,
        homeRate: home.tax.corporateTaxRate,
        homeSource: home.tax.corporateTaxSource,
        targetRaw: target.tax.corporateTaxRaw,
        targetRate: target.tax.corporateTaxRate,
        targetNote: target.tax.corporateTaxNote,
        targetSource: target.tax.corporateTaxSource,
        deltaPp: citDelta.deltaPp,
        deltaSummary: citDelta.summary,
      },
      vat: {
        homeRaw: home.tax.vatRaw,
        homeRate: home.tax.vatRate,
        homeSource: home.tax.vatSource,
        targetRaw: target.tax.vatRaw,
        targetRate: target.tax.vatRate,
        targetNote: target.tax.vatNote,
        targetSource: target.tax.vatSource,
        deltaPp: vatDelta.deltaPp,
        deltaSummary: vatDelta.summary,
      },
      investmentAgency: {
        home: home.tax.investmentAgency,
        target: target.tax.investmentAgency,
      },
      incentives: {
        home: home.tax.incentives,
        target: target.tax.incentives,
      },
      considerations: {
        home: home.tax.considerations,
        target: target.tax.considerations,
      },
    },
    languages: {
      homeOfficial: home.overview.officialLanguages,
      targetOfficial: target.overview.officialLanguages,
      homeSpoken: home.overview.dominantSpokenLanguages,
      targetSpoken: target.overview.dominantSpokenLanguages,
      sharedOfficial,
      droppedOfficial,
      addedOfficial,
      differs,
      shiftSummary,
      operationalImpact,
      homeNoteSource: home.expansionNotes[0]?.source,
      targetNoteSource: target.expansionNotes[0]?.source,
    },
    blocs: {
      homeBlocs: home.overview.regionalBlocs,
      targetBlocs: target.overview.regionalBlocs,
      sharedBlocs,
      homeOnlyBlocs,
      targetOnlyBlocs,
      corridorSummary,
      implications: blocImplications,
      homeNoteSource: home.expansionNotes[1]?.source,
      targetNoteSource: target.expansionNotes[1]?.source,
    },
    verifyFlags,
  };
}

export function exportBriefToMarkdown(brief: LaunchBrief, aiSummary?: string | null): string {
  const { home, target, sector } = brief;
  const lines: string[] = [
    `# Cross-Border Launch Brief: ${home.countryName} → ${target.countryName} (${sector})`,
    ``,
    `> Planning reference generated directly from \`${home.fileName}\` and \`${target.fileName}\`. Not legal, tax, or financial advice.`,
    ``,
  ];

  if (aiSummary) {
    lines.push(`## Executive Plain-Language Summary`, ``, aiSummary.trim(), ``);
  }

  lines.push(
    `## 1. Regulators to Engage`,
    `| Role | ${home.countryName} (${home.fileName}) | ${target.countryName} (${target.fileName}) | Founder Action |`,
    `| --- | --- | --- | --- |`,
    ...brief.regulators.map(
      (r) =>
        `| ${r.role} | ${r.homeName} *(source: ${r.homeSource.file} ${r.homeSource.section})* | ${r.targetName} *(source: ${r.targetSource.file} ${r.targetSource.section})* | ${r.founderAction} |`,
    ),
    ``,
    `## 2. Sector Compliance Steps (${sector})`,
    `- **Target (${target.countryName})** *(source: ${brief.compliance.targetSource.file} ${brief.compliance.targetSource.section}, line ${brief.compliance.targetSource.line})*:`,
    ...brief.compliance.targetSteps.map((s, idx) => `  ${idx + 1}. ${s}`),
    `- **Home baseline (${home.countryName})** *(source: ${brief.compliance.homeSource.file} ${brief.compliance.homeSource.section}, line ${brief.compliance.homeSource.line})*: ${brief.compliance.homeRaw}`,
    ``,
    `## 3. Tax & Investment Differences`,
    `| Item | ${home.countryName} | ${target.countryName} | Difference |`,
    `| --- | --- | --- | --- |`,
    `| Corporate Income Tax | ${brief.taxes.corporateTax.homeRaw} *(${brief.taxes.corporateTax.homeSource.file} §5)* | ${brief.taxes.corporateTax.targetRaw} *(${brief.taxes.corporateTax.targetSource.file} §5)* | ${brief.taxes.corporateTax.deltaSummary} |`,
    `| Standard VAT / Sales Tax | ${brief.taxes.vat.homeRaw} *(${brief.taxes.vat.homeSource.file} §5)* | ${brief.taxes.vat.targetRaw} *(${brief.taxes.vat.targetSource.file} §5)* | ${brief.taxes.vat.deltaSummary} |`,
    `| Investment Agency | ${brief.taxes.investmentAgency.home.value} *(${brief.taxes.investmentAgency.home.source.file} §5)* | ${brief.taxes.investmentAgency.target.value} *(${brief.taxes.investmentAgency.target.source.file} §5)* | Register local entity / incentives |`,
    ``,
    `## 4. Language & Legal Operations`,
    `- **${home.countryName} official** *(${brief.languages.homeOfficial.source.file} §1)*: ${brief.languages.homeOfficial.value.join(', ')}`,
    `- **${target.countryName} official** *(${brief.languages.targetOfficial.source.file} §1)*: ${brief.languages.targetOfficial.value.join(', ')}`,
    `- **Assessment**: ${brief.languages.shiftSummary}. ${brief.languages.operationalImpact}`,
    ``,
    `## 5. Regional Blocs & Cross-Border Corridor`,
    `- **${home.countryName} blocs** *(${brief.blocs.homeBlocs.source.file} §1)*: ${brief.blocs.homeBlocs.value.join('; ')}`,
    `- **${target.countryName} blocs** *(${brief.blocs.targetBlocs.source.file} §1)*: ${brief.blocs.targetBlocs.value.join('; ')}`,
    `- **Corridor**: ${brief.blocs.corridorSummary}`,
    ...brief.blocs.implications.map((imp) => `- **${imp.title}**: ${imp.detail}`),
    ``,
    `## 6. "Verify First" Flags (Automated Dossier Audit)`,
    ...brief.verifyFlags.map(
      (f) =>
        `- **[${f.severity.toUpperCase()}] ${f.title}** *(${f.source.file} ${f.source.section}, line ${f.source.line})*: ${f.explanation} **Action**: ${f.recommendation}`,
    ),
  );

  return lines.join('\n');
}
