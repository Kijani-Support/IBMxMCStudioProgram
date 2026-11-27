import { formatOrderStatus } from '../lib/format';
import type { OrderStatus } from '../lib/types';

export function StatusBadge({ status }: { status: OrderStatus }) {
  const tone =
    status === 'DELIVERED'
      ? 'bg-ok-soft text-forest'
      : status === 'CANCELLED'
        ? 'bg-alert-soft text-alert'
        : 'bg-sand text-ink';

  return (
    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${tone}`}>
      {formatOrderStatus(status)}
    </span>
  );
}
