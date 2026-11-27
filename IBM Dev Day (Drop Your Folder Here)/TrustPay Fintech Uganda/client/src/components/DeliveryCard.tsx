import { Link } from 'react-router-dom';
import { formatPhone, formatUgx } from '../lib/format';
import type { Order } from '../lib/types';
import { PaymentStatus } from './PaymentStatus';

export function DeliveryCard({ order }: { order: Order }) {
  const paid = order.paymentStatus === 'PAID';
  const delivered = order.status === 'DELIVERED';

  return (
    <article className="rounded-2xl border border-sand bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <h2 className="font-display text-xl text-ink">{order.orderNumber}</h2>
        <PaymentStatus status={order.paymentStatus} orderStatus={order.status} />
      </div>
      <p className="mt-3 font-medium">{order.customerName}</p>
      <p className="text-sm text-muted">{formatPhone(order.customerPhone)}</p>
      <p className="mt-4 font-display text-3xl">{formatUgx(order.amount)}</p>

      <p className={`mt-4 text-sm font-semibold ${delivered || paid ? 'text-forest' : 'text-alert'}`}>
        {delivered
          ? '✓ Delivery completed'
          : paid
            ? '✓ You can proceed with delivery'
            : 'Do not complete delivery'}
      </p>

      <Link
        to={`/rider/deliveries/${order.id}`}
        className="mt-5 inline-flex w-full items-center justify-center rounded-xl bg-forest px-4 py-3 text-sm font-semibold text-white"
      >
        View Delivery
      </Link>
    </article>
  );
}
