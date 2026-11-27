import { Bell, Package, UserRound } from 'lucide-react';
import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { BrandMark } from '../components/BrandMark';
import { NotificationBell } from '../components/NotificationBell';

const tabs = [
  { to: '/rider', label: 'Deliveries', icon: Package, end: true },
  { to: '/rider/notifications', label: 'Notifications', icon: Bell, end: false },
  { to: '/rider/profile', label: 'Profile', icon: UserRound, end: false }
];

export function RiderLayout() {
  const { user } = useAuth();

  return (
    <div className="mx-auto min-h-screen max-w-lg bg-transparent pb-24">
      <header className="sticky top-0 z-20 flex items-center justify-between border-b border-sand bg-paper/90 px-4 py-3 backdrop-blur">
        <BrandMark />
        <div className="flex items-center gap-2">
          <p className="hidden text-sm font-medium sm:block">{user?.name}</p>
          <NotificationBell />
        </div>
      </header>
      <main className="px-4 py-5">
        <Outlet />
      </main>
      <nav className="fixed inset-x-0 bottom-0 z-20 border-t border-sand bg-white/95 pb-[env(safe-area-inset-bottom)] backdrop-blur">
        <div className="mx-auto grid max-w-lg grid-cols-3">
          {tabs.map((tab) => (
            <NavLink
              key={tab.to}
              to={tab.to}
              end={tab.end}
              className={({ isActive }) =>
                `flex flex-col items-center gap-1 py-3 text-xs font-medium ${isActive ? 'text-forest' : 'text-muted'}`
              }
            >
              <tab.icon className="h-5 w-5" />
              {tab.label}
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  );
}
