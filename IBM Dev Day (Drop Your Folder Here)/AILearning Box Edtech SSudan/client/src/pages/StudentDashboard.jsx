import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import db from '../db/dexie';
import { useI18n } from '../i18n/I18nContext';

export default function StudentDashboard() {
  const { t } = useI18n();
  const [courseProgress, setCourseProgress] = useState([]);
  const [offlineCourses, setOfflineCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ coursesStarted: 0, lessonsCompleted: 0, avgScore: 0 });

  useEffect(() => {
    const loadData = async () => {
      try {
        const [cpRes, pRes] = await Promise.all([
          api.get('/progress/courses'),
          api.get('/progress').catch(() => ({ data: [] }))
        ]);
        setCourseProgress(cpRes.data);

        const totalLessonsCompleted = pRes.data.filter(p => p.completed).length;
        const scores = pRes.data.filter(p => p.quizScore != null).map(p => p.quizScore);
        const avgScore = scores.length > 0 ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0;

        setStats({
          coursesStarted: cpRes.data.filter(c => c.completedLessons > 0).length,
          lessonsCompleted: totalLessonsCompleted,
          avgScore
        });
      } catch {
        const localCourses = await db.courses.where('downloaded').equals(1).toArray();
        setOfflineCourses(localCourses);
      }
      setLoading(false);
    };
    loadData();
  }, []);

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin w-8 h-8 border-4 border-ss-blue border-t-transparent rounded-full"></div>
    </div>
  );

  const allCourses = courseProgress.length > 0 ? courseProgress : offlineCourses;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* WELCOME HEADER */}
      <div className="gradient-primary rounded-2xl p-8 text-white relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/5 rounded-full translate-y-1/2 -translate-x-1/2"></div>
        <div className="relative z-10">
          <h1 className="text-3xl font-bold mb-2">{t('student.title')}</h1>
          <p className="text-white/70">Continue where you left off or explore new courses</p>
        </div>
      </div>

      {/* STATS GRID */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>}
          value={stats.coursesStarted}
          label={t('progress.coursesStarted')}
          color="blue"
        />
        <StatCard
          icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
          value={stats.lessonsCompleted}
          label={t('progress.lessonsCompleted')}
          color="green"
        />
        <StatCard
          icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>}
          value={`${stats.avgScore}%`}
          label={t('progress.avgScore')}
          color="gold"
        />
        <Link to="/assessment" className="stat-card gradient-accent text-white flex items-center gap-4 hover:scale-105 transition-transform">
          <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <div>
            <div className="text-2xl font-bold">{t('assessment.title')}</div>
            <div className="text-white/70 text-sm">{t('assessment.subtitle')}</div>
          </div>
        </Link>
      </div>

      {/* COURSES */}
      <div>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-gray-800">Your Courses</h2>
          <span className="text-sm text-gray-500">{allCourses.length} courses</span>
        </div>

        {allCourses.length === 0 ? (
          <div className="stat-card text-center py-12">
            <svg className="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            <p className="text-gray-500">{t('student.noCourses')}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {allCourses.map((course, idx) => (
              <CourseCard key={course.courseId || course.id || course.serverId} course={course} index={idx} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ icon, value, label, color }) {
  const colors = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    gold: 'from-amber-500 to-amber-600'
  };

  return (
    <div className="stat-card">
      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colors[color]} flex items-center justify-center text-white mb-3`}>
        {icon}
      </div>
      <div className="text-2xl font-bold text-gray-800">{value}</div>
      <div className="text-sm text-gray-500">{label}</div>
    </div>
  );
}

function CourseCard({ course, index }) {
  const pct = course.overallPercentage || 0;
  const completed = course.completedLessons || 0;
  const total = course.totalLessons || 0;
  const subjectColors = {
    Mathematics: 'from-blue-500 to-indigo-600',
    Science: 'from-green-500 to-emerald-600',
    English: 'from-purple-500 to-pink-600'
  };
  const gradient = subjectColors[course.subject] || 'from-gray-500 to-gray-600';

  return (
    <Link to={`/course/${course.courseId || course.id || course.serverId}`}
      className="course-card animate-slide-up"
      style={{ animationDelay: `${index * 0.1}s` }}>
      {/* Header */}
      <div className={`h-32 bg-gradient-to-br ${gradient} p-6 relative overflow-hidden`}>
        <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2"></div>
        <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/10 rounded-full translate-y-1/2 -translate-x-1/2"></div>
        <div className="relative z-10">
          <span className="text-white/70 text-xs font-medium">{course.grade}</span>
          <h3 className="text-white font-bold text-lg mt-1">{course.title}</h3>
        </div>
      </div>

      {/* Body */}
      <div className="p-5">
        <div className="flex justify-between items-center mb-3">
          <span className="text-gray-500 text-sm">{completed}/{total} lessons</span>
          <span className={`text-lg font-bold ${pct >= 70 ? 'text-green-600' : pct >= 40 ? 'text-amber-600' : 'text-ss-blue'}`}>
            {pct}%
          </span>
        </div>
        <div className="w-full bg-gray-100 rounded-full h-2">
          <div className={`h-2 rounded-full transition-all duration-500 ${pct >= 70 ? 'bg-green-500' : pct >= 40 ? 'bg-amber-500' : 'bg-ss-blue'}`}
            style={{ width: `${pct}%` }} />
        </div>
        {course.avgQuizScore != null && (
          <div className="mt-3 text-xs text-gray-400">
            Avg Quiz Score: <span className="font-semibold text-gray-600">{course.avgQuizScore}%</span>
          </div>
        )}
      </div>
    </Link>
  );
}
