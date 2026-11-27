import { useState } from 'react';
import { ShieldAlert, AlertTriangle, Info } from 'lucide-react';
import { FlagSeverity, SectorName, SourceRef, VerifyFlag } from '../lib/types';
import { SourceTag } from './SourceTag';

interface VerifyFirstPanelProps {
  flags: VerifyFlag[];
  activeSector: SectorName;
  onInspectSource: (source: SourceRef) => void;
}

export function VerifyFirstPanel({
  flags,
  activeSector,
  onInspectSource,
}: VerifyFirstPanelProps) {
  const [scopeFilter, setScopeFilter] = useState<'relevant' | 'all'>('all');
  const [severityFilter, setSeverityFilter] = useState<'all' | FlagSeverity>('all');

  const visibleFlags = flags.filter((flag) => {
    if (scopeFilter === 'relevant' && flag.sectorScope !== 'All' && flag.sectorScope !== activeSector) {
      return false;
    }
    if (severityFilter !== 'all' && flag.severity !== severityFilter) {
      return false;
    }
    return true;
  });

  const criticalCount = flags.filter((f) => f.severity === 'critical').length;
  const warningCount = flags.filter((f) => f.severity === 'warning').length;
  const infoCount = flags.filter((f) => f.severity === 'info').length;

  return (
    <section
      id="verify-first"
      aria-labelledby="heading-verify-first"
      className="bg-white border border-slate-200 rounded-xl overflow-hidden"
    >
      <div className="px-6 py-5 border-b border-slate-200 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2.5">
            <ShieldAlert className="w-4 h-4 text-red-700 shrink-0" aria-hidden="true" />
            <h2 id="heading-verify-first" className="text-base font-semibold text-slate-900">
              06. &ldquo;Verify First&rdquo; Flags — Automated Dossier Audit
            </h2>
          </div>
          <p className="text-xs text-slate-600 tabular-nums">
            {flags.length} discrepancies detected automatically across source markdown ({criticalCount} critical · {warningCount} verify · {infoCount} template notes)
          </p>
        </div>

        <div className="no-print flex flex-wrap items-center gap-3">
          {/* Scope segmented control */}
          <div className="flex items-center gap-1 p-1 bg-slate-100 rounded-lg">
            <button
              type="button"
              onClick={() => setScopeFilter('all')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors whitespace-nowrap shrink-0 cursor-pointer ${
                scopeFilter === 'all'
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              All Dossier Findings ({flags.length})
            </button>
            <button
              type="button"
              onClick={() => setScopeFilter('relevant')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors whitespace-nowrap shrink-0 cursor-pointer ${
                scopeFilter === 'relevant'
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {activeSector} &amp; Global Only
            </button>
          </div>

          {/* Severity segmented control */}
          <div className="flex items-center gap-1 p-1 bg-slate-100 rounded-lg">
            {(['all', 'critical', 'warning', 'info'] as const).map((sev) => (
              <button
                key={sev}
                type="button"
                onClick={() => setSeverityFilter(sev)}
                className={`px-2.5 py-1.5 text-xs font-medium rounded-md transition-colors whitespace-nowrap shrink-0 cursor-pointer ${
                  severityFilter === sev
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {sev === 'all'
                  ? 'All'
                  : sev === 'critical'
                    ? 'Critical'
                    : sev === 'warning'
                      ? 'Verify'
                      : 'Notes'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {visibleFlags.length === 0 ? (
        <div className="p-8 text-center text-sm text-slate-500">
          No flags match the current filter selection.
        </div>
      ) : (
        <div className="divide-y divide-slate-200">
          {visibleFlags.map((flag) => (
            <article key={flag.id} className="p-6 space-y-2.5 hover:bg-slate-50/50 transition-colors">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex flex-wrap items-center gap-2 text-xs">
                  {flag.severity === 'critical' ? (
                    <span className="inline-flex items-center gap-1 font-semibold text-red-700">
                      <ShieldAlert className="w-3.5 h-3.5" aria-hidden="true" />
                      Critical Error
                    </span>
                  ) : flag.severity === 'warning' ? (
                    <span className="inline-flex items-center gap-1 font-semibold text-amber-700">
                      <AlertTriangle className="w-3.5 h-3.5" aria-hidden="true" />
                      Verify Authority
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 font-semibold text-slate-700">
                      <Info className="w-3.5 h-3.5" aria-hidden="true" />
                      Template Note
                    </span>
                  )}
                  <span aria-hidden="true" className="text-slate-300">·</span>
                  <span className="font-medium text-slate-800">{flag.country}</span>
                  <span aria-hidden="true" className="text-slate-300">·</span>
                  <span className="text-slate-500">
                    {flag.sectorScope === 'All' ? 'Cross-sector' : flag.sectorScope}
                  </span>
                </div>

                <SourceTag source={flag.source} onInspect={onInspectSource} />
              </div>

              <h3 className="text-sm font-semibold text-slate-900">{flag.title}</h3>

              <p className="text-sm text-slate-700 leading-relaxed">{flag.explanation}</p>

              <div className="pt-1 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                <p className="text-slate-600">
                  <strong className="font-semibold text-slate-800">Founder action:</strong>{' '}
                  {flag.recommendation}
                </p>
              </div>

              <p className="font-mono text-[11px] text-slate-500 bg-slate-50 border border-slate-200 rounded px-3 py-1.5 overflow-x-auto">
                Line {flag.source.line}: {flag.source.quote}
              </p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
