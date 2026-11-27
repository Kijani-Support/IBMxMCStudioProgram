import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Download, FileText, Printer, AlertCircle } from 'lucide-react';
import { parseDossierMarkdown } from './lib/dossierParser';
import { buildLaunchBrief, exportBriefToMarkdown } from './lib/launchBrief';
import { CountryDossier, SectorName, SourceRef } from './lib/types';
import { RouteControlBar } from './components/RouteControlBar';
import { BriefOverviewStrip } from './components/BriefOverviewStrip';
import { BriefSections } from './components/BriefSections';
import { VerifyFirstPanel } from './components/VerifyFirstPanel';
import { DossierDrawer } from './components/DossierDrawer';
import { ImportDossierModal } from './components/ImportDossierModal';

interface RawDossierPayload {
  fileName: string;
  rawMarkdown: string;
}

export default function App() {
  const [dossiers, setDossiers] = useState<CountryDossier[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [homeId, setHomeId] = useState<string>('tanzania');
  const [targetId, setTargetId] = useState<string>('zambia');
  const [sector, setSector] = useState<SectorName>('Agritech');

  const [aiSummary, setAiSummary] = useState<string | null>(null);
  const [aiModel, setAiModel] = useState<string | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerFile, setDrawerFile] = useState<string>('tanzania.md');
  const [highlightedSource, setHighlightedSource] = useState<SourceRef | null>(null);

  const [importOpen, setImportOpen] = useState(false);
  const [exportMenuOpen, setExportMenuOpen] = useState(false);
  const exportMenuRef = useRef<HTMLDivElement | null>(null);

  const fetchDiskDossiers = useCallback(async (isManualRefresh = false) => {
    try {
      if (isManualRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setLoadError(null);

      const res = await fetch('/api/dossiers');
      if (!res.ok) {
        throw new Error(`Server returned ${res.status} while reading africa-regulatory/`);
      }
      const data = (await res.json()) as { dossiers: RawDossierPayload[] };
      const parsed = data.dossiers.map((item) =>
        parseDossierMarkdown(item.rawMarkdown, item.fileName),
      );

      setDossiers((prev) => {
        // Keep any user-imported dossiers that aren't on disk
        const diskIds = new Set(parsed.map((p) => p.id));
        const customOnly = prev.filter((p) => !diskIds.has(p.id));
        return [...parsed, ...customOnly];
      });

      if (parsed.length > 0) {
        setHomeId((current) =>
          parsed.some((d) => d.id === current) ? current : parsed[0].id,
        );
        setTargetId((current) =>
          parsed.some((d) => d.id === current)
            ? current
            : (parsed[1]?.id ?? parsed[0].id),
        );
      }
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : 'Unable to load country dossiers');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchDiskDossiers(false);
  }, [fetchDiskDossiers]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (exportMenuRef.current && !exportMenuRef.current.contains(event.target as Node)) {
        setExportMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Reset AI summary when route or sector changes
  useEffect(() => {
    setAiSummary(null);
    setAiModel(null);
    setAiError(null);
  }, [homeId, targetId, sector]);

  const homeDossier = useMemo(
    () => dossiers.find((d) => d.id === homeId) || dossiers[0],
    [dossiers, homeId],
  );
  const targetDossier = useMemo(
    () => dossiers.find((d) => d.id === targetId) || dossiers[1] || dossiers[0],
    [dossiers, targetId],
  );

  const brief = useMemo(() => {
    if (!homeDossier || !targetDossier) return null;
    return buildLaunchBrief(homeDossier, targetDossier, sector);
  }, [homeDossier, targetDossier, sector]);

  const handleSwapCountries = () => {
    setHomeId(targetId);
    setTargetId(homeId);
  };

  const handleInspectSource = (source: SourceRef) => {
    setDrawerFile(source.file);
    setHighlightedSource(source);
    setDrawerOpen(true);
  };

  const handleImportFiles = (items: RawDossierPayload[]) => {
    const newlyParsed = items.map((item) =>
      parseDossierMarkdown(item.rawMarkdown, item.fileName),
    );
    setDossiers((prev) => {
      const map = new Map(prev.map((d) => [d.id, d]));
      for (const item of newlyParsed) {
        map.set(item.id, item);
      }
      return Array.from(map.values()).sort((a, b) =>
        a.countryName.localeCompare(b.countryName),
      );
    });
    if (newlyParsed.length === 1) {
      setTargetId(newlyParsed[0].id);
    } else if (newlyParsed.length >= 2) {
      setHomeId(newlyParsed[0].id);
      setTargetId(newlyParsed[1].id);
    }
  };

  const handleGenerateAiSummary = async () => {
    if (!brief) return;
    setAiLoading(true);
    setAiError(null);

    try {
      const briefContext = {
        route: `${brief.home.countryName} (${brief.home.fileName}) -> ${brief.target.countryName} (${brief.target.fileName})`,
        sector: brief.sector,
        regulators: brief.regulators.map((r) => ({
          role: r.role,
          home: `${r.homeName} [${r.homeSource.file} ${r.homeSource.section}]`,
          target: `${r.targetName} [${r.targetSource.file} ${r.targetSource.section}]`,
        })),
        targetComplianceSteps: brief.compliance.targetSteps,
        complianceSource: `${brief.compliance.targetSource.file} ${brief.compliance.targetSource.section}`,
        taxes: {
          corporateTaxHome: `${brief.taxes.corporateTax.homeRaw} [${brief.taxes.corporateTax.homeSource.file} §5]`,
          corporateTaxTarget: `${brief.taxes.corporateTax.targetRaw} [${brief.taxes.corporateTax.targetSource.file} §5]`,
          vatHome: `${brief.taxes.vat.homeRaw} [${brief.taxes.vat.homeSource.file} §5]`,
          vatTarget: `${brief.taxes.vat.targetRaw} [${brief.taxes.vat.targetSource.file} §5]`,
        },
        languages: {
          homeOfficial: brief.languages.homeOfficial.value,
          targetOfficial: brief.languages.targetOfficial.value,
          shift: brief.languages.shiftSummary,
        },
        blocs: {
          home: brief.blocs.homeBlocs.value,
          target: brief.blocs.targetBlocs.value,
          shared: brief.blocs.sharedBlocs,
          corridor: brief.blocs.corridorSummary,
        },
        topVerifyFlags: brief.verifyFlags.slice(0, 5).map((f) => ({
          severity: f.severity,
          source: `${f.source.file} ${f.source.section} line ${f.source.line}`,
          title: f.title,
        })),
      };

      const res = await fetch('/api/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ briefContext }),
      });

      const payload = (await res.json()) as {
        summary?: string;
        model?: string;
        error?: string;
      };

      if (!res.ok || !payload.summary) {
        throw new Error(payload.error || `HTTP ${res.status}`);
      }

      setAiSummary(payload.summary);
      setAiModel(payload.model || 'gemini-4-hydrogen');
    } catch (err) {
      setAiError(err instanceof Error ? err.message : 'Unable to generate summary');
    } finally {
      setAiLoading(false);
    }
  };

  const handleDownloadMarkdown = () => {
    if (!brief) return;
    const md = exportBriefToMarkdown(brief, aiSummary);
    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `launch-brief-${brief.home.id}-to-${brief.target.id}-${brief.sector.toLowerCase().replace(/[^a-z0-9]+/g, '-')}.md`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    setExportMenuOpen(false);
  };

  const handlePrintPdf = () => {
    setExportMenuOpen(false);
    window.print();
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
      {/* Top Bar Contract: 3 zones separated by gap-8 */}
      <header className="no-print bg-white border-b border-slate-200 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-8">
          <a
            href="#top"
            className="text-lg font-bold tracking-tight text-slate-900 whitespace-nowrap shrink-0 font-display"
          >
            Cross-Border Navigator
          </a>

          <nav
            aria-label="Primary navigation"
            className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-600"
          >
            <a
              href="#regulators"
              className="hover:text-slate-900 hover:underline underline-offset-4 transition-colors whitespace-nowrap shrink-0"
            >
              Launch Brief
            </a>
            <a
              href="#verify-first"
              className="hover:text-slate-900 hover:underline underline-offset-4 transition-colors whitespace-nowrap shrink-0"
            >
              Verify Flags
            </a>
            <button
              type="button"
              onClick={() => {
                if (targetDossier) setDrawerFile(targetDossier.fileName);
                setHighlightedSource(null);
                setDrawerOpen(true);
              }}
              className="hover:text-slate-900 hover:underline underline-offset-4 transition-colors whitespace-nowrap shrink-0 cursor-pointer"
            >
              Source Dossiers
            </button>
            <a
              href="#methodology"
              className="hover:text-slate-900 hover:underline underline-offset-4 transition-colors whitespace-nowrap shrink-0"
            >
              Methodology
            </a>
          </nav>

          <div className="relative shrink-0" ref={exportMenuRef}>
            <button
              type="button"
              onClick={() => setExportMenuOpen((open) => !open)}
              disabled={!brief}
              aria-expanded={exportMenuOpen}
              className="h-9 px-4 inline-flex items-center gap-2 text-xs font-medium text-white bg-slate-900 hover:bg-slate-800 rounded-lg transition-colors whitespace-nowrap shrink-0 cursor-pointer disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-700"
            >
              <Download className="w-3.5 h-3.5" aria-hidden="true" />
              <span>Export Brief</span>
            </button>

            {exportMenuOpen && (
              <div
                role="menu"
                className="absolute right-0 mt-2 w-56 bg-white border border-slate-200 rounded-xl shadow-lg py-1.5 z-40"
              >
                <button
                  type="button"
                  role="menuitem"
                  onClick={handleDownloadMarkdown}
                  className="w-full px-4 py-2.5 text-left text-xs font-medium text-slate-700 hover:bg-slate-50 flex items-center gap-2.5 cursor-pointer"
                >
                  <FileText className="w-4 h-4 text-emerald-800" aria-hidden="true" />
                  <span>Download Markdown (.md)</span>
                </button>
                <button
                  type="button"
                  role="menuitem"
                  onClick={handlePrintPdf}
                  className="w-full px-4 py-2.5 text-left text-xs font-medium text-slate-700 hover:bg-slate-50 flex items-center gap-2.5 cursor-pointer"
                >
                  <Printer className="w-4 h-4 text-emerald-800" aria-hidden="true" />
                  <span>Print / Save One-Page PDF</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      <main id="top" className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Hero Title & Context */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div className="space-y-2 max-w-3xl">
            <p className="text-xs font-medium text-slate-500">
              Africa Regulatory Launch Brief · Parsed Directly from Country Markdown Dossiers
            </p>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 [text-wrap:balance]">
              {brief
                ? `${brief.home.countryName} to ${brief.target.countryName} — ${brief.sector} Launch Brief`
                : 'Cross-Border Regulatory & Tax Launch Brief'}
            </h1>
            <p className="text-sm text-slate-600 max-w-2xl leading-relaxed">
              Side-by-side regulatory path, compliance steps, tax deltas, language shift, regional bloc corridor, and automated dossier error flags—every figure linked to its exact source line.
            </p>
          </div>

          {brief && (
            <div className="no-print flex items-center gap-2 text-xs text-slate-500 font-mono">
              <span>Sources:</span>
              <button
                type="button"
                onClick={() => {
                  setDrawerFile(brief.home.fileName);
                  setHighlightedSource(null);
                  setDrawerOpen(true);
                }}
                className="underline decoration-slate-300 hover:text-emerald-800 cursor-pointer"
              >
                {brief.home.fileName}
              </button>
              <span aria-hidden="true">·</span>
              <button
                type="button"
                onClick={() => {
                  setDrawerFile(brief.target.fileName);
                  setHighlightedSource(null);
                  setDrawerOpen(true);
                }}
                className="underline decoration-slate-300 hover:text-emerald-800 cursor-pointer"
              >
                {brief.target.fileName}
              </button>
            </div>
          )}
        </div>

        {/* Workspace Route & Sector Controls */}
        <RouteControlBar
          dossiers={dossiers}
          homeId={homeId}
          targetId={targetId}
          sector={sector}
          onHomeChange={setHomeId}
          onTargetChange={setTargetId}
          onSwapCountries={handleSwapCountries}
          onSectorChange={setSector}
          onOpenImport={() => setImportOpen(true)}
          onRefreshDisk={() => fetchDiskDossiers(true)}
          isRefreshing={refreshing}
        />

        {loading ? (
          <div className="bg-white border border-slate-200 rounded-xl p-12 text-center space-y-3">
            <div className="h-4 w-48 bg-slate-200 rounded mx-auto animate-pulse" />
            <div className="h-3 w-72 bg-slate-100 rounded mx-auto animate-pulse" />
            <p className="text-xs text-slate-500">Reading country dossiers from africa-regulatory/...</p>
          </div>
        ) : loadError ? (
          <div
            role="alert"
            className="bg-white border border-red-200 rounded-xl p-6 flex items-start gap-3 text-sm text-red-800"
          >
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5 text-red-700" aria-hidden="true" />
            <div className="space-y-1">
              <p className="font-semibold">Unable to load dossier files</p>
              <p className="text-red-700">{loadError}</p>
            </div>
          </div>
        ) : brief ? (
          <>
            {brief.home.id === brief.target.id && (
              <div
                role="status"
                className="no-print bg-amber-50 border border-amber-200 rounded-xl px-5 py-3 text-xs text-amber-900"
              >
                Home and target country are currently set to <strong>{brief.home.countryName}</strong>. Choose a second country or load additional <code className="font-mono">.md</code> dossiers to compare cross-border differences.
              </div>
            )}

            <BriefOverviewStrip
              brief={brief}
              aiSummary={aiSummary}
              aiModel={aiModel}
              aiLoading={aiLoading}
              aiError={aiError}
              onGenerateAiSummary={handleGenerateAiSummary}
              onInspectSource={handleInspectSource}
            />

            <BriefSections brief={brief} onInspectSource={handleInspectSource} />

            <VerifyFirstPanel
              flags={brief.verifyFlags}
              activeSector={brief.sector}
              onInspectSource={handleInspectSource}
            />

            {/* Methodology */}
            <section
              id="methodology"
              aria-labelledby="heading-methodology"
              className="no-print bg-white border border-slate-200 rounded-xl p-6 space-y-3"
            >
              <h2 id="heading-methodology" className="text-sm font-semibold text-slate-900">
                How This Navigator Reads Dossiers (Zero Hardcoding)
              </h2>
              <p className="text-sm text-slate-600 leading-relaxed">
                Every regulator name, compliance step, tax percentage, language, and regional bloc above is parsed live at runtime from the Markdown files in <code className="font-mono text-xs bg-slate-100 px-1.5 py-0.5 rounded">africa-regulatory/*.md</code> (plus any <code className="font-mono text-xs bg-slate-100 px-1.5 py-0.5 rounded">.md</code> files you upload). The automated auditor cross-checks Section 1 blocs against Section 2 harmonisation claims, checks Section 4 sector rows for leaked Section 5 VAT/corporate-tax percentages or swapped regulators, and flags generic unlocalized agencies and verification tags with exact line numbers.
              </p>
            </section>
          </>
        ) : null}
      </main>

      <footer className="border-t border-slate-200 bg-white py-5 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs text-slate-500">
          <p>
            Planning reference only — dossiers and launch briefs are not legal, tax, or financial advice. Verify each item with the named authority before commitment.
          </p>
          <p className="font-mono shrink-0">Source: africa-regulatory/*.md</p>
        </div>
      </footer>

      <DossierDrawer
        isOpen={drawerOpen}
        dossiers={dossiers}
        activeFile={drawerFile}
        highlightedSource={highlightedSource}
        flags={brief?.verifyFlags || []}
        onSelectFile={(file) => {
          setDrawerFile(file);
          setHighlightedSource(null);
        }}
        onClose={() => setDrawerOpen(false)}
      />

      <ImportDossierModal
        isOpen={importOpen}
        onClose={() => setImportOpen(false)}
        onImportFiles={handleImportFiles}
      />
    </div>
  );
}
