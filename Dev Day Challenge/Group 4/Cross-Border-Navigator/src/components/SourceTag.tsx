import { FileText } from 'lucide-react';
import { SourceRef } from '../lib/types';

interface SourceTagProps {
  source: SourceRef;
  onInspect: (source: SourceRef) => void;
  compact?: boolean;
}

export function SourceTag({ source, onInspect, compact = false }: SourceTagProps) {
  const label = compact
    ? `${source.file} · L${source.line}`
    : `${source.file} · ${source.section} · L${source.line}`;

  return (
    <button
      type="button"
      onClick={() => onInspect(source)}
      title={`Inspect ${source.file} line ${source.line}: "${source.quote}"`}
      className="inline-flex items-center gap-1 font-mono text-[11px] text-slate-500 hover:text-emerald-800 underline decoration-slate-300 underline-offset-2 hover:decoration-emerald-600 transition-colors text-left cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-700 rounded-sm"
    >
      <FileText className="w-3 h-3 shrink-0 text-slate-400" aria-hidden="true" />
      <span className="tabular-nums">{label}</span>
    </button>
  );
}
