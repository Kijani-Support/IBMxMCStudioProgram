import { ArrowLeftRight, FolderUp, RefreshCw } from 'lucide-react';
import { CountryDossier, SECTORS, SectorName } from '../lib/types';

interface RouteControlBarProps {
  dossiers: CountryDossier[];
  homeId: string;
  targetId: string;
  sector: SectorName;
  onHomeChange: (id: string) => void;
  onTargetChange: (id: string) => void;
  onSwapCountries: () => void;
  onSectorChange: (sector: SectorName) => void;
  onOpenImport: () => void;
  onRefreshDisk: () => void;
  isRefreshing: boolean;
}

export function RouteControlBar({
  dossiers,
  homeId,
  targetId,
  sector,
  onHomeChange,
  onTargetChange,
  onSwapCountries,
  onSectorChange,
  onOpenImport,
  onRefreshDisk,
  isRefreshing,
}: RouteControlBarProps) {
  return (
    <section
      aria-label="Route and sector configuration"
      className="no-print bg-white border border-slate-200 rounded-xl p-5 md:p-6 space-y-5"
    >
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4">
        <div className="grid grid-cols-1 sm:grid-cols-[1fr_auto_1fr] gap-3 items-end flex-1 max-w-2xl">
          <div>
            <label
              htmlFor="home-country-select"
              className="block text-xs font-medium text-slate-600 mb-1.5"
            >
              Home country (operating base)
            </label>
            <select
              id="home-country-select"
              value={homeId}
              onChange={(e) => onHomeChange(e.target.value)}
              className="w-full h-11 px-3 bg-slate-50 border border-slate-300 rounded-lg text-sm font-medium text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-700 focus:border-emerald-700"
            >
              {dossiers.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.countryName} ({d.fileName})
                </option>
              ))}
            </select>
          </div>

          <button
            type="button"
            onClick={onSwapCountries}
            aria-label="Swap home and target countries"
            title="Swap home and target countries"
            className="h-11 px-3 inline-flex items-center justify-center gap-2 border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 rounded-lg transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-700"
          >
            <ArrowLeftRight className="w-4 h-4 shrink-0" aria-hidden="true" />
            <span className="sm:hidden text-xs font-medium">Swap home &amp; target</span>
          </button>

          <div>
            <label
              htmlFor="target-country-select"
              className="block text-xs font-medium text-slate-600 mb-1.5"
            >
              Target country (expansion market)
            </label>
            <select
              id="target-country-select"
              value={targetId}
              onChange={(e) => onTargetChange(e.target.value)}
              className="w-full h-11 px-3 bg-slate-50 border border-slate-300 rounded-lg text-sm font-medium text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-700 focus:border-emerald-700"
            >
              {dossiers.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.countryName} ({d.fileName})
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <button
            type="button"
            onClick={onRefreshDisk}
            disabled={isRefreshing}
            className="h-10 px-3.5 inline-flex items-center gap-2 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors whitespace-nowrap shrink-0 cursor-pointer disabled:opacity-60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-700"
          >
            <RefreshCw
              className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`}
              aria-hidden="true"
            />
            <span>Reload Disk ({dossiers.length})</span>
          </button>

          <button
            type="button"
            onClick={onOpenImport}
            className="h-10 px-3.5 inline-flex items-center gap-2 text-xs font-medium text-emerald-900 bg-emerald-50 border border-emerald-200 rounded-lg hover:bg-emerald-100 transition-colors whitespace-nowrap shrink-0 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus:ring-emerald-700"
          >
            <FolderUp className="w-3.5 h-3.5" aria-hidden="true" />
            <span>Load .md Dossiers</span>
          </button>
        </div>
      </div>

      <div className="pt-4 border-t border-slate-200">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2.5">
          <span className="text-xs font-medium text-slate-600">
            Startup sector (parsed from Section 4 of each dossier)
          </span>
          <span className="text-xs text-slate-500 font-mono tabular-nums">
            {dossiers.length} country {dossiers.length === 1 ? 'dossier' : 'dossiers'} loaded
          </span>
        </div>

        <div
          role="tablist"
          aria-label="Startup sector"
          className="flex flex-wrap items-center gap-1.5 p-1 bg-slate-100 rounded-lg"
        >
          {SECTORS.map((item) => {
            const active = item === sector;
            return (
              <button
                key={item}
                type="button"
                role="tab"
                aria-selected={active}
                onClick={() => onSectorChange(item)}
                className={`px-3.5 py-2 text-xs font-medium rounded-md transition-colors whitespace-nowrap shrink-0 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-700 ${
                  active
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {item}
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
}
