import { useAuth } from '../../auth/AuthContext';
import { Button } from '../../components/Button';

export function RiderProfilePage() {
  const { user, logout } = useAuth();

  return (
    <div className="space-y-5">
      <h1 className="font-display text-4xl">Profile</h1>
      <section className="rounded-2xl border border-sand bg-white p-5">
        <p className="text-xs uppercase tracking-wide text-muted">Rider</p>
        <p className="mt-1 font-display text-2xl">{user?.name}</p>
        <p className="mt-3 text-sm">{user?.email}</p>
        <p className="text-sm text-muted">{user?.phone}</p>
      </section>
      <Button variant="secondary" className="w-full" onClick={logout}>
        Log out
      </Button>
    </div>
  );
}
