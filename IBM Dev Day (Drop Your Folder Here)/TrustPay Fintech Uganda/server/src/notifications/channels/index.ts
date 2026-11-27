import { InAppNotificationChannel } from './InAppChannel';
import type { NotificationChannel } from './NotificationChannel';

export const notificationChannels: NotificationChannel[] = [new InAppNotificationChannel()];
