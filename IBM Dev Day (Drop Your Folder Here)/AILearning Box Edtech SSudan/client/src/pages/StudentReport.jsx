import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import { useI18n } from '../i18n/I18nContext';

export default function StudentReport() {
  const { id } = useParams();
  const { t } = useI18n();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get(`/reports/student/${id}`).then(res => {
      setReport(res.data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [id]);

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin w-8 h-8 border-4 border-ss-blue border-t-transparent rounded-full"></div>
    </div>
  );

  if (!report) return <div className="text-center py-12 text-gray-500">{t('common.notFound')}</div>;

  const { student, summary, courses, overallRecommendations } = report;

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fade-in">
      <Link to="/dashboard" className="inline-flex items-center gap-2 text-ss-blue hover:underline text-sm">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        {t('common.back')}
      </Link>

      {/* STUDENT HEADER */}
      <div className="gradient-primary rounded-2xl p-8 text-white relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2"></div>
        <div className="relative z-10 flex items-center gap-6">
          <div className="w-20 h-20 rounded-2xl bg-white/20 flex items-center justify-center text-3xl font-bold">
            {student.name?.charAt(0)}
          </div>
          <div>
            <h1 className="text-3xl font-bold">{student.name}</h1>
            <p className="text-white/70">{student.email}</p>
            <p className="text-white/50 text-sm mt-1">{student.grade || 'N/A'} &bull; {student.school || 'N/A'}</p>
          </div>
        </div>
      </div>

      {/* SUMMARY STATS */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="stat-card text-center">
          <div className="text-3xl font-bold text-ss-blue">{summary.totalCourses}</div>
          <div className="text-sm text-gray-500">Courses</div>
        </div>
        <div className="stat-card text-center">
          <div className="text-3xl font-bold text-green-600">{summary.completedLessons}/{summary.totalLessons}</div>
          <div className="text-sm text-gray-500">Lessons Done</div>
        </div>
        <div className="stat-card text-center">
          <div className={`text-3xl font-bold ${summary.overallPercentage >= 70 ? 'text-green-600' : summary.overallPercentage >= 40 ? 'text-amber-600' : 'text-red-600'}`}>
            {summary.overallPercentage}%
          </div>
          <div className="text-sm text-gray-500">Overall Progress</div>
        </div>
        <div className="stat-card text-center">
          <div className={`text-3xl font-bold ${summary.overallAvgQuizScore != null && summary.overallAvgQuizScore >= 70 ? 'text-green-600' : summary.overallAvgQuizScore != null && summary.overallAvgQuizScore >= 40 ? 'text-amber-600' : 'text-red-600'}`}>
            {summary.overallAvgQuizScore != null ? `${summary.overallAvgQuizScore}%` : 'N/A'}
          </div>
          <div className="text-sm text-gray-500">Avg Quiz Score</div>
        </div>
        <div className="stat-card text-center">
          <div className="text-3xl font-bold text-ss-blue">{summary.strongAreas.length}</div>
          <div className="text-sm text-gray-500">Strong Areas</div>
        </div>
      </div>

      {/* STRENGTHS & WEAKNESSES */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="stat-card border-l-4 border-green-500">
          <h3 className="font-bold text-green-600 mb-3 flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            Strengths
          </h3>
          {summary.strongAreas.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {summary.strongAreas.map((area, i) => (
                <span key={i} className="bg-green-100 text-green-700 text-sm px-3 py-1 rounded-full">{area}</span>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">No strong areas identified yet</p>
          )}
        </div>
        <div className="stat-card border-l-4 border-red-500">
          <h3 className="font-bold text-red-600 mb-3 flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            Areas for Improvement
          </h3>
          {summary.weakAreas.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {summary.weakAreas.map((area, i) => (
                <span key={i} className="bg-red-100 text-red-700 text-sm px-3 py-1 rounded-full">{area}</span>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">No weak areas identified yet</p>
          )}
        </div>
      </div>

      {/* COURSE DETAILS */}
      <div>
        <h2 className="text-xl font-bold text-gray-800 mb-4">Course Breakdown</h2>
        <div className="space-y-6">
          {courses.map((course, idx) => (
            <div key={course.courseId} className="stat-card animate-slide-up" style={{ animationDelay: `${idx * 0.1}s` }}>
              <div className="flex justify-between items-start mb-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium text-ss-blue bg-ss-blue/10 px-3 py-1 rounded-full">{course.subject}</span>
                    <span className="text-xs font-medium text-gray-500 bg-gray-100 px-3 py-1 rounded-full">{course.grade}</span>
                  </div>
                  <h3 className="font-bold text-gray-800 text-lg">{course.title}</h3>
                </div>
                <div className="text-right">
                  <div className={`text-2xl font-bold ${course.overallPercentage >= 70 ? 'text-green-600' : course.overallPercentage >= 40 ? 'text-amber-600' : 'text-red-600'}`}>
                    {course.overallPercentage}%
                  </div>
                  <div className="text-xs text-gray-400">{course.completedLessons}/{course.totalLessons} lessons</div>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-gray-100 rounded-full h-2 mb-4">
                <div className={`h-2 rounded-full transition-all ${course.overallPercentage >= 70 ? 'bg-green-500' : course.overallPercentage >= 40 ? 'bg-amber-500' : 'bg-red-500'}`}
                  style={{ width: `${course.overallPercentage}%` }} />
              </div>

              {/* Quiz Average */}
              {course.avgQuizScore != null && (
                <div className="mb-4">
                  <span className="text-sm text-gray-500">Quiz Average: </span>
                  <span className={`font-bold ${course.avgQuizScore >= 70 ? 'text-green-600' : course.avgQuizScore >= 40 ? 'text-amber-600' : 'text-red-600'}`}>
                    {course.avgQuizScore}%
                  </span>
                </div>
              )}

              {/* Lessons Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-gray-500 border-b">
                      <th className="pb-2 font-medium">Lesson</th>
                      <th className="pb-2 font-medium">Status</th>
                      <th className="pb-2 font-medium">Progress</th>
                      <th className="pb-2 font-medium">Quiz Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    {course.lessons.map(lesson => (
                      <tr key={lesson.lessonId} className="border-b border-gray-50">
                        <td className="py-2">
                          <span className="font-medium text-gray-700">{lesson.title}</span>
                          {lesson.duration && <span className="text-gray-400 ml-2">({lesson.duration}min)</span>}
                        </td>
                        <td className="py-2">
                          {lesson.completed ? (
                            <span className="text-green-600 font-medium">Completed</span>
                          ) : (
                            <span className="text-gray-400">Not started</span>
                          )}
                        </td>
                        <td className="py-2">
                          <div className="w-20 bg-gray-100 rounded-full h-1.5">
                            <div className={`h-1.5 rounded-full ${lesson.percentage >= 70 ? 'bg-green-500' : lesson.percentage >= 40 ? 'bg-amber-500' : 'bg-red-500'}`}
                              style={{ width: `${lesson.percentage || 0}%` }} />
                          </div>
                        </td>
                        <td className="py-2">
                          {lesson.quizScore != null ? (
                            <span className={`font-bold ${lesson.quizScore >= 60 ? 'text-green-600' : 'text-red-600'}`}>
                              {lesson.quizScore}%
                            </span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Course Recommendations */}
              {course.recommendations.length > 0 && (
                <div className="mt-4 bg-ss-blue/5 rounded-xl p-4">
                  <h4 className="font-semibold text-ss-blue text-sm mb-2">Recommendations</h4>
                  <ul className="space-y-1">
                    {course.recommendations.map((rec, i) => (
                      <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                        <span className="text-ss-blue mt-0.5">•</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* OVERALL RECOMMENDATIONS */}
      {overallRecommendations.length > 0 && (
        <div className="stat-card bg-gradient-to-br from-ss-blue/5 to-ss-green/5">
          <h3 className="font-bold text-ss-blue mb-3 flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            Teacher Recommendations
          </h3>
          <ul className="space-y-2">
            {overallRecommendations.map((rec, i) => (
              <li key={i} className="flex items-start gap-3 bg-white rounded-xl p-3">
                <div className="w-6 h-6 rounded-full bg-ss-blue/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-ss-blue text-xs font-bold">{i + 1}</span>
                </div>
                <span className="text-gray-700">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
