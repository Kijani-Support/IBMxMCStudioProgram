import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './hooks/useAuth';
import { I18nProvider } from './i18n/I18nContext';
import { useOfflineSync } from './hooks/useOffline';
import Layout from './layouts/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import StudentDashboard from './pages/StudentDashboard';
import AdminDashboard from './pages/AdminDashboard';
import TeacherDashboard from './pages/TeacherDashboard';
import CourseView from './pages/CourseView';
import LessonView from './pages/LessonView';
import QuizView from './pages/QuizView';
import AssessmentPage from './pages/AssessmentPage';
import ReportsList from './pages/ReportsList';
import StudentReport from './pages/StudentReport';
import OfflineIndicator from './components/OfflineIndicator';

function PrivateRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex justify-center items-center h-screen"><div className="text-gray-500">Loading...</div></div>;
  return user ? children : <Navigate to="/login" />;
}

function AdminRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return null;
  return user?.role === 'ADMIN' || user?.role === 'TEACHER' ? children : <Navigate to="/dashboard" />;
}

function AppRoutes() {
  const { user } = useAuth();
  const location = useLocation();
  const { isOnline, isSyncing, pendingCount } = useOfflineSync();

  const isPublicPage = location.pathname === '/login' || location.pathname === '/register';

  return (
    <>
      {!isPublicPage && <OfflineIndicator isOnline={isOnline} isSyncing={isSyncing} pendingCount={pendingCount} />}
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<PrivateRoute><Layout /></PrivateRoute>}>
          <Route index element={<Navigate to="/dashboard" />} />
          <Route path="dashboard" element={
            user?.role === 'ADMIN' ? <AdminDashboard /> :
            user?.role === 'TEACHER' ? <TeacherDashboard /> :
            <StudentDashboard />
          } />
          <Route path="admin" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
          <Route path="teacher" element={<AdminRoute><TeacherDashboard /></AdminRoute>} />
          <Route path="course/:id" element={<CourseView />} />
          <Route path="lesson/:id" element={<LessonView />} />
          <Route path="quiz/:id" element={<QuizView />} />
          <Route path="assessment" element={<AssessmentPage />} />
          <Route path="reports" element={<AdminRoute><ReportsList /></AdminRoute>} />
          <Route path="reports/student/:id" element={<AdminRoute><StudentReport /></AdminRoute>} />
        </Route>
      </Routes>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <I18nProvider>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </I18nProvider>
    </BrowserRouter>
  );
}
