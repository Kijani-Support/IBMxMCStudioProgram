export const SECTORS = [
  'Agritech',
  'Fintech',
  'Healthtech',
  'Edtech',
  'Retail & ecommerce',
  'Energy & manufacturing',
] as const;

export type SectorName = (typeof SECTORS)[number];

export interface SourceRef {
  file: string;
  section: string;
  line: number;
  quote: string;
}

export interface SourcedValue<T> {
  value: T;
  source: SourceRef;
}

export interface SectorComplianceEntry {
  sector: string;
  rawText: string;
  steps: string[];
  firstLineRegulator: string;
  source: SourceRef;
}

export interface CountryDossier {
  id: string;
  fileName: string;
  countryName: string;
  rawMarkdown: string;
  lineCount: number;
  metadataLine?: SourcedValue<string>;
  updatedDate?: SourcedValue<string>;
  citationKey?: SourcedValue<string>;
  overview: {
    capital: SourcedValue<string>;
    currency: SourcedValue<string>;
    regionalBlocs: SourcedValue<string[]>;
    officialLanguages: SourcedValue<string[]>;
    dominantSpokenLanguages: SourcedValue<string[]>;
  };
  centralBank: {
    name: string;
    rawText: string;
    source: SourceRef;
  };
  regionalHarmonisationNote?: SourcedValue<string>;
  dataProtection: {
    name: string;
    rawText: string;
    source: SourceRef;
  };
  energySector: {
    regulator: string;
    rawText: string;
    source: SourceRef;
  };
  sectorPreamble?: SourcedValue<string>;
  sectorCompliance: Record<string, SectorComplianceEntry>;
  tax: {
    corporateTaxRaw: string;
    corporateTaxRate: number | null;
    corporateTaxNote: string | null;
    corporateTaxSource: SourceRef;
    vatRaw: string;
    vatRate: number | null;
    vatNote: string | null;
    vatSource: SourceRef;
    investmentAgency: SourcedValue<string>;
    incentives: SourcedValue<string[]>;
    considerations: SourcedValue<string>;
  };
  expansionNotes: SourcedValue<string>[];
}

export type FlagSeverity = 'critical' | 'warning' | 'info';

export type FlagCategory =
  | 'template-bleed'
  | 'wrong-regulator'
  | 'bloc-mismatch'
  | 'incomplete-agency'
  | 'verify-marker'
  | 'citation-bleed'
  | 'cross-border-gap';

export interface VerifyFlag {
  id: string;
  country: string;
  fileName: string;
  severity: FlagSeverity;
  category: FlagCategory;
  sectorScope: SectorName | 'All';
  title: string;
  explanation: string;
  recommendation: string;
  source: SourceRef;
}

export interface RegulatorComparisonRow {
  role: string;
  homeName: string;
  homeDetail: string;
  homeSource: SourceRef;
  targetName: string;
  targetDetail: string;
  targetSource: SourceRef;
  founderAction: string;
}

export interface LaunchBrief {
  home: CountryDossier;
  target: CountryDossier;
  sector: SectorName;
  regulators: RegulatorComparisonRow[];
  compliance: {
    homeSteps: string[];
    homeRaw: string;
    homeSource: SourceRef;
    targetSteps: string[];
    targetRaw: string;
    targetSource: SourceRef;
    targetRegulator: string;
    preambleWarning: string | null;
    preambleSource?: SourceRef;
    founderChecklist: {
      step: string;
      status: 'new-requirement' | 'verify-authority' | 'cross-border';
      source: SourceRef;
    }[];
  };
  taxes: {
    corporateTax: {
      homeRaw: string;
      homeRate: number | null;
      homeSource: SourceRef;
      targetRaw: string;
      targetRate: number | null;
      targetNote: string | null;
      targetSource: SourceRef;
      deltaPp: number | null;
      deltaSummary: string;
    };
    vat: {
      homeRaw: string;
      homeRate: number | null;
      homeSource: SourceRef;
      targetRaw: string;
      targetRate: number | null;
      targetNote: string | null;
      targetSource: SourceRef;
      deltaPp: number | null;
      deltaSummary: string;
    };
    investmentAgency: {
      home: SourcedValue<string>;
      target: SourcedValue<string>;
    };
    incentives: {
      home: SourcedValue<string[]>;
      target: SourcedValue<string[]>;
    };
    considerations: {
      home: SourcedValue<string>;
      target: SourcedValue<string>;
    };
  };
  languages: {
    homeOfficial: SourcedValue<string[]>;
    targetOfficial: SourcedValue<string[]>;
    homeSpoken: SourcedValue<string[]>;
    targetSpoken: SourcedValue<string[]>;
    sharedOfficial: string[];
    droppedOfficial: string[];
    addedOfficial: string[];
    differs: boolean;
    shiftSummary: string;
    operationalImpact: string;
    homeNoteSource?: SourceRef;
    targetNoteSource?: SourceRef;
  };
  blocs: {
    homeBlocs: SourcedValue<string[]>;
    targetBlocs: SourcedValue<string[]>;
    sharedBlocs: string[];
    homeOnlyBlocs: string[];
    targetOnlyBlocs: string[];
    corridorSummary: string;
    implications: {
      title: string;
      detail: string;
      kind: 'shared' | 'exit' | 'entry';
    }[];
    homeNoteSource?: SourceRef;
    targetNoteSource?: SourceRef;
  };
  verifyFlags: VerifyFlag[];
}
