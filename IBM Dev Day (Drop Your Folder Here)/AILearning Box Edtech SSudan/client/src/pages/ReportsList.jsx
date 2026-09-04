import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useI18n } from '../i18n/I18nContext';

export default function ReportsList() {
  const { t } = useI18n();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/reports/all').then(res => {
      setReports(res.data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin w-8 h-8 border-4 border-ss-blue border-t-transparent rounded-full"></div>
    </div>
  );

  const classAvg = reports.length > 0
    ? Math.round(reports.reduce((a, r) => a + r.overallPercentage, 0) / reports.length)
    : 0;

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fade-in">
      <Link to="/dashboard" className="inline-flex items-center gap-2 text-ss-blue hover:underline text-sm">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        {t('common.back')}
      </Link>

      <div className="gradient-primary rounded-2xl p-8 text-white relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2"></div>
        <div className="relative z-10">
          <h1 className="text-3xl font-bold mb-2">Student Reports</h1>
          <p className="text-white/70">Track learner progress and recommend changes</p>
        </div>
      </div>

      {/* CLASS SUMMARY */}
      <div className="grid grid-cols-3 gap-4">
        <div className="stat-card text-center">
          <div className="text-3xl font-bold text-ss-blue">{reports.length}</div>
          <div className="text-sm text-gray-500">Total Students</div>
        </div>
        <div className="stat-card text-center">
          <div className={`text-3xl font-bold ${classAvg >= 70 ? 'text-green-600' : classAvg >= 40 ? 'text-amber-600' : 'text-red-600'}`}>
            {classAvg}%
          </div>
          <div className="text-sm text-gray-500">Class Average</div>
        </div>
        <div className="stat-card text-center">
          <div className="text-3xl font-bold text-green-600">
            {reports.filter(r => r.overallPercentage >= 70).length}
          </div>
          <div className="text-sm text-gray-500">On Track</div>
        </div>
      </div>

      {/* STUDENT LIST */}
      <div>
        <h2 className="text-xl font-bold text-gray-800 mb-4">All Students</h2>
        <div className="space-y-3">
          {reports.map((report, idx) => (
            <Link key={report.student.id} to={`/reports/student/${report.student.id}`}
              className="stat-card flex items-center justify-between hover:scale-[1.01] transition-transform"
              style={{ animationDelay: `${idx * 0.05}s` }}>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-ss-blue to-ss-green flex items-center justify-center text-white font-bold text-lg">
                  {report.student.name?.charAt(0)}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800">{report.student.name}</h3>
                  <p className="text-sm text-gray-500">{report.student.grade || ''} &bull; {report.student.school || ''}</p>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-right">
                  <div className={`text-2xl font-bold ${report.overallPercentage >= 70 ? 'text-green-600' : report.overallPercentage >= 40 ? 'text-amber-600' : 'text-red-600'}`}>
                    {report.overallPercentage}%
                  </div>
                  <div className="text-xs text-gray-400">Progress</div>
                </div>
                <div className="text-right">
                  <div className={`text-lg font-bold ${report.overallAvgQuizScore != null && report.overallAvgQuizScore >= 70 ? 'text-green-600' : report.overallAvgQuizScore != null && report.overallAvgQuizScore >= 40 ? 'text-amber-600' : 'text-gray-400'}`}>
                    {report.overallAvgQuizScore != null ? `${report.overallAvgQuizScore}%` : 'N/A'}
                  </div>
                  <div className="text-xs text-gray-400">Quiz Avg</div>
                </div>
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
