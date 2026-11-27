import { useState, ChangeEvent } from 'react';
import { X, Upload, FilePlus2 } from 'lucide-react';

interface ImportDossierModalProps {
  isOpen: boolean;
  onClose: () => void;
  onImportFiles: (items: Array<{ fileName: string; rawMarkdown: string }>) => void;
}

export function ImportDossierModal({
  isOpen,
  onClose,
  onImportFiles,
}: ImportDossierModalProps) {
  const [fileName, setFileName] = useState('');
  const [markdownText, setMarkdownText] = useState('');
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleFileInput = async (e: ChangeEvent<HTMLInputElement>) => {
    setError(null);
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    const mdFiles = files.filter((f) => f.name.toLowerCase().endsWith('.md'));
    if (mdFiles.length === 0) {
      setError('Please select one or more .md dossier files.');
      return;
    }

    const loaded = await Promise.all(
      mdFiles.map(async (f) => ({
        fileName: f.name,
        rawMarkdown: await f.text(),
      })),
    );
    onImportFiles(loaded);
    onClose();
  };

  const handlePasteSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!markdownText.trim()) {
      setError('Paste a country dossier markdown document before importing.');
      return;
    }
    const cleanName = (fileName.trim() || 'custom-country.md').endsWith('.md')
      ? fileName.trim() || 'custom-country.md'
      : `${fileName.trim()}.md`;

    onImportFiles([{ fileName: cleanName, rawMarkdown: markdownText }]);
    setFileName('');
    setMarkdownText('');
    onClose();
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Load markdown country dossiers"
      className="no-print fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-[1px]"
    >
      <div className="w-full max-w-xl bg-white border border-slate-200 rounded-xl shadow-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h2 className="text-base font-semibold text-slate-900">
              Load Country Dossier Markdown (.md)
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Drop any of the 54 africa-regulatory/*.md files or paste dossier markdown directly
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close import modal"
            className="p-2 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-lg cursor-pointer"
          >
            <X className="w-4 h-4" aria-hidden="true" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* File upload dropzone */}
          <div className="space-y-2">
            <label
              htmlFor="dossier-file-upload"
              className="flex flex-col items-center justify-center gap-2 p-6 border border-dashed border-slate-300 rounded-lg bg-slate-50 hover:bg-slate-100/70 transition-colors cursor-pointer text-center"
            >
              <Upload className="w-5 h-5 text-emerald-800" aria-hidden="true" />
              <span className="text-sm font-medium text-slate-800">
                Select one or more .md dossier files
              </span>
              <span className="text-xs text-slate-500">
                Supports multi-select (all 54 country dossiers at once)
              </span>
              <input
                id="dossier-file-upload"
                type="file"
                accept=".md,.markdown,.txt"
                multiple
                onChange={handleFileInput}
                className="sr-only"
              />
            </label>
          </div>

          <div className="relative flex items-center">
            <div className="flex-1 border-t border-slate-200" />
            <span className="px-3 text-xs text-slate-400">or paste dossier text</span>
            <div className="flex-1 border-t border-slate-200" />
          </div>

          {/* Paste form */}
          <form onSubmit={handlePasteSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="paste-filename"
                className="block text-xs font-medium text-slate-700 mb-1"
              >
                Dossier filename
              </label>
              <input
                id="paste-filename"
                type="text"
                placeholder="e.g. kenya.md"
                value={fileName}
                onChange={(e) => setFileName(e.target.value)}
                className="w-full h-10 px-3 border border-slate-300 rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-emerald-700"
              />
            </div>

            <div>
              <label
                htmlFor="paste-markdown"
                className="block text-xs font-medium text-slate-700 mb-1"
              >
                Markdown dossier content
              </label>
              <textarea
                id="paste-markdown"
                rows={6}
                placeholder="Paste country dossier following the 6-section template..."
                value={markdownText}
                onChange={(e) => setMarkdownText(e.target.value)}
                className="w-full p-3 border border-slate-300 rounded-lg text-xs font-mono focus:outline-none focus:ring-2 focus:ring-emerald-700"
              />
            </div>

            {error && (
              <p role="alert" className="text-xs font-medium text-red-700">
                {error}
              </p>
            )}

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={onClose}
                className="h-10 px-4 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="h-10 px-4 inline-flex items-center gap-2 text-xs font-medium text-white bg-emerald-800 hover:bg-emerald-900 rounded-lg cursor-pointer"
              >
                <FilePlus2 className="w-3.5 h-3.5" aria-hidden="true" />
                <span>Parse &amp; Add Dossier</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
