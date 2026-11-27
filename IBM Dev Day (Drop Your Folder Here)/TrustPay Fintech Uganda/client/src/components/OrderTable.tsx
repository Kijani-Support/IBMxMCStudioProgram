import { Link } from 'react-router-dom';
import { formatPhone, formatUgx } from '../lib/format';
import type { Order } from '../lib/types';
import { PaymentStatus } from './PaymentStatus';
import { StatusBadge } from './StatusBadge';

export function OrderTable({ orders }: { orders: Order[] }) {
  return (
    <div className="overflow-hidden rounded-2xl border border-sand bg-white">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="bg-sand/50 text-xs uppercase tracking-wide text-muted">
            <tr>
              <th className="px-4 py-3 font-semibold">Order</th>
              <th className="px-4 py-3 font-semibold">Customer</th>
              <th className="px-4 py-3 font-semibold text-right">Amount</th>
              <th className="px-4 py-3 font-semibold">Rider</th>
              <th className="px-4 py-3 font-semibold">Payment</th>
              <th className="px-4 py-3 font-semibold">Status</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((order) => (
              <tr key={order.id} className="border-t border-sand/80 hover:bg-paper/60">
                <td className="px-4 py-3 font-semibold">
                  <Link to={`/business/orders/${order.id}`} className="text-forest hover:underline">
                    {order.orderNumber}
                  </Link>
                </td>
                <td className="px-4 py-3">
                  <div>{order.customerName}</div>
                  <div className="text-xs text-muted">{formatPhone(order.customerPhone)}</div>
                </td>
                <td className="px-4 py-3 text-right font-medium">{formatUgx(order.amount)}</td>
                <td className="px-4 py-3">{order.rider?.name ?? 'Unassigned'}</td>
                <td className="px-4 py-3">
                  <PaymentStatus status={order.paymentStatus} orderStatus={order.status} />
                </td>
                <td className="px-4 py-3">
                  <StatusBadge status={order.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
