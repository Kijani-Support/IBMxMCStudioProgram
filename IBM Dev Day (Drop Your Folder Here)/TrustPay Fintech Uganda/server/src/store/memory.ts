import { randomUUID } from 'crypto';
import type { Notification, Order, Payment, User } from '../types/domain';

export class MemoryStore {
  users: User[] = [];
  orders: Order[] = [];
  payments: Payment[] = [];
  notifications: Notification[] = [];

  id(): string {
    return randomUUID();
  }

  now(): Date {
    return new Date();
  }

  reset(): void {
    this.users = [];
    this.orders = [];
    this.payments = [];
    this.notifications = [];
  }

  findUserById(id: string): User | undefined {
    return this.users.find((user) => user.id === id);
  }

  findUserByEmail(email: string): User | undefined {
    return this.users.find((user) => user.email === email);
  }

  findUserByPhone(phone: string): User | undefined {
    return this.users.find((user) => user.phone === phone);
  }

  findOrderById(id: string): Order | undefined {
    return this.orders.find((order) => order.id === id);
  }

  findOrderByNumber(orderNumber: string): Order | undefined {
    return this.orders.find((order) => order.orderNumber === orderNumber);
  }

  findPaymentByReference(transactionReference: string): Payment | undefined {
    return this.payments.find((payment) => payment.transactionReference === transactionReference);
  }

  findNotification(id: string): Notification | undefined {
    return this.notifications.find((notification) => notification.id === id);
  }

  hasPaymentNotification(orderId: string, riderId: string): boolean {
    return this.notifications.some(
      (notification) =>
        notification.orderId === orderId &&
        notification.riderId === riderId &&
        notification.type === 'PAYMENT_CONFIRMED'
    );
  }
}

export const store = new MemoryStore();
