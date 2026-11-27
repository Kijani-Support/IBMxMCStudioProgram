import { Bell } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';
import { usePolling } from '../lib/usePolling';
import type { Notification } from '../lib/types';
import { EmptyState } from './EmptyState';
import { NotificationItem } from './NotificationItem';

export function NotificationBell({
  inboxHref = '/rider/notifications'
}: {
  inboxHref?: string;
}) {
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const panelRef = useRef<HTMLDivElement>(null);

  usePolling(async () => {
    try {
      const { notifications: next } = await api.getNotifications();
      setNotifications(next);
    } catch {
      /* keep last known notifications while polling */
    }
  }, 4000);

  const unread = notifications.filter((item) => !item.read).length;

  useEffect(() => {
    function onClick(event: MouseEvent) {
      if (panelRef.current && !panelRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, []);

  async function openItem(notification: Notification) {
    if (!notification.read) {
      await api.markNotificationRead(notification.id);
      setNotifications((current) =>
        current.map((item) => (item.id === notification.id ? { ...item, read: true } : item))
      );
    }
    setOpen(false);
  }

  return (
    <div className="relative" ref={panelRef}>
      <button
        className="relative rounded-full p-2 text-ink hover:bg-sand"
        aria-label="Notifications"
        onClick={() => setOpen((value) => !value)}
      >
        <Bell className="h-5 w-5" />
        {unread > 0 ? (
          <span className="absolute -right-0.5 -top-0.5 min-w-4 rounded-full bg-alert px-1 text-[10px] font-bold text-white">
            {unread}
          </span>
        ) : null}
      </button>
      {open ? (
        <div className="absolute right-0 z-30 mt-2 w-[min(22rem,calc(100vw-2rem))] rounded-2xl border border-sand bg-white p-3 shadow-xl">
          <div className="mb-2 flex items-center justify-between">
            <p className="text-sm font-semibold">Notifications</p>
            <Link to={inboxHref} className="text-xs text-forest" onClick={() => setOpen(false)}>
              View all
            </Link>
          </div>
          {notifications.length === 0 ? (
            <EmptyState title="You're all caught up." body="Payment and delivery updates will appear here." />
          ) : (
            <div className="max-h-80 space-y-2 overflow-y-auto">
              {notifications.slice(0, 6).map((notification) => (
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
      ) : null}
    </div>
  );
}
