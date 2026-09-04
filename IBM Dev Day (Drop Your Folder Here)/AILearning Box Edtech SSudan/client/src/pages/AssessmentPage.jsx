import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useI18n } from '../i18n/I18nContext';

export default function AssessmentPage() {
  const { t } = useI18n();
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [phase, setPhase] = useState('select');

  useEffect(() => {
    api.get('/assessment/courses').then(res => {
      setCourses(res.data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const startAssessment = async (courseTitle) => {
    setSelectedCourse(courseTitle);
    setPhase('taking');
    setAnswers({});
    const res = await api.get(`/assessment/diagnostic/${courseTitle}`);
    setQuestions(res.data.questions);
  };

  const handleAnswer = (qId, optIdx) => setAnswers({ ...answers, [qId]: optIdx });

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const res = await api.post(`/assessment/diagnostic/${selectedCourse}/submit`, { answers });
      setResult(res.data);
      setPhase('result');
    } catch (err) {
      console.error(err);
    }
    setSubmitting(false);
  };

  const needsReview = result?.learningPath?.filter(p => p.status === 'needs_review') || [];
  const practice = result?.learningPath?.filter(p => p.status === 'practice_recommended') || [];
  const mastered = result?.learningPath?.filter(p => p.status === 'mastered') || [];

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin w-8 h-8 border-4 border-ss-blue border-t-transparent rounded-full"></div>
    </div>
  );

  // SELECT COURSE
  if (phase === 'select') {
    return (
      <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
        <div className="gradient-primary rounded-2xl p-8 text-white relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2"></div>
          <div className="relative z-10">
            <h1 className="text-3xl font-bold mb-2">{t('assessment.title')}</h1>
            <p className="text-white/70">{t('assessment.subtitle')}</p>
          </div>
        </div>

        <div className="grid gap-4">
          {courses.map((course, idx) => (
            <div key={course.title} className="stat-card flex justify-between items-center hover:scale-[1.01] transition-transform"
              style={{ animationDelay: `${idx * 0.1}s` }}>
              <div>
                <h3 className="font-semibold text-gray-800">{course.title}</h3>
                <p className="text-sm text-gray-500 mt-1">
                  {course.topics.length} {t('assessment.topics')} &bull; {course.questionCount} {t('assessment.question').toLowerCase()}s
                </p>
                <div className="flex flex-wrap gap-2 mt-2">
                  {course.topics.map(topic => (
                    <span key={topic.id} className="text-xs bg-ss-blue/10 text-ss-blue px-2 py-1 rounded-full">{topic.name}</span>
                  ))}
                </div>
              </div>
              <button onClick={() => startAssessment(course.title)}
                className="btn-primary whitespace-nowrap">
                {t('assessment.startAssessment')}
              </button>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // TAKING ASSESSMENT
  if (phase === 'taking') {
    const answered = Object.keys(answers).length;
    return (
      <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
        <div className="gradient-primary rounded-2xl p-8 text-white">
          <div className="flex justify-between items-center mb-4">
            <h1 className="text-2xl font-bold">{selectedCourse}</h1>
            <button onClick={() => { setPhase('select'); setSelectedCourse(null); }}
              className="text-white/60 hover:text-white text-sm">{t('common.cancel')}</button>
          </div>
          <p className="text-white/70 mb-4">{answered} / {questions.length} {t('assessment.question').toLowerCase()}s answered</p>
          <div className="w-full bg-white/20 rounded-full h-2">
            <div className="bg-white h-2 rounded-full transition-all" style={{ width: `${(answered / questions.length) * 100}%` }} />
          </div>
        </div>

        <div className="space-y-4">
          {questions.map((q, qIdx) => (
            <div key={q.id} className="stat-card animate-slide-up" style={{ animationDelay: `${qIdx * 0.05}s` }}>
              <p className="font-semibold text-gray-800 mb-4">
                <span className="text-ss-blue">Q{q.id + 1}.</span> {q.text}
              </p>
              <div className="space-y-2">
                {q.options.map((opt, oIdx) => (
                  <button key={oIdx}
                    onClick={() => handleAnswer(q.id, oIdx)}
                    className={`quiz-option text-left ${answers[q.id] === oIdx ? 'selected' : ''}`}>
                    <span className="font-medium">{String.fromCharCode(65 + oIdx)}.</span> {opt}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

        <button onClick={handleSubmit}
          disabled={submitting || answered < questions.length}
          className="w-full btn-primary py-4 text-lg disabled:opacity-50">
          {submitting ? t('assessment.submitting') : t('assessment.submitAssessment')}
        </button>
      </div>
    );
  }

  // RESULT + LEARNING PATH
  if (phase === 'result' && result) {
    return (
      <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
        {/* SCORE */}
        <div className="stat-card text-center py-12">
          <div className={`text-6xl font-bold mb-2 ${result.score >= 70 ? 'text-green-600' : result.score >= 50 ? 'text-amber-600' : 'text-red-600'}`}>
            {result.score}%
          </div>
          <p className="text-gray-600 text-lg">{result.correct} / {result.total} correct</p>
          <p className="text-gray-400 text-sm mt-1">{result.courseTitle}</p>
        </div>

        {/* TOPIC BREAKDOWN */}
        <div className="stat-card">
          <h2 className="text-lg font-bold text-gray-800 mb-4">{t('assessment.topicResults')}</h2>
          <div className="space-y-3">
            {Object.values(result.topicResults || {}).map(topic => (
              <div key={topic.name} className="flex items-center gap-3">
                <div className="flex-1">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium text-gray-700">{topic.name}</span>
                    <span className={`font-bold ${topic.percentage >= 70 ? 'text-green-600' : topic.percentage >= 50 ? 'text-amber-600' : 'text-red-600'}`}>
                      {topic.percentage}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2 mt-1">
                    <div className={`h-2 rounded-full ${topic.percentage >= 70 ? 'bg-green-500' : topic.percentage >= 50 ? 'bg-amber-500' : 'bg-red-500'}`}
                      style={{ width: `${topic.percentage}%` }} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* LEARNING PATH */}
        <h2 className="text-xl font-bold text-gray-800">{t('assessment.learningPath')}</h2>

        {/* NEEDS REVIEW */}
        {needsReview.length > 0 && (
          <div className="stat-card border-l-4 border-red-500">
            <h3 className="text-sm font-semibold text-red-600 mb-3 flex items-center gap-2">
              <span className="w-3 h-3 bg-red-500 rounded-full"></span>
              {t('assessment.needsReview')} ({needsReview.length})
            </h3>
            <div className="space-y-3">
              {needsReview.map(item => (
                <div key={item.topicId} className="bg-red-50 rounded-xl p-4">
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-medium text-gray-800">{item.name}</span>
                    <span className="text-sm text-red-600 font-bold">{item.score}%</span>
                  </div>
                  {item.lesson && (
                    <div className="mt-3 pl-4 border-l-2 border-red-300">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-700">{t('assessment.lessonContent')}: {item.lesson.title}</p>
                          {item.lesson.description && <p className="text-xs text-gray-500 mt-0.5">{item.lesson.description}</p>}
                        </div>
                        <Link to={`/lesson/${item.lesson.id}`} className="btn-danger text-xs">
                          {t('assessment.startLesson')}
                        </Link>
                      </div>
                      {item.quiz && (
                        <Link to={`/quiz/${item.quiz.id}`} className="inline-block mt-2 text-xs text-red-700 hover:text-red-800 underline">
                          {t('assessment.quizAvailable')}: {item.quiz.title}
                        </Link>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* PRACTICE RECOMMENDED */}
        {practice.length > 0 && (
          <div className="stat-card border-l-4 border-amber-500">
            <h3 className="text-sm font-semibold text-amber-600 mb-3 flex items-center gap-2">
              <span className="w-3 h-3 bg-amber-500 rounded-full"></span>
              {t('assessment.practiceRecommended')} ({practice.length})
            </h3>
            <div className="space-y-3">
              {practice.map(item => (
                <div key={item.topicId} className="bg-amber-50 rounded-xl p-4">
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-medium text-gray-800">{item.name}</span>
                    <span className="text-sm text-amber-600 font-bold">{item.score}%</span>
                  </div>
                  {item.lesson && (
                    <div className="mt-3 pl-4 border-l-2 border-amber-300">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-gray-700">{t('assessment.lessonContent')}: {item.lesson.title}</p>
                        <Link to={`/lesson/${item.lesson.id}`} className="btn-accent text-xs">
                          {t('assessment.viewLesson')}
                        </Link>
                      </div>
                      {item.quiz && (
                        <Link to={`/quiz/${item.quiz.id}`} className="inline-block mt-2 text-xs text-amber-700 hover:text-amber-800 underline">
                          {t('assessment.quizAvailable')}: {item.quiz.title}
                        </Link>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* MASTERED */}
        {mastered.length > 0 && (
          <div className="stat-card border-l-4 border-green-500">
            <h3 className="text-sm font-semibold text-green-600 mb-3 flex items-center gap-2">
              <span className="w-3 h-3 bg-green-500 rounded-full"></span>
              {t('assessment.mastered')} ({mastered.length})
            </h3>
            <div className="space-y-2">
              {mastered.map(item => (
                <div key={item.topicId} className="bg-green-50 rounded-xl p-4 flex justify-between items-center">
                  <div className="flex items-center gap-3">
                    <span className="text-green-500 font-bold">&#10003;</span>
                    <span className="font-medium text-gray-800">{item.name}</span>
                  </div>
                  <span className="text-sm text-green-600 font-bold">{item.score}%</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ALL RESOURCES */}
        <div className="stat-card bg-ss-blue/5">
          <h3 className="font-bold text-ss-blue mb-2">{t('assessment.resources')}</h3>
          <p className="text-sm text-gray-500 mb-4">{t('assessment.improveSkills')}</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {result.learningPath?.filter(item => item.lesson).map(item => (
              <Link key={item.topicId} to={`/lesson/${item.lesson.id}`}
                className={`flex items-center gap-3 p-3 rounded-xl transition hover:scale-[1.02] ${
                  item.status === 'needs_review' ? 'bg-red-100 hover:bg-red-200' :
                  item.status === 'practice_recommended' ? 'bg-amber-100 hover:bg-amber-200' :
                  'bg-green-100 hover:bg-green-200'
                }`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold ${
                  item.status === 'needs_review' ? 'bg-red-500' :
                  item.status === 'practice_recommended' ? 'bg-amber-500' : 'bg-green-500'
                }`}>
                  {item.lessonOrder}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800 truncate">{item.lesson.title}</p>
                  <p className="text-xs text-gray-500">{item.name}</p>
                </div>
                <span className={`text-xs font-bold ${
                  item.status === 'needs_review' ? 'text-red-600' :
                  item.status === 'practice_recommended' ? 'text-amber-600' : 'text-green-600'
                }`}>{item.score}%</span>
              </Link>
            ))}
          </div>
        </div>

        {/* ACTIONS */}
        <div className="flex gap-3">
          <button onClick={() => { setPhase('select'); setResult(null); setSelectedCourse(null); }}
            className="bg-gray-200 text-gray-700 px-6 py-3 rounded-xl hover:bg-gray-300 transition font-medium">
            {t('assessment.takeAgain')}
          </button>
          <Link to="/dashboard" className="btn-primary px-6 py-3 text-center">
            {t('quiz.backToDashboard')}
          </Link>
        </div>
      </div>
    );
  }

  return null;
}
