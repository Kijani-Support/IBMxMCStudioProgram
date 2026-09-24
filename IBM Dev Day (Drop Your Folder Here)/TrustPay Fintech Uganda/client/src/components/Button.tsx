import type { ButtonHTMLAttributes, ReactNode } from 'react';

type Variant = 'primary' | 'secondary' | 'danger' | 'ghost' | 'demo';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  loading?: boolean;
  children: ReactNode;
}

const styles: Record<Variant, string> = {
  primary:
    'bg-forest text-white hover:bg-forest-dark disabled:bg-sand disabled:text-muted',
  secondary:
    'bg-white text-ink border border-sand hover:border-forest/40 disabled:text-muted',
  danger: 'bg-alert text-white hover:bg-alert/90 disabled:bg-sand disabled:text-muted',
  ghost: 'bg-transparent text-ink hover:bg-sand/60 disabled:text-muted',
  demo: 'bg-ink text-paper hover:bg-ink/90 disabled:bg-sand disabled:text-muted'
};

export function Button({
  variant = 'primary',
  loading = false,
  className = '',
  disabled,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition disabled:cursor-not-allowed ${styles[variant]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? 'Please wait…' : children}
    </button>
  );
}
