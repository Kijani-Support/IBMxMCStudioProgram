import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { homeForRole, useAuth } from './AuthContext';
import type { Role } from '../lib/types';
import { LoadingState } from '../components/LoadingState';

export function ProtectedRoute({ role }: { role?: Role }) {
  const { isAuthenticated, user, ready } = useAuth();
  const location = useLocation();

  if (!ready) {
    return <LoadingState label="Loading TrustPay…" />;
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  if (role && user.role !== role) {
    return <Navigate to={homeForRole(user.role)} replace />;
  }

  return <Outlet />;
}
