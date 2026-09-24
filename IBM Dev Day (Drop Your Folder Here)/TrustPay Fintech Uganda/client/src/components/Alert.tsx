import type { ReactNode } from 'react';

export function Alert({
  children,
  tone = 'error'
}: {
  children: ReactNode;
  tone?: 'error' | 'ok';
}) {
  const classes =
    tone === 'ok'
      ? 'border-forest/20 bg-ok-soft text-forest'
      : 'border-alert/20 bg-alert-soft text-alert';

  return <div className={`rounded-xl border px-3 py-2 text-sm ${classes}`}>{children}</div>;
}
