import { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../hooks/useAuth';
import { useI18n } from '../i18n/I18nContext';

export default function AdminDashboard() {
  const { user } = useAuth();
  const { t } = useI18n();
  const [courses, setCourses] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: '', description: '', grade: '', subject: '' });
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);

  useEffect(() => {
    api.get('/courses').then(res => setCourses(res.data)).finally(() => setLoading(false));
  }, []);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleCreate = async (e) => {
    e.preventDefault();
    if (editingId) {
      const res = await api.put(`/courses/${editingId}`, form);
      setCourses(courses.map(c => c.id === editingId ? res.data : c));
    } else {
      const res = await api.post('/courses', form);
      setCourses([res.data, ...courses]);
    }
    setForm({ title: '', description: '', grade: '', subject: '' });
    setShowForm(false);
    setEditingId(null);
  };

  const handleEdit = (course) => {
    setForm({ title: course.title, description: course.description, grade: course.grade, subject: course.subject });
    setEditingId(course.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this course?')) return;
    await api.delete(`/courses/${id}`);
    setCourses(courses.filter(c => c.id !== id));
  };

  const togglePublish = async (course) => {
    const res = await api.put(`/courses/${course.id}`, { published: !course.published });
    setCourses(courses.map(c => c.id === course.id ? res.data : c));
  };

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin w-8 h-8 border-4 border-ss-blue border-t-transparent rounded-full"></div>
    </div>
  );

  const publishedCount = courses.filter(c => c.published).length;

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fade-in">
      {/* HEADER */}
      <div className="gradient-primary rounded-2xl p-8 text-white relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2"></div>
        <div className="relative z-10 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold mb-2">{t('admin.title')}</h1>
            <p className="text-white/70">{user?.name}</p>
          </div>
          <button onClick={() => { setShowForm(!showForm); setEditingId(null); setForm({ title: '', description: '', grade: '', subject: '' }); }}
            className="bg-white text-ss-blue px-6 py-3 rounded-xl font-semibold hover:bg-white/90 transition">
            {showForm ? t('admin.cancel') : t('admin.newCourse')}
          </button>
        </div>
      </div>

      {/* STATS */}
      <div className="grid grid-cols-3 gap-4">
        <div className="stat-card text-center">
          <div className="text-3xl font-bold text-ss-blue">{courses.length}</div>
          <div className="text-sm text-gray-500">{t('admin.totalCourses')}</div>
        </div>
        <div className="stat-card text-center">
          <div className="text-3xl font-bold text-green-600">{publishedCount}</div>
          <div className="text-sm text-gray-500">{t('admin.published')}</div>
        </div>
        <div className="stat-card text-center">
          <div className="text-3xl font-bold text-amber-600">{courses.length - publishedCount}</div>
          <div className="text-sm text-gray-500">{t('admin.draft')}</div>
        </div>
      </div>

      {/* FORM */}
      {showForm && (
        <form onSubmit={handleCreate} className="stat-card space-y-4 animate-slide-up">
          <h2 className="text-lg font-bold text-gray-800">{editingId ? t('common.edit') : t('admin.newCourse')}</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">{t('admin.courseTitle')}</label>
              <input name="title" value={form.title} onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-ss-blue focus:border-transparent outline-none" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">{t('admin.courseGrade')}</label>
              <input name="grade" value={form.grade} onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-ss-blue focus:border-transparent outline-none"
                placeholder="e.g. Grade 5" required />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('admin.courseSubject')}</label>
            <input name="subject" value={form.subject} onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-ss-blue focus:border-transparent outline-none"
              placeholder="e.g. Mathematics" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('admin.courseDescription')}</label>
            <textarea name="description" value={form.description} onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-ss-blue focus:border-transparent outline-none resize-none"
              rows={3} required />
          </div>
          <button type="submit" className="btn-success">
            {editingId ? t('common.save') : t('admin.createCourse')}
          </button>
        </form>
      )}

      {/* COURSES */}
      <div>
        <h2 className="text-xl font-bold text-gray-800 mb-4">{t('admin.allCourses')}</h2>
        <div className="space-y-3">
          {courses.map((course, idx) => (
            <div key={course.id} className="stat-card hover:scale-[1.01] transition-transform"
              style={{ animationDelay: `${idx * 0.05}s` }}>
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium text-ss-blue bg-ss-blue/10 px-3 py-1 rounded-full">{course.grade}</span>
                    <span className="text-xs font-medium text-gray-500 bg-gray-100 px-3 py-1 rounded-full">{course.subject}</span>
                    <span className={`text-xs px-3 py-1 rounded-full font-medium ${course.published ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                      {course.published ? t('admin.published') : t('admin.draft')}
                    </span>
                  </div>
                  <h3 className="font-semibold text-gray-800">{course.title}</h3>
                  <p className="text-sm text-gray-500">{course.description?.slice(0, 80)}...</p>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <button onClick={() => togglePublish(course)}
                    className={`text-sm px-3 py-1.5 rounded-lg transition ${course.published ? 'bg-gray-100 text-gray-700 hover:bg-gray-200' : 'bg-green-500 text-white hover:bg-green-600'}`}>
                    {course.published ? t('admin.unpublish') : t('admin.publish')}
                  </button>
                  <button onClick={() => handleEdit(course)} className="text-sm px-3 py-1.5 rounded-lg bg-ss-blue/10 text-ss-blue hover:bg-ss-blue/20 transition">
                    {t('common.edit')}
                  </button>
                  <button onClick={() => handleDelete(course.id)} className="text-sm px-3 py-1.5 rounded-lg bg-red-100 text-red-600 hover:bg-red-200 transition">
                    {t('common.delete')}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
