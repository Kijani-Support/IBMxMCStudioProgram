import { useCallback, useState } from 'react';
import { api } from '../../lib/api';
import { usePolling } from '../../lib/usePolling';
import type { Notification } from '../../lib/types';
import { EmptyState } from '../../components/EmptyState';
import { LoadingState } from '../../components/LoadingState';
import { NotificationItem } from '../../components/NotificationItem';

export function RiderNotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[] | null>(null);

  const load = useCallback(async () => {
    try {
      const { notifications: next } = await api.getNotifications();
      setNotifications(next);
    } catch {
      setNotifications((current) => current ?? []);
    }
  }, []);

  usePolling(load, 4000);

  async function openItem(notification: Notification) {
    if (!notification.read) {
      await api.markNotificationRead(notification.id);
      setNotifications((current) =>
        current?.map((item) => (item.id === notification.id ? { ...item, read: true } : item)) ?? null
      );
    }
  }

  if (!notifications) return <LoadingState label="Loading notifications…" />;

  return (
    <div className="space-y-5">
      <h1 className="font-display text-4xl">Notifications</h1>
      {notifications.length === 0 ? (
        <EmptyState title="You're all caught up." body="Payment and delivery updates will appear here." />
      ) : (
        <div className="space-y-3">
          {notifications.map((notification) => (
            <NotificationItem
              key={notification.id}
              notification={notification}
              href={`/rider/deliveries/${notification.orderId}`}
              onOpen={() => void openItem(notification)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
