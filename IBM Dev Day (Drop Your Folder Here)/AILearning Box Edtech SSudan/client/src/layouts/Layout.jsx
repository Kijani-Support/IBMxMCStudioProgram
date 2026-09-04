import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useI18n } from '../i18n/I18nContext';
import LanguageSwitcher from '../components/LanguageSwitcher';

export default function Layout() {
  const { user, logout } = useAuth();
  const { t } = useI18n();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <div className="min-h-screen">
      {/* NAVBAR */}
      <nav className="gradient-primary sticky top-0 z-40 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/dashboard" className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <div>
                <span className="text-white font-bold text-lg">{t('app.name')}</span>
                <span className="text-white/60 text-xs block -mt-1">{t('app.tagline')}</span>
              </div>
            </Link>

            {/* Nav Links */}
            <div className="hidden md:flex items-center gap-1">
              <NavLink to="/dashboard" active={isActive('/dashboard')}>
                {t('nav.dashboard')}
              </NavLink>
              <NavLink to="/assessment" active={isActive('/assessment')}>
                {t('nav.assessment')}
              </NavLink>
              {(user?.role === 'ADMIN' || user?.role === 'TEACHER') && (
                <NavLink to="/teacher" active={isActive('/teacher')}>
                  {t('nav.analytics')}
                </NavLink>
              )}
              {user?.role === 'ADMIN' && (
                <NavLink to="/admin" active={isActive('/admin')}>
                  {t('nav.admin')}
                </NavLink>
              )}
            </div>

            {/* Right Side */}
            <div className="flex items-center gap-3">
              <LanguageSwitcher />
              <div className="hidden sm:flex items-center gap-2 bg-white/10 rounded-full px-3 py-1.5">
                <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center text-white text-sm font-bold">
                  {user?.name?.charAt(0)}
                </div>
                <span className="text-white text-sm font-medium">{user?.name}</span>
              </div>
              <button onClick={handleLogout}
                className="text-white/70 hover:text-white transition p-2 rounded-lg hover:bg-white/10">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Nav */}
        <div className="md:hidden border-t border-white/10 px-4 py-2 flex gap-1 overflow-x-auto">
          <MobileNavLink to="/dashboard" active={isActive('/dashboard')}>{t('nav.dashboard')}</MobileNavLink>
          <MobileNavLink to="/assessment" active={isActive('/assessment')}>{t('nav.assessment')}</MobileNavLink>
          {(user?.role === 'ADMIN' || user?.role === 'TEACHER') && (
            <MobileNavLink to="/teacher" active={isActive('/teacher')}>{t('nav.analytics')}</MobileNavLink>
          )}
          {user?.role === 'ADMIN' && (
            <MobileNavLink to="/admin" active={isActive('/admin')}>{t('nav.admin')}</MobileNavLink>
          )}
        </div>
      </nav>

      {/* MAIN CONTENT */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        <Outlet />
      </main>

      {/* FOOTER */}
      <footer className="gradient-primary mt-auto py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 text-center">
          <p className="text-white/60 text-sm">
            {t('app.name')} &copy; {new Date().getFullYear()} &mdash; {t('app.tagline')}
          </p>
        </div>
      </footer>
    </div>
  );
}

function NavLink({ to, active, children }) {
  return (
    <Link to={to}
      className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
        active
          ? 'bg-white/20 text-white'
          : 'text-white/70 hover:text-white hover:bg-white/10'
      }`}>
      {children}
    </Link>
  );
}

function MobileNavLink({ to, active, children }) {
  return (
    <Link to={to}
      className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all ${
        active
          ? 'bg-white/20 text-white'
          : 'text-white/60 hover:text-white'
      }`}>
      {children}
    </Link>
  );
}
