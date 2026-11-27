import { useEffect, useRef } from 'react';
import { X, FileCode2 } from 'lucide-react';
import { CountryDossier, SourceRef, VerifyFlag } from '../lib/types';

interface DossierDrawerProps {
  isOpen: boolean;
  dossiers: CountryDossier[];
  activeFile: string;
  highlightedSource: SourceRef | null;
  flags: VerifyFlag[];
  onSelectFile: (fileName: string) => void;
  onClose: () => void;
}

export function DossierDrawer({
  isOpen,
  dossiers,
  activeFile,
  highlightedSource,
  flags,
  onSelectFile,
  onClose,
}: DossierDrawerProps) {
  const highlightedLineRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (isOpen && highlightedSource && highlightedLineRef.current) {
      highlightedLineRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, [isOpen, highlightedSource]);

  if (!isOpen) return null;

  const current = dossiers.find((d) => d.fileName === activeFile) || dossiers[0];
  if (!current) return null;

  const lines = current.rawMarkdown.split(/\r?\n/);
  const lineFlags = new Map<number, VerifyFlag[]>();
  for (const f of flags) {
    if (f.source.file === current.fileName) {
      const existing = lineFlags.get(f.source.line) || [];
      existing.push(f);
      lineFlags.set(f.source.line, existing);
    }
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Source markdown dossier viewer"
      className="no-print fixed inset-0 z-50 flex justify-end bg-slate-900/40 backdrop-blur-[1px]"
    >
      <div className="w-full max-w-3xl bg-white h-full border-l border-slate-200 flex flex-col shadow-xl">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between gap-4">
          <div className="flex items-center gap-2.5 min-w-0">
            <FileCode2 className="w-4 h-4 text-emerald-800 shrink-0" aria-hidden="true" />
            <div className="min-w-0">
              <h2 className="text-sm font-semibold text-slate-900 truncate">
                Source Dossier Provenance Inspector
              </h2>
              <p className="text-xs text-slate-500 truncate">
                Live markdown read directly from africa-regulatory/ or imported files
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            aria-label="Close source dossier inspector"
            className="p-2 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" aria-hidden="true" />
          </button>
        </div>

        {/* File selector tabs */}
        <div className="px-6 py-2.5 border-b border-slate-200 bg-slate-50 flex items-center gap-1.5 overflow-x-auto">
          {dossiers.map((d) => {
            const active = d.fileName === current.fileName;
            return (
              <button
                key={d.fileName}
                type="button"
                onClick={() => onSelectFile(d.fileName)}
                className={`px-3 py-1.5 text-xs font-mono rounded-md transition-colors whitespace-nowrap shrink-0 cursor-pointer ${
                  active
                    ? 'bg-white text-slate-900 border border-slate-200 font-semibold'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {d.fileName}
              </button>
            );
          })}
        </div>

        {/* Raw markdown lines */}
        <div className="flex-1 overflow-y-auto p-4 bg-slate-950 text-slate-200 font-mono text-xs leading-6">
          {lines.map((line, index) => {
            const lineNum = index + 1;
            const isHighlighted =
              highlightedSource &&
              highlightedSource.file === current.fileName &&
              highlightedSource.line === lineNum;
            const flagsOnLine = lineFlags.get(lineNum) || [];
            const hasCritical = flagsOnLine.some((f) => f.severity === 'critical');
            const hasWarning = flagsOnLine.some((f) => f.severity === 'warning');

            return (
              <div
                key={lineNum}
                ref={isHighlighted ? highlightedLineRef : null}
                className={`flex items-start gap-4 px-3 py-0.5 rounded ${
                  isHighlighted
                    ? 'bg-emerald-900/60 ring-1 ring-emerald-400'
                    : hasCritical
                      ? 'bg-red-950/60'
                      : hasWarning
                        ? 'bg-amber-950/50'
                        : ''
                }`}
              >
                <span className="w-8 text-right text-slate-500 select-none shrink-0 tabular-nums">
                  {lineNum}
                </span>
                <div className="flex-1 min-w-0">
                  <span className="whitespace-pre-wrap break-words">{line || ' '}</span>
                  {flagsOnLine.length > 0 && (
                    <div className="mt-1 mb-1.5 space-y-1">
                      {flagsOnLine.map((flag) => (
                        <p
                          key={flag.id}
                          className={`text-[11px] font-sans px-2 py-1 rounded ${
                            flag.severity === 'critical'
                              ? 'bg-red-900/80 text-red-100'
                              : flag.severity === 'warning'
                                ? 'bg-amber-900/80 text-amber-100'
                                : 'bg-slate-800 text-slate-200'
                          }`}
                        >
                          [{flag.severity.toUpperCase()}] {flag.title}
                        </p>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
