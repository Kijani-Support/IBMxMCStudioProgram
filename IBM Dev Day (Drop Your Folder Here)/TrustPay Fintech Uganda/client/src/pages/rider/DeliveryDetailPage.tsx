import { useCallback, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Alert } from '../../components/Alert';
import { Button } from '../../components/Button';
import { LoadingState } from '../../components/LoadingState';
import { PaymentStatus } from '../../components/PaymentStatus';
import { api, ApiError } from '../../lib/api';
import { formatPhone, formatUgx } from '../../lib/format';
import { usePolling } from '../../lib/usePolling';
import type { Order } from '../../lib/types';

export function DeliveryDetailPage() {
  const { id } = useParams();
  const [order, setOrder] = useState<Order | null>(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [loading, setLoading] = useState(true);
  const [confirming, setConfirming] = useState(false);

  const load = useCallback(async () => {
    if (!id) return;
    try {
      const { order: next } = await api.getOrder(id);
      setOrder(next);
      setError('');
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Delivery not found.');
      setOrder(null);
    } finally {
      setLoading(false);
    }
  }, [id]);

  usePolling(load, 4000, Boolean(id));

  async function onConfirm() {
    if (!order) return;
    setConfirming(true);
    setError('');
    try {
      const result = await api.confirmDelivery(order.id);
      setOrder(result.order);
      setNotice(result.message);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not confirm delivery.');
    } finally {
      setConfirming(false);
    }
  }

  if (loading) return <LoadingState label="Loading delivery…" />;
  if (!order) {
    return (
      <div className="space-y-4">
        <Alert>{error || 'Unknown delivery.'}</Alert>
        <Link to="/rider" className="text-sm font-semibold text-forest">
          Back to deliveries
        </Link>
      </div>
    );
  }

  const canDeliver = order.paymentStatus === 'PAID' && order.status !== 'DELIVERED';

  return (
    <div className="space-y-5">
      <Link to="/rider" className="text-sm font-semibold text-forest">
        ← Deliveries
      </Link>
      <div>
        <p className="text-sm font-semibold uppercase tracking-[0.16em] text-forest">Delivery</p>
        <h1 className="font-display text-4xl">{order.orderNumber}</h1>
      </div>

      {error ? <Alert>{error}</Alert> : null}
      {notice ? <Alert tone="ok">{notice}</Alert> : null}

      <PaymentStatus
        status={order.paymentStatus}
        orderStatus={order.status}
        amount={order.amount}
        variant="banner"
      />

      <section className="rounded-2xl border border-sand bg-white p-5">
        <p className="text-xs uppercase tracking-wide text-muted">Customer</p>
        <p className="mt-1 text-lg font-semibold">{order.customerName}</p>
        <p className="text-muted">{formatPhone(order.customerPhone)}</p>
        <p className="mt-4 text-xs uppercase tracking-wide text-muted">Amount</p>
        <p className="font-display text-2xl">{formatUgx(order.amount)}</p>
      </section>

      {order.status === 'DELIVERED' ? null : canDeliver ? (
        <Button className="w-full py-3.5 text-base" loading={confirming} onClick={() => void onConfirm()}>
          Confirm delivery
        </Button>
      ) : (
        <div className="rounded-2xl border border-alert/20 bg-alert-soft p-4 text-sm text-alert">
          You cannot complete this delivery yet. Wait for payment confirmation.
        </div>
      )}
    </div>
  );
}
