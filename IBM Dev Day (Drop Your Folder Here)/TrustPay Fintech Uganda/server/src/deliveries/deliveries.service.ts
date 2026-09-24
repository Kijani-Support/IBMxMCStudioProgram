import { store } from '../store/memory';
import { OrderStatus, PaymentStatus } from '../types/domain';
import { AppError } from '../utils/errors';
import { serializeOrder } from '../utils/serialize';

export async function confirmDelivery(orderId: string, riderId: string) {
  const order = store.findOrderById(orderId);

  if (!order) {
    throw new AppError(404, 'Order not found', 'ORDER_NOT_FOUND');
  }

  if (order.riderId !== riderId) {
    throw new AppError(403, 'You are not assigned to this order', 'FORBIDDEN');
  }

  if (order.status === OrderStatus.DELIVERED) {
    throw new AppError(409, 'Delivery has already been confirmed.', 'ALREADY_DELIVERED');
  }

  if (order.status === OrderStatus.CANCELLED) {
    throw new AppError(409, 'This order has been cancelled.', 'ORDER_CANCELLED');
  }

  if (order.paymentStatus !== PaymentStatus.PAID) {
    throw new AppError(
      409,
      'Payment has not been confirmed. Delivery cannot be completed.',
      'PAYMENT_NOT_CONFIRMED'
    );
  }

  order.status = OrderStatus.DELIVERED;
  order.updatedAt = store.now();

  return {
    message: 'Delivery confirmed successfully.',
    order: serializeOrder(order)
  };
}
