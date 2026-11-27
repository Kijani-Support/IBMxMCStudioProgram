import type { InputHTMLAttributes, ReactNode, SelectHTMLAttributes, TextareaHTMLAttributes } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  hint?: string;
  addon?: ReactNode;
}

export function Input({ label, hint, addon, id, className = '', ...props }: InputProps) {
  const inputId = id ?? props.name;
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-medium text-ink">{label}</span>
      <span className="flex items-center rounded-xl border border-sand bg-white focus-within:border-forest focus-within:ring-2 focus-within:ring-forest/15">
        {addon ? <span className="pl-3 text-sm text-muted">{addon}</span> : null}
        <input
          id={inputId}
          className={`w-full bg-transparent px-3 py-2.5 text-sm outline-none ${className}`}
          {...props}
        />
      </span>
      {hint ? <span className="mt-1 block text-xs text-muted">{hint}</span> : null}
    </label>
  );
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label: string;
  hint?: string;
}

export function Select({ label, hint, id, children, ...props }: SelectProps) {
  const inputId = id ?? props.name;
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-medium text-ink">{label}</span>
      <select
        id={inputId}
        className="w-full rounded-xl border border-sand bg-white px-3 py-2.5 text-sm outline-none focus:border-forest focus:ring-2 focus:ring-forest/15"
        {...props}
      >
        {children}
      </select>
      {hint ? <span className="mt-1 block text-xs text-muted">{hint}</span> : null}
    </label>
  );
}

interface TextAreaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label: string;
}

export function TextArea({ label, id, ...props }: TextAreaProps) {
  const inputId = id ?? props.name;
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-medium text-ink">{label}</span>
      <textarea
        id={inputId}
        className="w-full rounded-xl border border-sand bg-white px-3 py-2.5 text-sm outline-none focus:border-forest focus:ring-2 focus:ring-forest/15"
        {...props}
      />
    </label>
  );
}
