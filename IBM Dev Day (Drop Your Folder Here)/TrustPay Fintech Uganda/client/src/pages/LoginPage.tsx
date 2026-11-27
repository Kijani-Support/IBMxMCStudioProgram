import { type FormEvent, useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { homeForRole, useAuth } from '../auth/AuthContext';
import { Alert } from '../components/Alert';
import { BrandMark } from '../components/BrandMark';
import { Button } from '../components/Button';
import { Input, Select } from '../components/Input';
import { ApiError } from '../lib/api';
import { toInternationalPhone } from '../lib/format';
import type { Role } from '../lib/types';

export function LoginPage() {
  const { login, register, isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [role, setRole] = useState<Role>('BUSINESS');

  if (isAuthenticated && user) {
    return <Navigate to={homeForRole(user.role)} replace />;
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setError('');
    setLoading(true);
    try {
      if (mode === 'login') {
        const nextUser = await login(String(form.get('email')), String(form.get('password')));
        navigate(homeForRole(nextUser.role), { replace: true });
        return;
      }

      const nextUser = await register({
        name: String(form.get('name')),
        phone: toInternationalPhone(String(form.get('phone'))),
        email: String(form.get('email')),
        password: String(form.get('password')),
        role
      });
      navigate(homeForRole(nextUser.role), { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not sign you in.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto grid min-h-screen max-w-6xl lg:grid-cols-2">
      <section className="hidden flex-col justify-between p-10 lg:flex">
        <BrandMark />
        <div className="max-w-md">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-forest">Uganda · Fintech</p>
          <h1 className="mt-4 font-display text-5xl leading-tight">
            Payment confirmed.
            <br />
            Rider notified.
          </h1>
          <p className="mt-5 text-lg text-muted">
            TrustPay tells the rider the moment a parcel is paid for — so delivery never depends on a
            customer’s word.
          </p>
        </div>
        <p className="text-sm text-muted">Payment received → Rider notified → Delivery can proceed</p>
      </section>

      <section className="flex items-center justify-center p-5 sm:p-10">
        <div className="w-full max-w-md rounded-3xl border border-sand bg-white p-6 shadow-sm">
          <div className="mb-6 lg:hidden">
            <BrandMark />
          </div>
          <h2 className="font-display text-3xl">{mode === 'login' ? 'Welcome back' : 'Create account'}</h2>
          <p className="mt-1 text-sm text-muted">
            {mode === 'login'
              ? 'Sign in to your business or rider workspace.'
              : 'Create a Business account and a Rider account to run the demo.'}
          </p>

          <div className="mt-5 grid grid-cols-2 rounded-xl bg-sand p-1 text-sm font-semibold">
            <button
              className={`rounded-lg py-2 ${mode === 'login' ? 'bg-white text-ink' : 'text-muted'}`}
              onClick={() => setMode('login')}
              type="button"
            >
              Log in
            </button>
            <button
              className={`rounded-lg py-2 ${mode === 'register' ? 'bg-white text-ink' : 'text-muted'}`}
              onClick={() => setMode('register')}
              type="button"
            >
              Register
            </button>
          </div>

          <form className="mt-6 space-y-4" onSubmit={onSubmit}>
            {error ? <Alert>{error}</Alert> : null}
            {mode === 'register' ? (
              <>
                <Input label="Name" name="name" required minLength={2} placeholder="Kampala Parcels" />
                <Input
                  label="Phone"
                  name="phone"
                  required
                  placeholder="+256700000001"
                  hint="Include the country code"
                />
                <Select label="Role" value={role} onChange={(event) => setRole(event.target.value as Role)}>
                  <option value="BUSINESS">Business owner</option>
                  <option value="RIDER">Rider</option>
                </Select>
              </>
            ) : null}
            <Input label="Email" name="email" type="email" required placeholder="you@business.ug" />
            <Input label="Password" name="password" type="password" required minLength={mode === 'register' ? 8 : 1} />
            <Button type="submit" loading={loading} className="w-full">
              {mode === 'login' ? 'Log in' : 'Create account'}
            </Button>
          </form>

          {import.meta.env.DEV ? (
            <div className="mt-5 rounded-xl bg-paper px-3 py-3 text-xs text-muted">
              <p className="font-semibold text-ink">Demo accounts (in-memory)</p>
              <p className="mt-1">Business: business@trustpay.test / password123</p>
              <p>Rider: john@trustpay.test / password123</p>
              <p className="mt-2">
                Each tab keeps its own login. Open a second tab, sign in as the rider, and watch
                payment confirmation arrive.
              </p>
            </div>
          ) : null}
        </div>
      </section>
    </div>
  );
}
