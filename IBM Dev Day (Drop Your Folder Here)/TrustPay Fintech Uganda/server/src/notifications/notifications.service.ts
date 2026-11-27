import { store } from '../store/memory';
import type { Order } from '../types/domain';
import { AppError } from '../utils/errors';
import { formatUgx } from '../utils/money';
import { notificationChannels } from './channels';
import type { NotificationPayload } from './channels/NotificationChannel';

class NotificationService {
  async notifyPaymentConfirmed(order: Order): Promise<void> {
    if (!order.riderId) {
      return;
    }

    const payload: NotificationPayload = {
      riderId: order.riderId,
      orderId: order.id,
      type: 'PAYMENT_CONFIRMED',
      title: 'Payment Confirmed',
      message: [
        `Order ${order.orderNumber} has been paid successfully.`,
        `Amount: ${formatUgx(order.amount)}.`,
        'You can proceed with the delivery.'
      ].join('\n')
    };

    await Promise.all(notificationChannels.map((channel) => channel.send(payload)));
  }

  async listForRider(riderId: string, unreadOnly = false) {
    return store.notifications
      .filter((notification) => notification.riderId === riderId && (!unreadOnly || !notification.read))
      .sort((a, b) => {
        if (a.read !== b.read) return Number(a.read) - Number(b.read);
        return b.createdAt.getTime() - a.createdAt.getTime();
      });
  }

  async markRead(notificationId: string, riderId: string) {
    const notification = store.findNotification(notificationId);
    if (!notification || notification.riderId !== riderId) {
      throw new AppError(404, 'Notification not found', 'NOTIFICATION_NOT_FOUND');
    }

    notification.read = true;
    return notification;
  }
}

export const notificationService = new NotificationService();
