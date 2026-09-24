import { Link } from 'react-router-dom';
import { formatPhone, formatUgx } from '../lib/format';
import type { Order } from '../lib/types';
import { PaymentStatus } from './PaymentStatus';
import { StatusBadge } from './StatusBadge';

export function OrderCard({ order, href }: { order: Order; href: string }) {
  return (
    <Link
      to={href}
      className="block rounded-2xl border border-sand bg-white p-4 shadow-sm transition hover:border-forest/30"
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-display text-lg text-ink">{order.orderNumber}</p>
          <p className="mt-1 text-sm font-medium">{order.customerName}</p>
          <p className="text-sm text-muted">{formatPhone(order.customerPhone)}</p>
        </div>
        <StatusBadge status={order.status} />
      </div>
      <p className="mt-4 font-display text-2xl">{formatUgx(order.amount)}</p>
      <div className="mt-3">
        <PaymentStatus status={order.paymentStatus} orderStatus={order.status} />
      </div>
    </Link>
  );
}
