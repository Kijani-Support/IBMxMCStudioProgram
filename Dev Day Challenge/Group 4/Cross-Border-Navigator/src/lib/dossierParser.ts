import {
  CountryDossier,
  SectorComplianceEntry,
  SourceRef,
  SourcedValue,
} from './types';

function stripMarkdownFormatting(text: string): string {
  return text
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/\*([^*]+)\*/g, '$1')
    .replace(/`([^`]+)`/g, '$1')
    .trim();
}

function splitList(raw: string, delimiters: RegExp): string[] {
  return raw
    .split(delimiters)
    .map((item) => item.trim())
    .filter(Boolean);
}

function parsePercentage(raw: string): { rate: number | null; note: string | null } {
  const match = raw.match(/(\d+(?:\.\d+)?)\s*%/);
  if (!match) {
    return { rate: null, note: raw.trim() || null };
  }
  const rate = Number(match[1]);
  const remainder = raw.replace(match[0], '').replace(/^[\s\-–—]+/, '').trim();
  const parenMatch = raw.match(/\(([^)]+)\)/);
  const note = parenMatch ? parenMatch[1].trim() : remainder || null;
  return { rate: Number.isFinite(rate) ? rate : null, note };
}

function parseTableRow(line: string): [string, string] | null {
  const trimmed = line.trim();
  if (!trimmed) return null;

  // Pipe-delimited markdown table row
  if (trimmed.includes('|')) {
    // Skip separator rows like | --- | --- |
    if (/^\|?[\s:-]+\|[\s|:-]*$/.test(trimmed)) {
      return null;
    }
    const cells = trimmed
      .replace(/^\|/, '')
      .replace(/\|$/, '')
      .split('|')
      .map((c) => stripMarkdownFormatting(c));
    if (cells.length >= 2 && cells[0] && cells[1]) {
      return [cells[0], cells.slice(1).join(' | ').trim()];
    }
    return null;
  }

  // Tab-separated table row fallback
  if (trimmed.includes('\t')) {
    const cells = trimmed.split('\t').map((c) => stripMarkdownFormatting(c));
    if (cells.length >= 2 && cells[0] && cells[1]) {
      return [cells[0], cells.slice(1).join(' ').trim()];
    }
  }

  return null;
}

function extractFirstLineRegulator(sector: string, rawSteps: string): string {
  const normalizedSector = sector.toLowerCase();
  if (normalizedSector.includes('energy')) {
    const colonMatch = rawSteps.match(/^([^;]+)/);
    return colonMatch ? colonMatch[1].trim() : rawSteps;
  }
  if (normalizedSector.includes('fintech')) {
    const licensingMatch = rawSteps.match(/^(.*?)(?:\s+licensing\b|;)/i);
    return licensingMatch ? licensingMatch[1].trim() : rawSteps.split(';')[0]?.trim() || rawSteps;
  }
  const firstClause = rawSteps.split(';')[0]?.trim() || rawSteps;
  const approvalTrim = firstClause
    .replace(/\s+approval for products and services$/i, '')
    .replace(/\s+content and curriculum accreditation$/i, '')
    .trim();
  return approvalTrim || firstClause;
}

function makeSource(file: string, section: string, line: number, quote: string): SourceRef {
  return {
    file,
    section,
    line,
    quote: quote.trim(),
  };
}

export function parseDossierMarkdown(rawMarkdown: string, fileName: string): CountryDossier {
  const lines = rawMarkdown.split(/\r?\n/);
  const cleanFileName = fileName.split('/').pop() || fileName;

  let countryName = cleanFileName.replace(/\.md$/i, '');
  countryName = countryName.charAt(0).toUpperCase() + countryName.slice(1);

  let metadataLine: SourcedValue<string> | undefined;
  let updatedDate: SourcedValue<string> | undefined;
  let citationKey: SourcedValue<string> | undefined;

  let currentSection = 'Header';
  const sectionLines: Record<string, Array<{ line: number; text: string }>> = {};

  for (let i = 0; i < lines.length; i++) {
    const lineNum = i + 1;
    const raw = lines[i];
    const trimmed = raw.trim();
    if (!trimmed) continue;

    // Detect title line
    const titleMatch = trimmed.match(/^(?:#\s*)?(.+?)\s+[—–-]\s+Regulatory,\s*Compliance/i);
    if (titleMatch && currentSection === 'Header') {
      countryName = stripMarkdownFormatting(titleMatch[1]);
      continue;
    }

    // Detect numbered section heading: ## 1. Overview or 1. Overview
    const sectionMatch = trimmed.match(/^(?:#{1,3}\s*)?(\d+)\.\s+(.+)$/);
    if (sectionMatch) {
      currentSection = `§${sectionMatch[1]} ${stripMarkdownFormatting(sectionMatch[2])}`;
      sectionLines[currentSection] = sectionLines[currentSection] || [];
      continue;
    }

    if (currentSection === 'Header') {
      if (/^Author:/i.test(trimmed)) {
        metadataLine = {
          value: trimmed,
          source: makeSource(cleanFileName, 'Header', lineNum, trimmed),
        };
        const updMatch = trimmed.match(/Updated:\s*([0-9-]+)/i);
        if (updMatch) {
          updatedDate = {
            value: updMatch[1],
            source: makeSource(cleanFileName, 'Header', lineNum, trimmed),
          };
        }
      } else if (/^Citation key:/i.test(trimmed)) {
        citationKey = {
          value: trimmed.replace(/^Citation key:\s*/i, ''),
          source: makeSource(cleanFileName, 'Header', lineNum, trimmed),
        };
      }
    } else {
      sectionLines[currentSection] = sectionLines[currentSection] || [];
      sectionLines[currentSection].push({ line: lineNum, text: trimmed });
    }
  }

  const findSectionKey = (prefix: string): string | undefined =>
    Object.keys(sectionLines).find((k) => k.startsWith(prefix));

  const emptySource = (section: string): SourceRef =>
    makeSource(cleanFileName, section, 1, 'Not found in dossier');

  // --- Section 1: Overview ---
  const s1Key = findSectionKey('§1');
  const s1Lines = s1Key ? sectionLines[s1Key] : [];
  let capital: SourcedValue<string> = { value: 'Not specified', source: emptySource('§1 Overview') };
  let currency: SourcedValue<string> = { value: 'Not specified', source: emptySource('§1 Overview') };
  let regionalBlocs: SourcedValue<string[]> = { value: [], source: emptySource('§1 Overview') };
  let officialLanguages: SourcedValue<string[]> = { value: [], source: emptySource('§1 Overview') };
  let dominantSpokenLanguages: SourcedValue<string[]> = { value: [], source: emptySource('§1 Overview') };

  for (const item of s1Lines) {
    const row = parseTableRow(item.text);
    if (!row) continue;
    const [field, value] = row;
    const lower = field.toLowerCase();
    if (lower === 'field' && value.toLowerCase() === 'value') continue;

    const src = makeSource(cleanFileName, '§1 Overview', item.line, item.text);
    if (lower.includes('capital')) {
      capital = { value, source: src };
    } else if (lower.includes('currency')) {
      currency = { value, source: src };
    } else if (lower.includes('regional bloc')) {
      regionalBlocs = { value: splitList(value, /[;,]/), source: src };
    } else if (lower.includes('official language')) {
      officialLanguages = { value: splitList(value, /[,;]/), source: src };
    } else if (lower.includes('dominant spoken') || lower.includes('spoken language')) {
      dominantSpokenLanguages = { value: splitList(value, /[,;]/), source: src };
    }
  }

  // --- Section 2: Central bank and financial regulation ---
  const s2Key = findSectionKey('§2');
  const s2Lines = s2Key ? sectionLines[s2Key] : [];
  let centralBank = {
    name: 'Not specified',
    rawText: '',
    source: emptySource('§2 Central bank & financial regulation'),
  };
  let dataProtection = {
    name: 'Not specified',
    rawText: '',
    source: emptySource('§2 Central bank & financial regulation'),
  };
  let regionalHarmonisationNote: SourcedValue<string> | undefined;

  for (const item of s2Lines) {
    const clean = stripMarkdownFormatting(item.text);
    const src = makeSource(cleanFileName, '§2 Central bank & financial regulation', item.line, item.text);

    if (/^Central bank:/i.test(clean)) {
      const afterColon = clean.replace(/^Central bank:\s*/i, '');
      const firstSentence = afterColon.split('.')[0]?.trim() || afterColon;
      centralBank = {
        name: firstSentence,
        rawText: clean,
        source: src,
      };
      const harmonisationMatch = clean.match(/Cross-border digital services.*$/i);
      if (harmonisationMatch) {
        regionalHarmonisationNote = {
          value: harmonisationMatch[0],
          source: src,
        };
      }
    } else if (/^Data protection:/i.test(clean)) {
      const afterColon = clean.replace(/^Data protection:\s*/i, '');
      const namePart = afterColon.split(/\s+[—–-]\s+/)[0]?.trim() || afterColon;
      dataProtection = {
        name: namePart,
        rawText: clean,
        source: src,
      };
    }
  }

  // --- Section 3: Energy sector ---
  const s3Key = findSectionKey('§3');
  const s3Lines = s3Key ? sectionLines[s3Key] : [];
  let energySector = {
    regulator: 'Not specified',
    rawText: '',
    source: emptySource('§3 Energy sector'),
  };

  for (const item of s3Lines) {
    const clean = stripMarkdownFormatting(item.text);
    if (/^Regulator\s*\/\s*authority:/i.test(clean)) {
      const afterColon = clean.replace(/^Regulator\s*\/\s*authority:\s*/i, '');
      const regName = afterColon.split('.')[0]?.trim() || afterColon;
      energySector = {
        regulator: regName,
        rawText: clean,
        source: makeSource(cleanFileName, '§3 Energy sector', item.line, item.text),
      };
    }
  }

  // --- Section 4: Sector compliance steps ---
  const s4Key = findSectionKey('§4');
  const s4Lines = s4Key ? sectionLines[s4Key] : [];
  let sectorPreamble: SourcedValue<string> | undefined;
  const sectorCompliance: Record<string, SectorComplianceEntry> = {};

  for (const item of s4Lines) {
    const row = parseTableRow(item.text);
    if (!row) {
      if (!sectorPreamble && !item.text.startsWith('|')) {
        sectorPreamble = {
          value: stripMarkdownFormatting(item.text),
          source: makeSource(cleanFileName, '§4 Sector compliance steps', item.line, item.text),
        };
      }
      continue;
    }
    const [sectorCol, stepsCol] = row;
    if (sectorCol.toLowerCase() === 'sector' && stepsCol.toLowerCase().includes('compliance')) {
      continue;
    }
    const cleanSector = sectorCol.trim();
    const steps = stepsCol
      .replace(/\.$/, '')
      .split(';')
      .map((s) => s.trim())
      .filter(Boolean);

    sectorCompliance[cleanSector] = {
      sector: cleanSector,
      rawText: stepsCol,
      steps,
      firstLineRegulator: extractFirstLineRegulator(cleanSector, stepsCol),
      source: makeSource(cleanFileName, `§4 Sector compliance (${cleanSector})`, item.line, item.text),
    };
  }

  // --- Section 5: Tax planning ---
  const s5Key = findSectionKey('§5');
  const s5Lines = s5Key ? sectionLines[s5Key] : [];
  let corporateTaxRaw = 'Not specified';
  let corporateTaxRate: number | null = null;
  let corporateTaxNote: string | null = null;
  let corporateTaxSource = emptySource('§5 Tax planning');

  let vatRaw = 'Not specified';
  let vatRate: number | null = null;
  let vatNote: string | null = null;
  let vatSource = emptySource('§5 Tax planning');

  let investmentAgency: SourcedValue<string> = {
    value: 'Not specified',
    source: emptySource('§5 Tax planning'),
  };
  let incentives: SourcedValue<string[]> = {
    value: [],
    source: emptySource('§5 Tax planning'),
  };
  let considerations: SourcedValue<string> = {
    value: 'Not specified',
    source: emptySource('§5 Tax planning'),
  };

  for (const item of s5Lines) {
    const row = parseTableRow(item.text);
    if (row) {
      const [key, val] = row;
      const lower = key.toLowerCase();
      if (lower === 'item') continue;
      const src = makeSource(cleanFileName, '§5 Tax planning', item.line, item.text);
      if (lower.includes('corporate income tax')) {
        corporateTaxRaw = val;
        const parsed = parsePercentage(val);
        corporateTaxRate = parsed.rate;
        corporateTaxNote = parsed.note;
        corporateTaxSource = src;
      } else if (lower.includes('vat') || lower.includes('sales tax')) {
        vatRaw = val;
        const parsed = parsePercentage(val);
        vatRate = parsed.rate;
        vatNote = parsed.note;
        vatSource = src;
      }
      continue;
    }

    const clean = stripMarkdownFormatting(item.text);
    const src = makeSource(cleanFileName, '§5 Tax planning', item.line, item.text);
    if (/^Investment promotion agency:/i.test(clean)) {
      const agencyMatch = clean.match(/Investment promotion agency:\s*([^.]+)\.?/i);
      if (agencyMatch) {
        investmentAgency = { value: agencyMatch[1].trim(), source: src };
      }
      const incMatch = clean.match(/Incentives:\s*(.+)$/i);
      if (incMatch) {
        incentives = {
          value: splitList(incMatch[1].replace(/\.$/, ''), /;/),
          source: src,
        };
      }
    } else if (/^Tax-planning considerations:/i.test(clean)) {
      considerations = {
        value: clean.replace(/^Tax-planning considerations:\s*/i, ''),
        source: src,
      };
    }
  }

  // --- Section 6: Expansion notes ---
  const s6Key = findSectionKey('§6');
  const s6Lines = s6Key ? sectionLines[s6Key] : [];
  const expansionNotes: SourcedValue<string>[] = s6Lines.map((item) => ({
    value: stripMarkdownFormatting(item.text).replace(/^[-*]\s*/, ''),
    source: makeSource(cleanFileName, '§6 Expansion notes', item.line, item.text),
  }));

  return {
    id: cleanFileName.replace(/\.md$/i, '').toLowerCase(),
    fileName: cleanFileName,
    countryName,
    rawMarkdown,
    lineCount: lines.length,
    metadataLine,
    updatedDate,
    citationKey,
    overview: {
      capital,
      currency,
      regionalBlocs,
      officialLanguages,
      dominantSpokenLanguages,
    },
    centralBank,
    regionalHarmonisationNote,
    dataProtection,
    energySector,
    sectorPreamble,
    sectorCompliance,
    tax: {
      corporateTaxRaw,
      corporateTaxRate,
      corporateTaxNote,
      corporateTaxSource,
      vatRaw,
      vatRate,
      vatNote,
      vatSource,
      investmentAgency,
      incentives,
      considerations,
    },
    expansionNotes,
  };
}
