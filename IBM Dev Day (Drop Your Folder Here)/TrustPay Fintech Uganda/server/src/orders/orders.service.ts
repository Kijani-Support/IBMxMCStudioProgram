import { store } from '../store/memory';
import { OrderStatus, PaymentStatus, Role, type Order } from '../types/domain';
import { getRiderById } from '../users/users.service';
import { AppError } from '../utils/errors';
import { generateOrderNumber } from '../utils/orderNumber';
import { serializeOrder } from '../utils/serialize';
import { notificationService } from '../notifications/notifications.service';
import type { AssignRiderInput, CreateOrderInput } from './orders.schemas';

export async function createOrder(businessId: string, input: CreateOrderInput) {
  const now = store.now();
  const order: Order = {
    id: store.id(),
    orderNumber: generateOrderNumber(),
    businessId,
    riderId: null,
    customerName: input.customerName,
    customerPhone: input.customerPhone,
    amount: input.amount,
    status: OrderStatus.PENDING,
    paymentStatus: PaymentStatus.PENDING,
    createdAt: now,
    updatedAt: now
  };

  store.orders.push(order);
  return serializeOrder(order);
}

export async function listOrders(userId: string, role: Role) {
  const orders = store.orders
    .filter((order) => (role === Role.BUSINESS ? order.businessId === userId : order.riderId === userId))
    .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());

  return orders.map(serializeOrder);
}

export async function getOrderForUser(orderId: string, userId: string, role: Role) {
  const order = store.findOrderById(orderId);
  if (!order) {
    throw new AppError(404, 'Order not found', 'ORDER_NOT_FOUND');
  }

  const allowed =
    (role === Role.BUSINESS && order.businessId === userId) ||
    (role === Role.RIDER && order.riderId === userId);

  if (!allowed) {
    throw new AppError(403, 'You do not have access to this order', 'FORBIDDEN');
  }

  return serializeOrder(order);
}

export async function assignRider(orderId: string, businessId: string, input: AssignRiderInput) {
  const order = store.findOrderById(orderId);
  if (!order) {
    throw new AppError(404, 'Order not found', 'ORDER_NOT_FOUND');
  }

  if (order.businessId !== businessId) {
    throw new AppError(403, 'You do not have access to this order', 'FORBIDDEN');
  }

  if (order.status === OrderStatus.DELIVERED) {
    throw new AppError(409, 'Cannot assign a rider to a delivered order', 'ORDER_DELIVERED');
  }

  if (order.status === OrderStatus.CANCELLED) {
    throw new AppError(409, 'Cannot assign a rider to a cancelled order', 'ORDER_CANCELLED');
  }

  const rider = await getRiderById(input.riderId);
  order.riderId = rider.id;
  order.status = OrderStatus.ASSIGNED;
  order.updatedAt = store.now();

  if (order.paymentStatus === PaymentStatus.PAID) {
    await notificationService.notifyPaymentConfirmed(order);
  }

  return serializeOrder(order);
}
