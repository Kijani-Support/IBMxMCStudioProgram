import { type FormEvent, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Alert } from '../../components/Alert';
import { Button } from '../../components/Button';
import { Input, Select } from '../../components/Input';
import { api, ApiError } from '../../lib/api';
import { toInternationalPhone } from '../../lib/format';
import type { RiderSummary } from '../../lib/types';

export function NewOrderPage() {
  const navigate = useNavigate();
  const [riders, setRiders] = useState<RiderSummary[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    void api
      .getRiders()
      .then((result) => setRiders(result.riders))
      .catch(() => setRiders([]));
  }, []);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const riderId = String(form.get('riderId') ?? '');
    setError('');
    setLoading(true);
    try {
      const { order } = await api.createOrder({
        customerName: String(form.get('customerName')),
        customerPhone: toInternationalPhone(String(form.get('customerPhone'))),
        amount: Number(form.get('amount'))
      });

      if (riderId) {
        await api.assignRider(order.id, riderId);
      }

      navigate(`/business/orders/${order.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not create the order.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-xl">
      <p className="text-sm font-semibold uppercase tracking-[0.16em] text-forest">New order</p>
      <h1 className="font-display text-4xl">Create a parcel order</h1>
      <p className="mt-2 text-sm text-muted">
        After the customer pays, TrustPay will notify the assigned rider automatically.
      </p>

      <form className="mt-6 space-y-4 rounded-3xl border border-sand bg-white p-5" onSubmit={onSubmit}>
        {error ? <Alert>{error}</Alert> : null}
        <Input label="Customer name" name="customerName" required placeholder="Sarah" />
        <Input
          label="Customer phone"
          name="customerPhone"
          required
          placeholder="+256700000003"
          hint="Include the country code"
        />
        <Input label="Amount (UGX)" name="amount" type="number" min={1} step={1} required placeholder="50000" />
        <Select
          label="Assign rider"
          name="riderId"
          hint={
            riders.length === 0
              ? 'No riders yet. Register a rider account, then return here.'
              : 'You can also assign a rider after creating the order.'
          }
        >
          <option value="">Assign later</option>
          {riders.map((rider) => (
            <option key={rider.id} value={rider.id}>
              {rider.name} · {rider.phone}
            </option>
          ))}
        </Select>
        <Button type="submit" loading={loading} className="w-full">
          Create order
        </Button>
      </form>
    </div>
  );
}
