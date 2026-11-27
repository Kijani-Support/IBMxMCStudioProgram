import { useCallback, useState } from 'react';
import { Alert } from '../../components/Alert';
import { DeliveryCard } from '../../components/DeliveryCard';
import { EmptyState } from '../../components/EmptyState';
import { LoadingState } from '../../components/LoadingState';
import { api, ApiError } from '../../lib/api';
import { usePolling } from '../../lib/usePolling';
import type { Order } from '../../lib/types';

export function RiderDashboardPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    try {
      const { orders: next } = await api.getOrders();
      setOrders(next);
      setError('');
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not load deliveries.');
    } finally {
      setLoading(false);
    }
  }, []);

  usePolling(load, 4000);

  const active = orders.filter((order) => order.status !== 'DELIVERED' && order.status !== 'CANCELLED');
  const done = orders.filter((order) => order.status === 'DELIVERED');

  if (loading) return <LoadingState label="Loading deliveries…" />;

  return (
    <div className="space-y-5">
      <div>
        <p className="text-sm font-semibold uppercase tracking-[0.16em] text-forest">Today</p>
        <h1 className="font-display text-4xl">Deliveries</h1>
        <p className="mt-1 text-sm text-muted">Only deliver when TrustPay shows payment confirmed.</p>
      </div>
      {error ? <Alert>{error}</Alert> : null}
      {active.length === 0 ? (
        <EmptyState title="No deliveries yet" body="Assigned deliveries will appear here." />
      ) : (
        <div className="space-y-4">
          {active.map((order) => (
            <DeliveryCard key={order.id} order={order} />
          ))}
        </div>
      )}
      {done.length > 0 ? (
        <section className="space-y-3">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-muted">Completed</h2>
          {done.map((order) => (
            <DeliveryCard key={order.id} order={order} />
          ))}
        </section>
      ) : null}
    </div>
  );
}
