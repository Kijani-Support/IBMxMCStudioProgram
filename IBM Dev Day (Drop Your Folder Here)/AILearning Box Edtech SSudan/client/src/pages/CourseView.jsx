import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import db from '../db/dexie';
import { useDownloadedCourse } from '../hooks/useOffline';
import { useI18n } from '../i18n/I18nContext';

export default function CourseView() {
  const { id } = useParams();
  const { t } = useI18n();
  const [course, setCourse] = useState(null);
  const [lessons, setLessons] = useState([]);
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const { downloaded, downloading, progress: dlProgress, download, remove } = useDownloadedCourse(id);

  useEffect(() => {
    const loadCourse = async () => {
      try {
        const [courseRes, progressRes] = await Promise.all([
          api.get(`/courses/${id}`),
          api.get(`/progress/course/${id}`).catch(() => ({ data: null }))
        ]);
        setCourse(courseRes.data);
        setLessons(courseRes.data.lessons || []);
        setProgress(progressRes.data);
      } catch {
        const localCourse = await db.courses.where('serverId').equals(id).first();
        if (localCourse) {
          setCourse(localCourse);
          const localLessons = await db.lessons.where('courseId').equals(localCourse.id).sortBy('order');
          setLessons(localLessons);
        }
      }
      setLoading(false);
    };
    loadCourse();
  }, [id]);

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin w-8 h-8 border-4 border-ss-blue border-t-transparent rounded-full"></div>
    </div>
  );
  if (!course) return <div className="text-center py-12 text-gray-500">{t('common.notFound')}</div>;

  const subjectColors = {
    Mathematics: 'from-blue-500 to-indigo-600',
    Science: 'from-green-500 to-emerald-600',
    English: 'from-purple-500 to-pink-600'
  };
  const gradient = subjectColors[course.subject] || 'from-gray-500 to-gray-600';

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      <Link to="/dashboard" className="inline-flex items-center gap-2 text-ss-blue hover:underline text-sm">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        {t('common.back')}
      </Link>

      {/* COURSE HEADER */}
      <div className={`rounded-2xl bg-gradient-to-br ${gradient} p-8 text-white relative overflow-hidden`}>
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2"></div>
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-3">
            <span className="bg-white/20 text-white text-xs font-medium px-3 py-1 rounded-full">{course.grade}</span>
            <span className="bg-white/20 text-white text-xs font-medium px-3 py-1 rounded-full">{course.subject}</span>
          </div>
          <h1 className="text-3xl font-bold mb-2">{course.title}</h1>
          <p className="text-white/80 max-w-2xl">{course.description}</p>
          <div className="flex items-center gap-4 mt-4 text-white/70 text-sm">
            <span>{lessons.length} {t('student.lessons')}</span>
            {downloaded && <span className="text-green-300">✓ {t('student.availableOffline')}</span>}
          </div>
        </div>
        <div className="relative z-10 mt-6 flex gap-3">
          {downloaded ? (
            <button onClick={remove} className="bg-white/20 text-white px-4 py-2 rounded-xl hover:bg-white/30 transition text-sm">
              {t('student.remove')}
            </button>
          ) : (
            <button onClick={download} disabled={downloading}
              className="bg-white text-gray-800 px-6 py-2 rounded-xl font-semibold hover:bg-white/90 transition disabled:opacity-50">
              {downloading ? `${t('student.downloading')} ${dlProgress}%` : t('student.downloadForOffline')}
            </button>
          )}
        </div>
        {downloading && (
          <div className="relative z-10 mt-4">
            <div className="w-full bg-white/20 rounded-full h-2">
              <div className="bg-white h-2 rounded-full transition-all" style={{ width: `${dlProgress}%` }} />
            </div>
          </div>
        )}
      </div>

      {/* PROGRESS */}
      {progress && (
        <div className="stat-card">
          <div className="flex justify-between items-center mb-4">
            <h2 className="font-bold text-gray-800">{t('progress.overall')}</h2>
            <span className={`text-3xl font-bold ${progress.overallPercentage >= 70 ? 'text-green-600' : progress.overallPercentage >= 40 ? 'text-amber-600' : 'text-ss-blue'}`}>
              {progress.overallPercentage}%
            </span>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-3 mb-4">
            <div className={`h-3 rounded-full transition-all duration-500 ${progress.overallPercentage >= 70 ? 'bg-green-500' : progress.overallPercentage >= 40 ? 'bg-amber-500' : 'bg-ss-blue'}`}
              style={{ width: `${progress.overallPercentage}%` }} />
          </div>
          <div className="flex gap-6 text-sm text-gray-500">
            <span>{progress.completedLessons}/{progress.totalLessons} {t('student.lessons')}</span>
            {progress.avgQuizScore != null && <span>{t('progress.avgScore')}: {progress.avgQuizScore}%</span>}
          </div>
        </div>
      )}

      {/* LESSONS */}
      <div>
        <h2 className="text-xl font-bold text-gray-800 mb-4">{t('student.lessons')} ({lessons.length})</h2>
        <div className="space-y-3">
          {lessons.map((lesson, idx) => {
            const lessonProgress = progress?.lessons?.find(l => l.lessonId === lesson.id);
            const isCompleted = lessonProgress?.completed;

            return (
              <Link key={lesson._id || lesson.id} to={`/lesson/${lesson._id || lesson.serverId || lesson.id}`}
                className={`stat-card flex items-center gap-4 hover:scale-[1.01] transition-transform ${isCompleted ? 'border-l-4 border-green-500' : ''}`}>
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold ${
                  isCompleted ? 'bg-green-100 text-green-600' : 'bg-ss-blue/10 text-ss-blue'
                }`}>
                  {isCompleted ? (
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : idx + 1}
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-800">{lesson.title}</h3>
                  <p className="text-sm text-gray-500">{lesson.duration ? `${lesson.duration} min` : t('student.selfPaced')}</p>
                </div>
                {lessonProgress?.quizScore != null && (
                  <div className={`text-sm font-bold px-3 py-1 rounded-lg ${lessonProgress.quizScore >= 60 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                    {lessonProgress.quizScore}%
                  </div>
                )}
                {!isCompleted && (
                  <span className="text-ss-blue text-sm font-medium">{t('student.startLesson')}</span>
                )}
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
