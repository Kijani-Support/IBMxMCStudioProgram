import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../hooks/useAuth';
import { useI18n } from '../i18n/I18nContext';

export default function TeacherDashboard() {
  const { user } = useAuth();
  const { t } = useI18n();
  const [students, setStudents] = useState([]);
  const [courses, setCourses] = useState([]);
  const [progress, setProgress] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get('/courses?published=true'),
      api.get('/progress').catch(() => ({ data: [] }))
    ]).then(([coursesRes, progressRes]) => {
      setCourses(coursesRes.data);
      setProgress(progressRes.data);
      const studentMap = new Map();
      progressRes.data.forEach(p => {
        if (p.studentId && !studentMap.has(p.studentId._id || p.studentId.id)) {
          studentMap.set(p.studentId._id || p.studentId.id, p.studentId);
        }
      });
      setStudents(Array.from(studentMap.values()));
    }).finally(() => setLoading(false));
  }, []);

  const getStudentProgress = (studentId) => progress.filter(p => (p.studentId?._id || p.studentId) === studentId);

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin w-8 h-8 border-4 border-ss-blue border-t-transparent rounded-full"></div>
    </div>
  );

  const avgProgress = progress.length > 0 ? Math.round(progress.reduce((a, p) => a + (p.percentage || 0), 0) / progress.length) : 0;

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fade-in">
      {/* HEADER */}
      <div className="gradient-primary rounded-2xl p-8 text-white relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2"></div>
        <div className="relative z-10 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold mb-2">{t('teacher.title')}</h1>
            <p className="text-white/70">{user?.name}</p>
          </div>
          <Link to="/reports" className="bg-white text-ss-blue px-6 py-3 rounded-xl font-semibold hover:bg-white/90 transition flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            View Full Reports
          </Link>
        </div>
      </div>

      {/* STATS */}
      <div className="grid grid-cols-3 gap-4">
        <div className="stat-card text-center">
          <div className="text-3xl font-bold text-ss-blue">{students.length}</div>
          <div className="text-sm text-gray-500">{t('teacher.students')}</div>
        </div>
        <div className="stat-card text-center">
          <div className="text-3xl font-bold text-green-600">{courses.length}</div>
          <div className="text-sm text-gray-500">{t('teacher.publishedCourses')}</div>
        </div>
        <div className="stat-card text-center">
          <div className="text-3xl font-bold text-amber-600">{avgProgress}%</div>
          <div className="text-sm text-gray-500">{t('teacher.avgProgress')}</div>
        </div>
      </div>

      {/* STUDENT PROGRESS */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-800">{t('teacher.studentProgress')}</h2>
          <Link to="/reports" className="text-ss-blue text-sm font-medium hover:underline flex items-center gap-1">
            View detailed reports
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>
        <div className="space-y-4">
          {students.length === 0 ? (
            <div className="stat-card text-center py-12">
              <svg className="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <p className="text-gray-500">{t('teacher.noData')}</p>
            </div>
          ) : (
            students.map((student, idx) => {
              const sp = getStudentProgress(student._id || student.id);
              const avg = sp.length > 0 ? Math.round(sp.reduce((a, p) => a + (p.percentage || 0), 0) / sp.length) : 0;
              return (
                <Link key={student._id || student.id} to={`/reports/student/${student._id || student.id}`}
                  className="stat-card flex items-center justify-between hover:scale-[1.01] transition-transform"
                  style={{ animationDelay: `${idx * 0.1}s` }}>
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-ss-blue to-ss-green flex items-center justify-center text-white font-bold text-lg">
                      {student.name?.charAt(0)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-800">{student.name}</h3>
                      <p className="text-sm text-gray-500">{student.grade || ''} &bull; {student.school || ''}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <div className={`text-2xl font-bold ${avg >= 70 ? 'text-green-600' : avg >= 40 ? 'text-amber-600' : 'text-ss-blue'}`}>{avg}%</div>
                      <div className="text-xs text-gray-400">{t('teacher.overall')}</div>
                    </div>
                    <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </Link>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
