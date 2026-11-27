import { Navigate, Route, Routes } from 'react-router-dom';
import { homeForRole, useAuth } from './auth/AuthContext';
import { ProtectedRoute } from './auth/ProtectedRoute';
import { LoadingState } from './components/LoadingState';
import { BusinessLayout } from './layouts/BusinessLayout';
import { RiderLayout } from './layouts/RiderLayout';
import { LoginPage } from './pages/LoginPage';
import { BusinessDashboardPage } from './pages/business/DashboardPage';
import { NewOrderPage } from './pages/business/NewOrderPage';
import { BusinessNotificationsPage } from './pages/business/NotificationsPage';
import { OrderDetailPage } from './pages/business/OrderDetailPage';
import { BusinessProfilePage } from './pages/business/ProfilePage';
import { RiderDashboardPage } from './pages/rider/DashboardPage';
import { DeliveryDetailPage } from './pages/rider/DeliveryDetailPage';
import { RiderNotificationsPage } from './pages/rider/NotificationsPage';
import { RiderProfilePage } from './pages/rider/ProfilePage';

function HomeRedirect() {
  const { isAuthenticated, user, ready } = useAuth();
  if (!ready) return <LoadingState />;
  if (!isAuthenticated || !user) return <Navigate to="/login" replace />;
  return <Navigate to={homeForRole(user.role)} replace />;
}

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<HomeRedirect />} />

      <Route element={<ProtectedRoute role="BUSINESS" />}>
        <Route element={<BusinessLayout />}>
          <Route path="/business" element={<BusinessDashboardPage />} />
          <Route path="/business/orders/new" element={<NewOrderPage />} />
          <Route path="/business/orders/:id" element={<OrderDetailPage />} />
          <Route path="/business/notifications" element={<BusinessNotificationsPage />} />
          <Route path="/business/profile" element={<BusinessProfilePage />} />
        </Route>
      </Route>

      <Route element={<ProtectedRoute role="RIDER" />}>
        <Route element={<RiderLayout />}>
          <Route path="/rider" element={<RiderDashboardPage />} />
          <Route path="/rider/deliveries/:id" element={<DeliveryDetailPage />} />
          <Route path="/rider/notifications" element={<RiderNotificationsPage />} />
          <Route path="/rider/profile" element={<RiderProfilePage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
