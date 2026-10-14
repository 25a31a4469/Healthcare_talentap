import React, { useState, useEffect } from 'react';
import {
  Users,
  Activity,
  AlertTriangle,
  ShieldAlert,
  Clock,
  Sparkles,
  ArrowUpRight,
  Filter,
  CheckCircle2,
  RefreshCw,
  ShieldCheck
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, PieChart, Pie
} from 'recharts';
import { api } from '../api/client';
import { DashboardSummary, SafetyAlert } from '../types';

interface Props {
  onNavigate: (tab: any) => void;
  onSelectAlert: (alert: SafetyAlert) => void;
}

export const DashboardPage: React.FC<Props> = ({ onNavigate, onSelectAlert }) => {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');

  const fetchSummary = async () => {
    setLoading(true);
    setError(null);
    try {
      const summary = await api.getDashboardSummary();
      setData(summary);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard summary');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center space-y-3 text-slate-500 text-sm">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
          <span>Loading clinical decision metrics...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-xl text-red-800 space-y-3">
        <div className="flex items-center space-x-2 font-bold text-base">
          <AlertTriangle className="w-5 h-5 text-red-600" />
          <span>Dashboard Connection Error</span>
        </div>
        <p className="text-sm">{error}</p>
        <button
          onClick={fetchSummary}
          className="px-4 py-2 bg-red-600 text-white rounded-lg text-xs font-semibold hover:bg-red-700 transition"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  if (!data) return null;

  // Chart data preparation
  const categoryChartData = Object.entries(data.alert_distribution || {})
    .filter(([_, count]) => count > 0)
    .map(([cat, count]) => ({
      name: cat.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase()),
      count
    }));

  const severityChartData = [
    { name: 'High Priority', value: data.severity_distribution?.HIGH || 0, color: '#ef4444' },
    { name: 'Medium Priority', value: data.severity_distribution?.MEDIUM || 0, color: '#f59e0b' },
    { name: 'Low / Info', value: (data.severity_distribution?.LOW || 0) + (data.severity_distribution?.INFORMATIONAL || 0), color: '#3b82f6' }
  ].filter(d => d.value > 0);

  const filteredRecentAlerts = data.recent_alerts.filter(a => {
    if (severityFilter === 'ALL') return true;
    return a.severity === severityFilter;
  });

  return (
    <div className="space-y-6">
      {/* Top Banner / Dataset Status */}
      <div className="bg-gradient-to-r from-navy-950 via-navy-900 to-slate-900 rounded-xl text-white p-6 shadow-md border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-blue-500/20 text-blue-300 border border-blue-500/40">
              Active Reference Rules {data.active_reference_version}
            </span>
            <span className="text-xs text-slate-400">• Deterministic CDSS Active</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Medication Safety Clinical Overview
          </h1>
          <p className="text-sm text-slate-300 max-w-2xl">
            Real-time decision support evaluating drug-drug interactions, duplicate therapies, renal clearance thresholds, and patient-specific contraindications.
          </p>
        </div>
        <div className="flex flex-wrap gap-2.5">
          <button
            onClick={() => onNavigate('checker')}
            className="px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow transition flex items-center space-x-1.5"
          >
            <ShieldAlert className="w-4 h-4" />
            <span>Launch Safety Checker</span>
          </button>
          <button
            onClick={fetchSummary}
            className="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs transition border border-slate-700"
            title="Refresh dashboard metrics"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 6 Key Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Patient Records</span>
            <Users className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{data.patient_count}</div>
          <div className="text-[11px] text-slate-400">Authorized Cohort</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Reviews Done</span>
            <Activity className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{data.reviews_count}</div>
          <div className="text-[11px] text-slate-400">Total Safety Analyses</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-red-200 bg-red-50/20 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-red-600 text-xs font-semibold">
            <span>High Priority Risks</span>
            <AlertTriangle className="w-4 h-4 text-red-600" />
          </div>
          <div className="text-2xl font-bold text-red-700">{data.high_priority_alerts}</div>
          <div className="text-[11px] text-red-500 font-medium">Severe DDI / Renal / Contra</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-amber-200 bg-amber-50/20 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-amber-600 text-xs font-semibold">
            <span>Medium Priority</span>
            <ShieldAlert className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-bold text-amber-700">{data.medium_priority_alerts}</div>
          <div className="text-[11px] text-amber-500 font-medium">Dose Adjust / Warnings</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Unresolved Alerts</span>
            <Clock className="w-4 h-4 text-purple-600" />
          </div>
          <div className="text-2xl font-bold text-purple-700">{data.unresolved_alerts_count}</div>
          <div className="text-[11px] text-slate-400">Pending Review</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Manual Review</span>
            <Sparkles className="w-4 h-4 text-cyan-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{data.manual_review_needed_count}</div>
          <div className="text-[11px] text-slate-400">Ambiguity / Limitations</div>
        </div>
      </div>

      {/* Alert Fatigue Reduction Highlight Banner */}
      <div className="bg-emerald-50/70 border border-emerald-200 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-emerald-100 flex items-center justify-center text-emerald-700 font-bold shrink-0">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-emerald-950 text-sm">Alert Fatigue Reduction: -{data.alert_volume_reduction_pct || 0}% Measured Volume Reduced</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                100% Serious Retained
              </span>
            </div>
            <p className="text-emerald-800 text-[11px] mt-0.5">
              Evidence-based alert consolidation eliminates repetitive multi-ingredient alerts and groups concurrent missing lab panels. Zero serious risks suppressed.
            </p>
          </div>
        </div>

        <button
          onClick={() => onNavigate('evaluation')}
          className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow transition whitespace-nowrap self-start sm:self-auto"
        >
          View Benchmark Validation →
        </button>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Category Breakdown Bar Chart */}
        <div className="lg:col-span-2 bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-slate-900 text-sm">Alert Distribution by Risk Category</h3>
              <p className="text-xs text-slate-500">Breakdown of detected clinical hazards across patient cohort</p>
            </div>
            <span className="text-xs font-semibold text-slate-600 bg-slate-100 px-2 py-1 rounded">
              Total {data.recent_alerts.length} Flagged
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryChartData} margin={{ top: 10, right: 10, left: -20, bottom: 40 }}>
                <XAxis dataKey="name" angle={-25} textAnchor="end" interval={0} tick={{ fontSize: 10 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 10 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]}>
                  {categoryChartData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={index % 2 === 0 ? '#1e40af' : '#3b82f6'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Severity Distribution Pie Chart */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4 flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-slate-900 text-sm">Severity Proportion</h3>
            <p className="text-xs text-slate-500">Risk-first stratification ratio</p>
          </div>

          <div className="h-44 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={severityChartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={45}
                  outerRadius={70}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {severityChartData.map((entry, index) => (
                    <Cell key={`pie-cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-1.5 border-t border-slate-100 pt-3">
            {severityChartData.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-slate-600">{item.name}</span>
                </div>
                <span className="font-semibold text-slate-900">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Alerts & Analyses Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Alerts List */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h3 className="font-bold text-slate-900 text-sm">Prioritised Clinical Alerts</h3>
              <p className="text-xs text-slate-500">High & medium clinical safety risks requiring clinician evaluation</p>
            </div>
            <div className="flex items-center space-x-2">
              <Filter className="w-3.5 h-3.5 text-slate-400" />
              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="text-xs border border-slate-200 rounded-md px-2 py-1 bg-slate-50 focus:outline-none"
              >
                <option value="ALL">All Severities</option>
                <option value="HIGH">High Priority</option>
                <option value="MEDIUM">Medium Priority</option>
                <option value="LOW">Low / Info</option>
              </select>
            </div>
          </div>

          <div className="divide-y divide-slate-100">
            {filteredRecentAlerts.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-xs">
                No alerts matching the selected filter.
              </div>
            ) : (
              filteredRecentAlerts.map((alert) => (
                <div
                  key={alert.id}
                  onClick={() => onSelectAlert(alert)}
                  className="p-4 hover:bg-slate-50/80 transition-colors cursor-pointer flex items-start justify-between gap-4"
                >
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                          alert.severity === 'HIGH'
                            ? 'bg-red-100 text-red-800 border-red-200'
                            : alert.severity === 'MEDIUM'
                            ? 'bg-amber-100 text-amber-800 border-amber-200'
                            : 'bg-blue-100 text-blue-800 border-blue-200'
                        }`}
                      >
                        {alert.severity}
                      </span>
                      <span className="text-xs font-semibold text-slate-800">
                        {alert.title}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 line-clamp-1">
                      {alert.what_detected}
                    </p>
                    <div className="flex items-center space-x-3 text-[11px] text-slate-400">
                      <span>Patient: <strong>{alert.patient_id || 'Ad-Hoc'}</strong></span>
                      <span>•</span>
                      <span>Rule: <strong>{alert.rule_id || 'Deterministic'}</strong></span>
                    </div>
                  </div>

                  <div className="text-right shrink-0">
                    {alert.is_acknowledged ? (
                      <span className="inline-flex items-center text-[11px] text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded font-medium">
                        <CheckCircle2 className="w-3 h-3 mr-1" />
                        Reviewed
                      </span>
                    ) : (
                      <span className="text-[11px] text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded font-medium">
                        Unresolved
                      </span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="p-3 bg-slate-50 border-t border-slate-200 text-center">
            <button
              onClick={() => onNavigate('alerts')}
              className="text-xs text-blue-700 font-semibold hover:underline"
            >
              View All Medication Alerts & Audit History →
            </button>
          </div>
        </div>

        {/* Recent Analyses Cohort */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col justify-between">
          <div className="p-4 border-b border-slate-200">
            <h3 className="font-bold text-slate-900 text-sm">Recent Analyses Log</h3>
            <p className="text-xs text-slate-500">Audit trail of latest safety reviews</p>
          </div>

          <div className="divide-y divide-slate-100 p-2 space-y-1">
            {data.recent_analyses.map((anl) => (
              <div key={anl.id} className="p-2.5 rounded-lg hover:bg-slate-50 text-xs flex items-center justify-between">
                <div>
                  <div className="font-semibold text-slate-800">
                    {anl.patient_id || 'Direct Checker Analysis'}
                  </div>
                  <div className="text-[11px] text-slate-400">
                    {new Date(anl.created_at).toLocaleDateString()} at {new Date(anl.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-slate-900">
                    {anl.total_alerts} alert{anl.total_alerts !== 1 ? 's' : ''}
                  </div>
                  {anl.high_priority_count > 0 && (
                    <span className="text-[10px] text-red-600 font-bold">
                      {anl.high_priority_count} HIGH
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="p-3 bg-slate-50 border-t border-slate-200 text-center">
            <button
              onClick={() => onNavigate('audit')}
              className="text-xs text-slate-600 font-medium hover:underline"
            >
              Open Full Audit Log →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
