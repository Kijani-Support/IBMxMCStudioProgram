import { store } from '../../store/memory';
import { NotificationType } from '../../types/domain';
import type { NotificationChannel, NotificationPayload } from './NotificationChannel';

export class InAppNotificationChannel implements NotificationChannel {
  readonly name = 'in-app';

  async send(payload: NotificationPayload): Promise<void> {
    if (store.hasPaymentNotification(payload.orderId, payload.riderId)) {
      return;
    }

    store.notifications.push({
      id: store.id(),
      riderId: payload.riderId,
      orderId: payload.orderId,
      type: NotificationType.PAYMENT_CONFIRMED,
      title: payload.title,
      message: payload.message,
      read: false,
      createdAt: store.now()
    });
  }
}
