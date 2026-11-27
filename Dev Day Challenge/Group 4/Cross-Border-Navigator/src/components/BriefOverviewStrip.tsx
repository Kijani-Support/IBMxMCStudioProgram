import { Sparkles, Loader2, AlertCircle } from 'lucide-react';
import { cleanAuthorityName } from '../lib/launchBrief';
import { LaunchBrief, SourceRef } from '../lib/types';
import { SourceTag } from './SourceTag';

interface BriefOverviewStripProps {
  brief: LaunchBrief;
  aiSummary: string | null;
  aiModel: string | null;
  aiLoading: boolean;
  aiError: string | null;
  onGenerateAiSummary: () => void;
  onInspectSource: (source: SourceRef) => void;
}

export function BriefOverviewStrip({
  brief,
  aiSummary,
  aiModel,
  aiLoading,
  aiError,
  onGenerateAiSummary,
  onInspectSource,
}: BriefOverviewStripProps) {
  const { home, target, taxes, languages, blocs, verifyFlags } = brief;
  const criticalCount = verifyFlags.filter((f) => f.severity === 'critical').length;

  return (
    <div className="space-y-6">
      {/* 4-Column Executive Metric Strip */}
      <div className="bg-white border border-slate-200 rounded-xl grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 divide-y sm:divide-y-0 sm:divide-x divide-slate-200 print-break-inside-avoid">
        {/* Corporate Income Tax */}
        <div className="p-5 flex flex-col justify-between gap-3">
          <div className="space-y-1">
            <p className="text-xs font-medium text-slate-500">Corporate Income Tax</p>
            <div className="flex items-baseline gap-2 font-mono tabular-nums">
              <span className="text-xl font-semibold text-slate-900">
                {taxes.corporateTax.homeRate !== null ? `${taxes.corporateTax.homeRate}%` : taxes.corporateTax.homeRaw}
              </span>
              <span className="text-slate-400">→</span>
              <span className="text-xl font-semibold text-emerald-800">
                {taxes.corporateTax.targetRate !== null ? `${taxes.corporateTax.targetRate}%` : taxes.corporateTax.targetRaw}
              </span>
            </div>
            <p className="text-xs text-slate-600">
              {taxes.corporateTax.deltaSummary}
              {taxes.corporateTax.targetNote ? ` (${taxes.corporateTax.targetNote})` : ''}
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 pt-2 border-t border-slate-100">
            <SourceTag source={taxes.corporateTax.homeSource} onInspect={onInspectSource} compact />
            <SourceTag source={taxes.corporateTax.targetSource} onInspect={onInspectSource} compact />
          </div>
        </div>

        {/* Standard VAT */}
        <div className="p-5 flex flex-col justify-between gap-3">
          <div className="space-y-1">
            <p className="text-xs font-medium text-slate-500">Standard VAT / Sales Tax</p>
            <div className="flex items-baseline gap-2 font-mono tabular-nums">
              <span className="text-xl font-semibold text-slate-900">
                {taxes.vat.homeRate !== null ? `${taxes.vat.homeRate}%` : taxes.vat.homeRaw}
              </span>
              <span className="text-slate-400">→</span>
              <span className="text-xl font-semibold text-emerald-800">
                {taxes.vat.targetRate !== null ? `${taxes.vat.targetRate}%` : taxes.vat.targetRaw}
              </span>
            </div>
            <p className="text-xs text-slate-600">{taxes.vat.deltaSummary}</p>
          </div>
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 pt-2 border-t border-slate-100">
            <SourceTag source={taxes.vat.homeSource} onInspect={onInspectSource} compact />
            <SourceTag source={taxes.vat.targetSource} onInspect={onInspectSource} compact />
          </div>
        </div>

        {/* Official Language */}
        <div className="p-5 flex flex-col justify-between gap-3">
          <div className="space-y-1">
            <p className="text-xs font-medium text-slate-500">Official Business Language</p>
            <p className="text-base font-semibold text-slate-900 leading-snug">
              {languages.homeOfficial.value.join(', ')} <span className="text-slate-400">→</span>{' '}
              <span className="text-emerald-800">{languages.targetOfficial.value.join(', ')}</span>
            </p>
            <p className="text-xs text-slate-600">{languages.shiftSummary}</p>
          </div>
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 pt-2 border-t border-slate-100">
            <SourceTag source={languages.homeOfficial.source} onInspect={onInspectSource} compact />
            <SourceTag source={languages.targetOfficial.source} onInspect={onInspectSource} compact />
          </div>
        </div>

        {/* Regional Blocs */}
        <div className="p-5 flex flex-col justify-between gap-3">
          <div className="space-y-1">
            <p className="text-xs font-medium text-slate-500">Regional Bloc Corridor</p>
            <p className="text-base font-semibold text-slate-900 leading-snug">
              {blocs.sharedBlocs.filter((b) => !/african union/i.test(b)).length > 0
                ? `Shared: ${blocs.sharedBlocs.filter((b) => !/african union/i.test(b)).join(', ')}`
                : 'No shared sub-bloc'}
            </p>
            <p className="text-xs text-slate-600">{blocs.corridorSummary}</p>
          </div>
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 pt-2 border-t border-slate-100">
            <SourceTag source={blocs.homeBlocs.source} onInspect={onInspectSource} compact />
            <SourceTag source={blocs.targetBlocs.source} onInspect={onInspectSource} compact />
          </div>
        </div>
      </div>

      {/* Plain-Language Executive Summary */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 print-break-inside-avoid">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-200">
          <div>
            <h2 className="text-base font-semibold text-slate-900">
              Plain-Language Founder Briefing
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Grounded strictly in {home.fileName} and {target.fileName} · No external figures invented
            </p>
          </div>

          <button
            type="button"
            onClick={onGenerateAiSummary}
            disabled={aiLoading}
            className="no-print h-9 px-3.5 inline-flex items-center gap-2 text-xs font-medium text-white bg-emerald-800 hover:bg-emerald-900 rounded-lg transition-colors whitespace-nowrap shrink-0 cursor-pointer disabled:opacity-60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-700"
          >
            {aiLoading ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" aria-hidden="true" />
            ) : (
              <Sparkles className="w-3.5 h-3.5" aria-hidden="true" />
            )}
            <span>{aiSummary ? 'Regenerate AI Brief' : 'Generate AI Plain-Language Brief'}</span>
          </button>
        </div>

        <div className="pt-4 space-y-3 text-sm leading-relaxed text-slate-700">
          {aiError && (
            <div
              role="alert"
              className="flex items-start gap-2.5 p-3 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 text-xs"
            >
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-amber-700" aria-hidden="true" />
              <div>
                <p className="font-medium">AI summary unavailable: {aiError}</p>
                <p className="mt-0.5 text-amber-800">
                  Showing deterministic dossier brief below. All six regulatory outputs remain 100% live from the parsed markdown files.
                </p>
              </div>
            </div>
          )}

          {aiSummary ? (
            <div className="space-y-3">
              {aiSummary.split(/\n\n+/).map((para, idx) => (
                <p key={idx} className="text-slate-800">
                  {para}
                </p>
              ))}
              {aiModel && (
                <p className="text-xs text-slate-500 font-mono">
                  Synthesized by {aiModel} · Grounded in {home.fileName} & {target.fileName}
                </p>
              )}
            </div>
          ) : (
            <div className="space-y-2.5 text-slate-700">
              <p>
                Expanding your <strong className="font-semibold text-slate-900">{brief.sector}</strong> operation from{' '}
                <strong className="font-semibold text-slate-900">{home.countryName}</strong> to{' '}
                <strong className="font-semibold text-slate-900">{target.countryName}</strong> requires engaging{' '}
                <strong className="font-semibold text-slate-900">{target.centralBank.name}</strong> ({target.fileName} §2),{' '}
                <strong className="font-semibold text-slate-900">{cleanAuthorityName(target.dataProtection.name)}</strong> ({target.fileName} §2), and{' '}
                <strong className="font-semibold text-slate-900">{brief.compliance.targetRegulator}</strong> ({target.fileName} §4).
              </p>
              <p>
                Headline corporate tax stays at{' '}
                <span className="font-mono tabular-nums font-medium text-slate-900">
                  {taxes.corporateTax.targetRaw}
                </span>{' '}
                ({target.fileName} §5) while standard VAT shifts from{' '}
                <span className="font-mono tabular-nums font-medium text-slate-900">
                  {taxes.vat.homeRaw}
                </span>{' '}
                ({home.fileName} §5) to{' '}
                <span className="font-mono tabular-nums font-medium text-slate-900">
                  {taxes.vat.targetRaw}
                </span>{' '}
                ({target.fileName} §5). {languages.operationalImpact}
              </p>
              <p>
                Before retaining local counsel, review the{' '}
                <strong className="font-semibold text-amber-900 tabular-nums">
                  {verifyFlags.length} automated &ldquo;Verify First&rdquo; flags
                </strong>{' '}
                ({criticalCount} critical dossier inconsistencies) surfaced below—these dossiers are planning drafts containing real template errors.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
