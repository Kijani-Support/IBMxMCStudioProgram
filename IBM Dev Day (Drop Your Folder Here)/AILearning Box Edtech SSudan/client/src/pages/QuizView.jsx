import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import db from '../db/dexie';
import { useOfflineProgress } from '../hooks/useOffline';
import { useI18n } from '../i18n/I18nContext';

export default function QuizView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { t } = useI18n();
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const { submitQuizOffline } = useOfflineProgress();

  useEffect(() => {
    const loadQuiz = async () => {
      try {
        const res = await api.get(`/quizzes/lesson/${id}`);
        setQuiz(res.data);
      } catch {
        const localQuiz = await db.quizzes.where('serverId').equals(id).first();
        if (localQuiz) setQuiz(localQuiz);
      }
      setLoading(false);
    };
    loadQuiz();
  }, [id]);

  const handleAnswer = (qIdx, oIdx) => setAnswers({ ...answers, [qIdx]: oIdx });

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const res = await api.post(`/quizzes/${quiz._id}/submit`, { answers });
      setResult(res.data);
    } catch {
      const r = await submitQuizOffline(quiz, answers, quiz.courseId, quiz.lessonId);
      setResult(r);
    }
    setSubmitting(false);
  };

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin w-8 h-8 border-4 border-ss-blue border-t-transparent rounded-full"></div>
    </div>
  );
  if (!quiz) return <div className="text-center py-12 text-gray-500">{t('common.notFound')}</div>;

  if (result) {
    const passed = result.passed;
    return (
      <div className="max-w-lg mx-auto animate-fade-in">
        <div className="stat-card text-center py-12">
          <div className={`w-24 h-24 rounded-full mx-auto mb-6 flex items-center justify-center ${passed ? 'bg-green-100' : 'bg-red-100'}`}>
            {passed ? (
              <svg className="w-12 h-12 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg className="w-12 h-12 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            )}
          </div>
          <div className={`text-5xl font-bold mb-2 ${passed ? 'text-green-600' : 'text-red-600'}`}>{result.score}%</div>
          <p className={`text-lg font-medium mb-2 ${passed ? 'text-green-600' : 'text-red-600'}`}>
            {passed ? t('quiz.passed') : t('quiz.failed')}
          </p>
          <p className="text-gray-500 mb-8">{result.correct} {t('quiz.correct')} {result.total} ({t('quiz.passing')}: {result.passingScore}%)</p>
          <button onClick={() => navigate('/dashboard')} className="btn-primary">
            {t('quiz.backToDashboard')}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
      <div className="gradient-primary rounded-2xl p-8 text-white">
        <h1 className="text-2xl font-bold mb-2">{quiz.title}</h1>
        <p className="text-white/70">{Object.keys(answers).length} / {quiz.questions.length} answered</p>
        <div className="w-full bg-white/20 rounded-full h-2 mt-4">
          <div className="bg-white h-2 rounded-full transition-all"
            style={{ width: `${(Object.keys(answers).length / quiz.questions.length) * 100}%` }} />
        </div>
      </div>

      <div className="space-y-4">
        {quiz.questions.map((question, qIdx) => (
          <div key={qIdx} className="stat-card animate-slide-up" style={{ animationDelay: `${qIdx * 0.05}s` }}>
            <p className="font-semibold text-gray-800 mb-4">
              <span className="text-ss-blue">Q{qIdx + 1}.</span> {question.text}
            </p>
            <div className="grid grid-cols-1 gap-2">
              {question.options.map((option, oIdx) => (
                <button key={oIdx}
                  onClick={() => handleAnswer(qIdx, oIdx)}
                  className={`quiz-option text-left ${answers[qIdx] === oIdx ? 'selected' : ''}`}>
                  <span className="font-medium">{String.fromCharCode(65 + oIdx)}.</span> {option.text}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      <button onClick={handleSubmit}
        disabled={submitting || Object.keys(answers).length < quiz.questions.length}
        className="w-full btn-primary py-4 text-lg disabled:opacity-50">
        {submitting ? t('quiz.submitting') : t('quiz.submit')}
      </button>
    </div>
  );
}
