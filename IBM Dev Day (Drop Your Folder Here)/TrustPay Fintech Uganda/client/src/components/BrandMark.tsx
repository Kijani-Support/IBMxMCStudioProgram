import { Link } from 'react-router-dom';

export function BrandMark({ compact = false }: { compact?: boolean }) {
  return (
    <Link to="/" className="flex items-center gap-2 text-ink">
      <span className="grid h-8 w-8 place-items-center rounded-lg bg-forest font-display text-sm text-white">
        T
      </span>
      {compact ? null : (
        <span className="leading-tight">
          <span className="block font-display text-lg">TrustPay</span>
          <span className="block text-[10px] uppercase tracking-[0.18em] text-muted">Uganda</span>
        </span>
      )}
    </Link>
  );
}
