import { useCallback, useState } from 'react';
import { Link } from 'react-router-dom';
import { EmptyState } from '../../components/EmptyState';
import { LoadingState } from '../../components/LoadingState';
import { PaymentStatus } from '../../components/PaymentStatus';
import { api } from '../../lib/api';
import { formatUgx } from '../../lib/format';
import { usePolling } from '../../lib/usePolling';
import type { Order } from '../../lib/types';

export function BusinessNotificationsPage() {
  const [orders, setOrders] = useState<Order[] | null>(null);

  const load = useCallback(async () => {
    try {
      const { orders: next } = await api.getOrders();
      setOrders(next.filter((order) => order.paymentStatus === 'PAID' || order.riderNotified));
    } catch {
      setOrders((current) => current ?? []);
    }
  }, []);

  usePolling(load, 5000);

  if (!orders) return <LoadingState label="Loading activity…" />;

  return (
    <div className="space-y-5">
      <div>
        <h1 className="font-display text-4xl">Notifications</h1>
        <p className="mt-1 text-sm text-muted">Payment confirmations sent to assigned riders.</p>
      </div>
      {orders.length === 0 ? (
        <EmptyState
          title="No payment alerts yet"
          body="When you confirm a payment, TrustPay notifies the rider and it will show up here."
        />
      ) : (
        <div className="space-y-3">
          {orders.map((order) => (
            <Link
              key={order.id}
              to={`/business/orders/${order.id}`}
              className="block rounded-2xl border border-sand bg-white p-4"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-display text-lg">{order.orderNumber}</p>
                  <p className="text-sm text-muted">
                    {formatUgx(order.amount)} · {order.rider?.name ?? 'No rider'}
                  </p>
                </div>
                <PaymentStatus status={order.paymentStatus} orderStatus={order.status} />
              </div>
              <p className={`mt-3 text-sm font-semibold ${order.riderNotified ? 'text-forest' : 'text-muted'}`}>
                {order.riderNotified ? '✓ Rider notified' : 'Rider not notified yet'}
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
