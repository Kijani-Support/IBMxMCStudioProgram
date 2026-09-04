import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useI18n } from '../i18n/I18nContext';

export default function Register() {
  const [form, setForm] = useState({ name: '', email: '', password: '', grade: '', school: '' });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const { register } = useAuth();
  const { t } = useI18n();
  const navigate = useNavigate();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await register({ ...form, role: 'STUDENT' });
      navigate('/dashboard', { replace: true });
    } catch (err) {
      setError(err.response?.data?.message || t('common.error'));
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* LEFT - FORM */}
      <div className="flex-1 flex items-center justify-center p-8 bg-white">
        <div className="w-full max-w-md animate-fade-in">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-ss-black">{t('app.name')}</h1>
            <p className="text-gray-500 mt-2">{t('app.tagline')}</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-50 text-red-600 p-4 rounded-xl text-sm border border-red-200">{error}</div>
            )}

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">{t('auth.name')}</label>
              <input type="text" name="name" value={form.name} onChange={handleChange}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-ss-blue focus:border-transparent transition"
                required />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">{t('auth.email')}</label>
              <input type="email" name="email" value={form.email} onChange={handleChange}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-ss-blue focus:border-transparent transition"
                required />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">{t('auth.password')}</label>
              <input type="password" name="password" value={form.password} onChange={handleChange}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-ss-blue focus:border-transparent transition"
                required minLength={6} />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">{t('auth.grade')}</label>
                <input type="text" name="grade" value={form.grade} onChange={handleChange}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-ss-blue focus:border-transparent transition"
                  placeholder="Grade 5" />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">{t('auth.school')}</label>
                <input type="text" name="school" value={form.school} onChange={handleChange}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-ss-blue focus:border-transparent transition" />
              </div>
            </div>

            <button type="submit" disabled={submitting}
              className="w-full btn-primary py-3 text-lg disabled:opacity-50">
              {submitting ? '...' : t('auth.register')}
            </button>
          </form>

          <p className="text-center mt-6 text-gray-500">
            {t('auth.hasAccount')}{' '}
            <Link to="/login" className="text-ss-blue font-semibold hover:underline">{t('auth.signIn')}</Link>
          </p>
        </div>
      </div>

      {/* RIGHT - HERO */}
      <div className="hidden lg:flex flex-1 gradient-primary items-center justify-center p-12 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-16 right-24 w-40 h-40 border-4 border-white rounded-full"></div>
          <div className="absolute bottom-24 left-20 w-36 h-36 border-4 border-white rounded-full"></div>
        </div>
        <div className="relative z-10 text-center text-white max-w-md">
          <div className="w-24 h-24 bg-white/20 rounded-3xl flex items-center justify-center mx-auto mb-8 backdrop-blur-sm">
            <svg className="w-14 h-14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
          </div>
          <h2 className="text-3xl font-bold mb-4">Start Learning Today</h2>
          <p className="text-white/80 text-lg leading-relaxed">
            Join thousands of students learning with offline-first education. Your journey starts here.
          </p>
          <div className="flex justify-center gap-4 mt-8">
            <div className="bg-white/10 rounded-xl px-4 py-3 backdrop-blur-sm">
              <div className="text-white/60 text-xs">Grade Levels</div>
              <div className="font-bold">1-12</div>
            </div>
            <div className="bg-white/10 rounded-xl px-4 py-3 backdrop-blur-sm">
              <div className="text-white/60 text-xs">Subjects</div>
              <div className="font-bold">Math, Science, English</div>
            </div>
            <div className="bg-white/10 rounded-xl px-4 py-3 backdrop-blur-sm">
              <div className="text-white/60 text-xs">Offline</div>
              <div className="font-bold">Full Support</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
