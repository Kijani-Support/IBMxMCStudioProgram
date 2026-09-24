import { type FormEvent, useCallback, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Alert } from '../../components/Alert';
import { Button } from '../../components/Button';
import { LoadingState } from '../../components/LoadingState';
import { PaymentStatus } from '../../components/PaymentStatus';
import { Select } from '../../components/Input';
import { api, ApiError } from '../../lib/api';
import { formatPhone, formatUgx } from '../../lib/format';
import { usePolling } from '../../lib/usePolling';
import type { Order, RiderSummary } from '../../lib/types';

export function OrderDetailPage() {
  const { id } = useParams();
  const [order, setOrder] = useState<Order | null>(null);
  const [riders, setRiders] = useState<RiderSummary[]>([]);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [loading, setLoading] = useState(true);
  const [assigning, setAssigning] = useState(false);
  const [simulating, setSimulating] = useState(false);

  const load = useCallback(async () => {
    if (!id) return;
    try {
      const { order: next } = await api.getOrder(id);
      setOrder(next);
      setError('');
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Order not found.');
      setOrder(null);
    } finally {
      setLoading(false);
    }
  }, [id]);

  usePolling(load, 4000, Boolean(id));

  useEffect(() => {
    void api
      .getRiders()
      .then((result) => setRiders(result.riders))
      .catch(() => setRiders([]));
  }, []);

  async function onAssign(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!order) return;
    const riderId = String(new FormData(event.currentTarget).get('riderId'));
    if (!riderId) return;
    setAssigning(true);
    setError('');
    try {
      const { order: next } = await api.assignRider(order.id, riderId);
      setOrder(next);
      setNotice('Rider assigned.');
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not assign rider.');
    } finally {
      setAssigning(false);
    }
  }

  async function onSimulatePayment() {
    if (!order) return;
    setSimulating(true);
    setError('');
    setNotice('');
    try {
      const result = await api.simulatePayment(order);
      if (result.matched === false) {
        setError(result.message ?? 'Payment could not be matched to this order.');
      } else {
        setNotice(
          result.notificationCreated
            ? 'Payment confirmed. The rider has been notified.'
            : 'Payment confirmed.'
        );
      }
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not simulate payment.');
    } finally {
      setSimulating(false);
    }
  }

  if (loading) return <LoadingState label="Loading order…" />;
  if (!order) {
    return (
      <div className="space-y-4">
        <Alert>{error || 'Unknown order.'}</Alert>
        <Link to="/business" className="text-sm font-semibold text-forest">
          Back to dashboard
        </Link>
      </div>
    );
  }

  const canSimulate = order.paymentStatus !== 'PAID' && order.status !== 'DELIVERED';

  return (
    <div className="mx-auto max-w-2xl space-y-5">
      <Link to="/business" className="text-sm font-semibold text-forest">
        ← Dashboard
      </Link>
      <div>
        <p className="text-sm font-semibold uppercase tracking-[0.16em] text-forest">Order</p>
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

      <section className="grid gap-4 rounded-2xl border border-sand bg-white p-5 sm:grid-cols-2">
        <Field label="Customer" value={order.customerName} detail={formatPhone(order.customerPhone)} />
        <Field label="Amount" value={formatUgx(order.amount)} />
        <Field
          label="Rider"
          value={order.rider?.name ?? 'Not assigned'}
          detail={order.rider ? formatPhone(order.rider.phone) : 'Assign a rider so they can be notified.'}
        />
        <div>
          <p className="text-xs uppercase tracking-wide text-muted">Rider notification</p>
          <p className={`mt-1 font-semibold ${order.riderNotified ? 'text-forest' : 'text-muted'}`}>
            {order.riderNotified ? '✓ Rider notified' : 'Rider not notified yet'}
          </p>
        </div>
      </section>

      {!order.riderId ? (
        <form className="space-y-3 rounded-2xl border border-sand bg-white p-5" onSubmit={onAssign}>
          <h2 className="font-display text-xl">Assign a rider</h2>
          <Select name="riderId" label="Rider" required>
            <option value="">Select rider</option>
            {riders.map((rider) => (
              <option key={rider.id} value={rider.id}>
                {rider.name} · {rider.phone}
              </option>
            ))}
          </Select>
          <Button type="submit" loading={assigning}>
            Assign rider
          </Button>
        </form>
      ) : null}

      {canSimulate ? (
        <section className="rounded-2xl border border-dashed border-ink/20 bg-ink p-5 text-paper">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-sand">Demo only</p>
          <h2 className="mt-1 font-display text-2xl">Demo: Simulate Payment</h2>
          <p className="mt-2 text-sm text-paper/75">
            This is not a real payment. It sends the mock webhook so you can show rider notification in
            the demo.
          </p>
          <Button
            variant="demo"
            className="mt-4 bg-paper text-ink hover:bg-white"
            loading={simulating}
            onClick={() => void onSimulatePayment()}
          >
            Simulate payment received
          </Button>
        </section>
      ) : null}
    </div>
  );
}

function Field({ label, value, detail }: { label: string; value: string; detail?: string }) {
  return (
    <div>
      <p className="text-xs uppercase tracking-wide text-muted">{label}</p>
      <p className="mt-1 font-semibold">{value}</p>
      {detail ? <p className="text-sm text-muted">{detail}</p> : null}
    </div>
  );
}
