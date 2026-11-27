import { CircleCheck, CircleX } from 'lucide-react';
import { formatUgx } from '../lib/format';
import type { OrderStatus, PaymentStatusValue } from '../lib/types';

interface PaymentStatusProps {
  status: PaymentStatusValue;
  orderStatus?: OrderStatus;
  amount?: number;
  variant?: 'badge' | 'banner';
}

export function PaymentStatus({
  status,
  orderStatus,
  amount,
  variant = 'badge'
}: PaymentStatusProps) {
  if (orderStatus === 'DELIVERED') {
    if (variant === 'banner') {
      return (
        <section className="rounded-2xl border border-forest/20 bg-ok-soft p-5">
          <p className="flex items-center gap-2 text-lg font-semibold text-forest">
            <CircleCheck className="h-6 w-6" />
            DELIVERY COMPLETED
          </p>
          <p className="mt-2 text-sm text-ink/80">This order has been successfully delivered.</p>
        </section>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-ok-soft px-2.5 py-1 text-xs font-semibold text-forest">
        <CircleCheck className="h-3.5 w-3.5" />
        Delivered
      </span>
    );
  }

  if (status === 'PAID') {
    if (variant === 'banner') {
      return (
        <section className="rounded-2xl border border-forest/25 bg-ok-soft p-5 shadow-[inset_0_1px_0_rgba(255,255,255,0.6)]">
          <p className="flex items-center gap-2 text-lg font-semibold tracking-wide text-forest">
            <span aria-hidden>🟢</span> PAYMENT CONFIRMED
          </p>
          {amount != null ? (
            <p className="mt-2 font-display text-2xl text-ink">{formatUgx(amount)}</p>
          ) : null}
          <p className="mt-2 text-sm leading-6 text-ink/80">
            Payment received successfully.
            <br />
            You can safely hand over the parcel.
          </p>
        </section>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-ok-soft px-2.5 py-1 text-xs font-semibold text-forest">
        <span aria-hidden>🟢</span> Paid
      </span>
    );
  }

  if (status === 'FAILED') {
    if (variant === 'banner') {
      return (
        <section className="rounded-2xl border border-alert/20 bg-alert-soft p-5">
          <p className="flex items-center gap-2 text-lg font-semibold text-alert">
            <CircleX className="h-6 w-6" />
            PAYMENT FAILED
          </p>
          <p className="mt-2 text-sm text-ink/80">
            TrustPay could not confirm this payment. Do not complete delivery.
          </p>
        </section>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-alert-soft px-2.5 py-1 text-xs font-semibold text-alert">
        <CircleX className="h-3.5 w-3.5" />
        Failed
      </span>
    );
  }

  if (variant === 'banner') {
    return (
      <section className="rounded-2xl border border-alert/20 bg-alert-soft p-5">
        <p className="flex items-center gap-2 text-lg font-semibold tracking-wide text-alert">
          <span aria-hidden>🔴</span> PAYMENT PENDING
        </p>
        {amount != null ? (
          <p className="mt-2 font-display text-2xl text-ink">{formatUgx(amount)}</p>
        ) : null}
        <p className="mt-2 text-sm leading-6 text-ink/80">
          Payment has not yet been confirmed.
          <br />
          Do not complete delivery.
        </p>
      </section>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-alert-soft px-2.5 py-1 text-xs font-semibold text-alert">
      <span aria-hidden>🔴</span> Pending
    </span>
  );
}
