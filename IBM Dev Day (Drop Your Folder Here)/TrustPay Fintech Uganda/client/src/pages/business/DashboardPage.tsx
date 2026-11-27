import { useCallback, useState } from 'react';
import { Link } from 'react-router-dom';
import { Alert } from '../../components/Alert';
import { Button } from '../../components/Button';
import { EmptyState } from '../../components/EmptyState';
import { LoadingState } from '../../components/LoadingState';
import { OrderCard } from '../../components/OrderCard';
import { OrderTable } from '../../components/OrderTable';
import { api, ApiError } from '../../lib/api';
import { usePolling } from '../../lib/usePolling';
import type { Order } from '../../lib/types';

export function BusinessDashboardPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    try {
      const { orders: next } = await api.getOrders();
      setOrders(next);
      setError('');
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not load orders.');
    } finally {
      setLoading(false);
    }
  }, []);

  usePolling(load, 5000);

  const pending = orders.filter((order) => order.paymentStatus === 'PENDING').length;
  const paid = orders.filter((order) => order.paymentStatus === 'PAID').length;
  const delivered = orders.filter((order) => order.status === 'DELIVERED').length;

  if (loading) return <LoadingState label="Loading orders…" />;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.16em] text-forest">Business</p>
          <h1 className="font-display text-4xl">Orders</h1>
          <p className="mt-1 text-sm text-muted">Payment status is the source of truth for every delivery.</p>
        </div>
        <Link to="/business/orders/new">
          <Button>New order</Button>
        </Link>
      </div>

      {error ? <Alert>{error}</Alert> : null}

      <section className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <SummaryCard label="Total orders" value={orders.length} />
        <SummaryCard label="Pending payment" value={pending} tone="alert" />
        <SummaryCard label="Paid" value={paid} tone="ok" />
        <SummaryCard label="Delivered" value={delivered} />
      </section>

      {orders.length === 0 ? (
        <EmptyState
          title="No orders yet"
          body="Create an order, assign a rider, then simulate payment to notify them."
          action={
            <Link to="/business/orders/new">
              <Button>Create first order</Button>
            </Link>
          }
        />
      ) : (
        <>
          <div className="hidden md:block">
            <OrderTable orders={orders} />
          </div>
          <div className="grid gap-3 md:hidden">
            {orders.map((order) => (
              <OrderCard key={order.id} order={order} href={`/business/orders/${order.id}`} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

function SummaryCard({
  label,
  value,
  tone
}: {
  label: string;
  value: number;
  tone?: 'ok' | 'alert';
}) {
  const color = tone === 'ok' ? 'text-forest' : tone === 'alert' ? 'text-alert' : 'text-ink';
  return (
    <div className="rounded-2xl border border-sand bg-white p-4">
      <p className="text-xs uppercase tracking-wide text-muted">{label}</p>
      <p className={`mt-2 font-display text-3xl ${color}`}>{value}</p>
    </div>
  );
}
