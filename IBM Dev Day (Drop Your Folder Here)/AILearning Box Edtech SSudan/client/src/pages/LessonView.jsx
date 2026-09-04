import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import db from '../db/dexie';
import { useOfflineProgress } from '../hooks/useOffline';
import { useI18n } from '../i18n/I18nContext';

export default function LessonView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { t } = useI18n();
  const [lesson, setLesson] = useState(null);
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(true);
  const [completing, setCompleting] = useState(false);
  const { saveProgress } = useOfflineProgress();

  useEffect(() => {
    const loadLesson = async () => {
      try {
        const res = await api.get(`/lessons/${id}`);
        setLesson(res.data);
        setQuiz(res.data.quiz);
      } catch {
        const localLesson = await db.lessons.where('serverId').equals(id).first();
        if (localLesson) {
          setLesson(localLesson);
          const localQuiz = await db.quizzes.where('lessonId').equals(localLesson.id).first();
          if (localQuiz) setQuiz(localQuiz);
        }
      }
      setLoading(false);
    };
    loadLesson();
  }, [id]);

  const handleComplete = async () => {
    setCompleting(true);
    const courseId = lesson.courseId?._id || lesson.courseId;
    await saveProgress(courseId, lesson._id || lesson.serverId, { completed: true, percentage: 100 });
    setCompleting(false);
    if (quiz) navigate(`/quiz/${quiz._id || quiz.serverId}`);
  };

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin w-8 h-8 border-4 border-ss-blue border-t-transparent rounded-full"></div>
    </div>
  );
  if (!lesson) return <div className="text-center py-12 text-gray-500">{t('common.notFound')}</div>;

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
      <Link to="/dashboard" className="inline-flex items-center gap-2 text-ss-blue hover:underline text-sm">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        {t('common.back')}
      </Link>

      {/* LESSON HEADER */}
      <div className="gradient-primary rounded-2xl p-8 text-white relative overflow-hidden">
        <div className="absolute top-0 right-0 w-48 h-48 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2"></div>
        <div className="relative z-10">
          <h1 className="text-3xl font-bold mb-2">{lesson.title}</h1>
          {lesson.description && <p className="text-white/70">{lesson.description}</p>}
          <div className="flex items-center gap-4 mt-4 text-white/60 text-sm">
            {lesson.duration && <span>{lesson.duration} min</span>}
            {quiz && <span className="bg-white/20 px-3 py-1 rounded-full">{t('assessment.quizAvailable')}</span>}
          </div>
        </div>
      </div>

      {/* MEDIA */}
      {lesson.video && (
        <div className="stat-card p-2">
          <video controls className="w-full rounded-xl" src={lesson.video} />
        </div>
      )}

      {lesson.audio && (
        <div className="stat-card">
          <audio controls className="w-full" src={lesson.audio} />
        </div>
      )}

      {/* CONTENT */}
      <div className="stat-card">
        <div className="lesson-content whitespace-pre-wrap text-gray-700 leading-relaxed">
          {lesson.content}
        </div>
      </div>

      {/* DOCUMENTS */}
      {lesson.documents && lesson.documents.length > 0 && (
        <div className="stat-card">
          <h3 className="font-bold text-gray-800 mb-3">Documents</h3>
          <div className="space-y-2">
            {lesson.documents.map((doc, idx) => (
              <a key={idx} href={doc.url} target="_blank" rel="noopener noreferrer"
                className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition">
                <svg className="w-5 h-5 text-ss-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
                <span className="text-sm text-gray-700">{doc.name || `Document ${idx + 1}`}</span>
              </a>
            ))}
          </div>
        </div>
      )}

      {/* ACTIONS */}
      <div className="flex gap-4">
        <button onClick={handleComplete} disabled={completing}
          className="btn-success flex-1 disabled:opacity-50">
          {completing ? t('student.saving') : t('student.markComplete')}
        </button>
        {quiz && (
          <Link to={`/quiz/${quiz._id || quiz.serverId}`}
            className="btn-primary flex-1 text-center">
            {t('student.takeQuiz')}
          </Link>
        )}
      </div>
    </div>
  );
}
