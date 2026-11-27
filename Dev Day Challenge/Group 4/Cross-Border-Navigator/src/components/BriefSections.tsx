import { AlertTriangle, CheckCircle2, Globe2, Languages, Scale, Landmark } from 'lucide-react';
import { LaunchBrief, SourceRef } from '../lib/types';
import { SourceTag } from './SourceTag';

interface BriefSectionsProps {
  brief: LaunchBrief;
  onInspectSource: (source: SourceRef) => void;
}

export function BriefSections({ brief, onInspectSource }: BriefSectionsProps) {
  const { home, target, sector, regulators, compliance, taxes, languages, blocs } = brief;

  return (
    <div className="space-y-8">
      {/* 1. Regulators to Engage */}
      <section
        id="regulators"
        aria-labelledby="heading-regulators"
        className="bg-white border border-slate-200 rounded-xl overflow-hidden print-break-inside-avoid"
      >
        <div className="px-6 py-4 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2.5">
            <Landmark className="w-4 h-4 text-emerald-800 shrink-0" aria-hidden="true" />
            <h2 id="heading-regulators" className="text-base font-semibold text-slate-900">
              01. Regulators to Engage ({target.countryName} vs. {home.countryName})
            </h2>
          </div>
          <span className="text-xs text-slate-500">
            Central bank · Data protection · {sector} authority
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50/70 text-xs font-medium text-slate-600">
                <th className="py-3 px-6 w-48">Regulatory Role</th>
                <th className="py-3 px-4">Home: {home.countryName}</th>
                <th className="py-3 px-4">Target: {target.countryName}</th>
                <th className="py-3 px-6">What this means for your launch</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 text-sm">
              {regulators.map((row) => (
                <tr key={row.role} className="hover:bg-slate-50/60 transition-colors align-top">
                  <td className="py-4 px-6 font-medium text-slate-900">{row.role}</td>
                  <td className="py-4 px-4 space-y-1.5">
                    <p className="font-medium text-slate-800">{row.homeName}</p>
                    <div>
                      <SourceTag source={row.homeSource} onInspect={onInspectSource} />
                    </div>
                  </td>
                  <td className="py-4 px-4 space-y-1.5">
                    <p className="font-semibold text-emerald-900">{row.targetName}</p>
                    <div>
                      <SourceTag source={row.targetSource} onInspect={onInspectSource} />
                    </div>
                  </td>
                  <td className="py-4 px-6 text-slate-600 leading-relaxed">{row.founderAction}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* 2. Sector Compliance Steps */}
      <section
        id="compliance"
        aria-labelledby="heading-compliance"
        className="bg-white border border-slate-200 rounded-xl overflow-hidden print-break-inside-avoid"
      >
        <div className="px-6 py-4 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-800 shrink-0" aria-hidden="true" />
            <h2 id="heading-compliance" className="text-base font-semibold text-slate-900">
              02. Sector Compliance Steps — {sector}
            </h2>
          </div>
          <SourceTag source={compliance.targetSource} onInspect={onInspectSource} />
        </div>

        {compliance.preambleWarning && (
          <div className="px-6 py-3 bg-amber-50/70 border-b border-amber-200 flex items-start gap-2.5 text-xs text-amber-900">
            <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" aria-hidden="true" />
            <div className="flex-1 flex flex-wrap items-center justify-between gap-2">
              <span>{compliance.preambleWarning}</span>
              {compliance.preambleSource && (
                <SourceTag source={compliance.preambleSource} onInspect={onInspectSource} compact />
              )}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-slate-200">
          {/* Target Checklist */}
          <div className="p-6 space-y-4">
            <div className="flex items-center justify-between gap-2">
              <h3 className="text-sm font-semibold text-slate-900">
                Target Requirements in {target.countryName}
              </h3>
              <SourceTag source={compliance.targetSource} onInspect={onInspectSource} compact />
            </div>

            <ol className="space-y-3.5">
              {compliance.founderChecklist.map((item, idx) => (
                <li key={idx} className="flex items-start gap-3">
                  <span className="font-mono tabular-nums text-xs font-semibold text-emerald-800 bg-emerald-50 border border-emerald-200 rounded w-6 h-6 inline-flex items-center justify-center shrink-0 mt-0.5">
                    {idx + 1}
                  </span>
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-slate-900">
                      {item.step.charAt(0).toUpperCase() + item.step.slice(1)}
                    </p>
                    <p className="text-xs text-slate-500">
                      {item.status === 'cross-border'
                        ? 'Cross-border trigger — verify export permits & border SPS rules'
                        : item.status === 'verify-authority'
                          ? 'Generic template label — confirm exact national agency & fee schedule'
                          : 'Target statutory filing required before launch'}
                    </p>
                  </div>
                </li>
              ))}
            </ol>
          </div>

          {/* Home Baseline Comparison */}
          <div className="p-6 space-y-4 bg-slate-50/40">
            <div className="flex items-center justify-between gap-2">
              <h3 className="text-sm font-semibold text-slate-900">
                Home Baseline ({home.countryName})
              </h3>
              <SourceTag source={compliance.homeSource} onInspect={onInspectSource} compact />
            </div>

            <ol className="space-y-3">
              {compliance.homeSteps.map((step, idx) => (
                <li key={idx} className="flex items-start gap-3 text-sm text-slate-700">
                  <span className="font-mono tabular-nums text-xs text-slate-500 w-5 shrink-0 mt-0.5">
                    0{idx + 1}.
                  </span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>

            <div className="pt-3 border-t border-slate-200 text-xs text-slate-600 leading-relaxed">
              <strong className="font-medium text-slate-800">Comparison note:</strong>{' '}
              {compliance.homeRaw === compliance.targetRaw
                ? `Both ${home.fileName} and ${target.fileName} use identical generic compliance phrasing for ${sector}. That signals the compliance table has not yet been localized with ${target.countryName}-specific agency names or statutory fee amounts.`
                : `${target.countryName} introduces distinct ${sector.toLowerCase()} requirements relative to ${home.countryName}; verify each named step locally.`}
            </div>
          </div>
        </div>
      </section>

      {/* 3. Tax & Investment Differences */}
      <section
        id="taxes"
        aria-labelledby="heading-taxes"
        className="bg-white border border-slate-200 rounded-xl overflow-hidden print-break-inside-avoid"
      >
        <div className="px-6 py-4 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2.5">
            <Scale className="w-4 h-4 text-emerald-800 shrink-0" aria-hidden="true" />
            <h2 id="heading-taxes" className="text-base font-semibold text-slate-900">
              03. Tax &amp; Investment Differences
            </h2>
          </div>
          <span className="text-xs text-slate-500">
            Corporate income tax · VAT · Investment incentives
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50/70 text-xs font-medium text-slate-600">
                <th className="py-3 px-6 w-52">Tax / Fiscal Item</th>
                <th className="py-3 px-4">{home.countryName} (Home)</th>
                <th className="py-3 px-4">{target.countryName} (Target)</th>
                <th className="py-3 px-6">Difference &amp; Impact</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 text-sm">
              <tr className="align-top">
                <td className="py-4 px-6 font-medium text-slate-900">Standard Corporate Income Tax</td>
                <td className="py-4 px-4 space-y-1">
                  <p className="font-mono tabular-nums font-semibold text-slate-900">
                    {taxes.corporateTax.homeRaw}
                  </p>
                  <SourceTag source={taxes.corporateTax.homeSource} onInspect={onInspectSource} compact />
                </td>
                <td className="py-4 px-4 space-y-1">
                  <p className="font-mono tabular-nums font-semibold text-emerald-900">
                    {taxes.corporateTax.targetRaw}
                  </p>
                  <SourceTag source={taxes.corporateTax.targetSource} onInspect={onInspectSource} compact />
                </td>
                <td className="py-4 px-6 text-slate-700">{taxes.corporateTax.deltaSummary}</td>
              </tr>

              <tr className="align-top">
                <td className="py-4 px-6 font-medium text-slate-900">Standard VAT / Sales Tax</td>
                <td className="py-4 px-4 space-y-1">
                  <p className="font-mono tabular-nums font-semibold text-slate-900">
                    {taxes.vat.homeRaw}
                  </p>
                  <SourceTag source={taxes.vat.homeSource} onInspect={onInspectSource} compact />
                </td>
                <td className="py-4 px-4 space-y-1">
                  <p className="font-mono tabular-nums font-semibold text-emerald-900">
                    {taxes.vat.targetRaw}
                  </p>
                  <SourceTag source={taxes.vat.targetSource} onInspect={onInspectSource} compact />
                </td>
                <td className="py-4 px-6 text-slate-700">{taxes.vat.deltaSummary}</td>
              </tr>

              <tr className="align-top">
                <td className="py-4 px-6 font-medium text-slate-900">Investment Agency &amp; Incentives</td>
                <td className="py-4 px-4 space-y-1.5">
                  <p className="font-medium text-slate-800">{taxes.investmentAgency.home.value}</p>
                  <p className="text-xs text-slate-600">
                    {taxes.incentives.home.value.join(' · ') || 'See dossier'}
                  </p>
                  <SourceTag source={taxes.investmentAgency.home.source} onInspect={onInspectSource} compact />
                </td>
                <td className="py-4 px-4 space-y-1.5">
                  <p className="font-medium text-emerald-900">{taxes.investmentAgency.target.value}</p>
                  <p className="text-xs text-slate-600">
                    {taxes.incentives.target.value.join(' · ') || 'See dossier'}
                  </p>
                  <SourceTag source={taxes.investmentAgency.target.source} onInspect={onInspectSource} compact />
                </td>
                <td className="py-4 px-6 text-xs text-slate-600 leading-relaxed">
                  {taxes.considerations.target.value}
                  <div className="mt-1.5">
                    <SourceTag source={taxes.considerations.target.source} onInspect={onInspectSource} compact />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* 4 & 5. Language & Regional Blocs (Balanced 2-column row) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
        {/* 4. Language & Legal Operations */}
        <section
          id="language"
          aria-labelledby="heading-language"
          className="bg-white border border-slate-200 rounded-xl p-6 flex flex-col justify-between gap-5 print-break-inside-avoid"
        >
          <div className="space-y-4">
            <div className="flex items-center justify-between gap-2 pb-3 border-b border-slate-200">
              <div className="flex items-center gap-2.5">
                <Languages className="w-4 h-4 text-emerald-800 shrink-0" aria-hidden="true" />
                <h2 id="heading-language" className="text-base font-semibold text-slate-900">
                  04. Language &amp; Business Operations
                </h2>
              </div>
              <span className="text-xs font-medium text-slate-600">
                {languages.differs ? 'Language Shift' : 'No Shift'}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="space-y-1">
                <p className="text-xs font-medium text-slate-500">{home.countryName} Official</p>
                <p className="font-semibold text-slate-900">
                  {languages.homeOfficial.value.join(', ')}
                </p>
                <p className="text-xs text-slate-500">
                  Spoken: {languages.homeSpoken.value.join(', ')}
                </p>
                <SourceTag source={languages.homeOfficial.source} onInspect={onInspectSource} compact />
              </div>

              <div className="space-y-1">
                <p className="text-xs font-medium text-slate-500">{target.countryName} Official</p>
                <p className="font-semibold text-emerald-900">
                  {languages.targetOfficial.value.join(', ')}
                </p>
                <p className="text-xs text-slate-500">
                  Spoken: {languages.targetSpoken.value.join(', ')}
                </p>
                <SourceTag source={languages.targetOfficial.source} onInspect={onInspectSource} compact />
              </div>
            </div>

            <div className="pt-3 border-t border-slate-200 space-y-2 text-sm text-slate-700 leading-relaxed">
              <p className="font-medium text-slate-900">{languages.shiftSummary}</p>
              <p>{languages.operationalImpact}</p>
            </div>
          </div>

          {languages.targetNoteSource && (
            <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
              <span>Legal &amp; contractual language note</span>
              <SourceTag source={languages.targetNoteSource} onInspect={onInspectSource} compact />
            </div>
          )}
        </section>

        {/* 5. Regional Blocs & Cross-Border Corridor */}
        <section
          id="blocs"
          aria-labelledby="heading-blocs"
          className="bg-white border border-slate-200 rounded-xl p-6 flex flex-col justify-between gap-5 print-break-inside-avoid"
        >
          <div className="space-y-4">
            <div className="flex items-center justify-between gap-2 pb-3 border-b border-slate-200">
              <div className="flex items-center gap-2.5">
                <Globe2 className="w-4 h-4 text-emerald-800 shrink-0" aria-hidden="true" />
                <h2 id="heading-blocs" className="text-base font-semibold text-slate-900">
                  05. Shared Regional Blocs &amp; Trade Corridor
                </h2>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="space-y-1">
                <p className="text-xs font-medium text-slate-500">{home.countryName} Blocs</p>
                <p className="font-medium text-slate-900">
                  {blocs.homeBlocs.value.join(' · ')}
                </p>
                <SourceTag source={blocs.homeBlocs.source} onInspect={onInspectSource} compact />
              </div>
              <div className="space-y-1">
                <p className="text-xs font-medium text-slate-500">{target.countryName} Blocs</p>
                <p className="font-medium text-emerald-900">
                  {blocs.targetBlocs.value.join(' · ')}
                </p>
                <SourceTag source={blocs.targetBlocs.source} onInspect={onInspectSource} compact />
              </div>
            </div>

            <div className="pt-3 border-t border-slate-200 space-y-3">
              {blocs.implications.map((imp, idx) => (
                <div key={idx} className="space-y-1">
                  <p className="text-xs font-semibold text-slate-900">
                    <span
                      className={
                        imp.kind === 'shared'
                          ? 'text-emerald-800'
                          : imp.kind === 'exit'
                            ? 'text-amber-800'
                            : 'text-slate-900'
                      }
                    >
                      {imp.title}
                    </span>
                  </p>
                  <p className="text-sm text-slate-700 leading-relaxed">{imp.detail}</p>
                </div>
              ))}
            </div>
          </div>

          {blocs.targetNoteSource && (
            <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
              <span>Customs, data flows &amp; recognition note</span>
              <SourceTag source={blocs.targetNoteSource} onInspect={onInspectSource} compact />
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
