import { store } from '../store/memory';
import { PaymentStatus, type Order, type Payment, type User } from '../types/domain';

export function omitPasswordHash<T extends { passwordHash: string }>(
  user: T
): Omit<T, 'passwordHash'> {
  const { passwordHash: _passwordHash, ...safeUser } = user;
  return safeUser;
}

export function serializeUser(user: User) {
  return omitPasswordHash(user);
}

export function serializeOrder(order: Order) {
  const riderUser = order.riderId ? store.findUserById(order.riderId) : undefined;
  const rider = riderUser
    ? { id: riderUser.id, name: riderUser.name, phone: riderUser.phone }
    : null;

  return {
    id: order.id,
    orderNumber: order.orderNumber,
    businessId: order.businessId,
    riderId: order.riderId,
    rider,
    customerName: order.customerName,
    customerPhone: order.customerPhone,
    amount: order.amount,
    currency: 'UGX' as const,
    status: order.status,
    paymentStatus: order.paymentStatus,
    safeToDeliver: order.paymentStatus === PaymentStatus.PAID,
    riderNotified: Boolean(
      order.riderId && store.hasPaymentNotification(order.id, order.riderId)
    ),
    createdAt: order.createdAt,
    updatedAt: order.updatedAt
  };
}

export function serializePayment(payment: Payment) {
  return { ...payment };
}
