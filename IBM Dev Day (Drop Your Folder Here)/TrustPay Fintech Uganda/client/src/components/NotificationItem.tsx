import { Link } from 'react-router-dom';
import type { Notification } from '../lib/types';

export function NotificationItem({
  notification,
  href,
  onOpen
}: {
  notification: Notification;
  href?: string;
  onOpen?: () => void;
}) {
  const content = (
    <div
      className={`rounded-xl border p-3 text-left ${
        notification.read ? 'border-sand bg-white' : 'border-forest/20 bg-ok-soft'
      }`}
    >
      <p className="text-sm font-semibold text-ink">{notification.title}</p>
      <p className="mt-1 whitespace-pre-line text-sm text-ink/80">{notification.message}</p>
    </div>
  );

  if (!href) {
    return (
      <button className="block w-full" onClick={onOpen}>
        {content}
      </button>
    );
  }

  return (
    <Link to={href} onClick={onOpen} className="block">
      {content}
    </Link>
  );
}
