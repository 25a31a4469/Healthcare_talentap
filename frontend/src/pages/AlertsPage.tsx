import React, { useState, useEffect } from 'react';
import {
  BellRing,
  Search,
  Filter,
  CheckCircle2,
  Clock,
  ExternalLink,
  RefreshCw,
  AlertTriangle,
  UserCheck
} from 'lucide-react';
import { api } from '../api/client';
import { SafetyAlert } from '../types';

interface Props {
  onSelectAlert: (alert: SafetyAlert) => void;
}

export const AlertsPage: React.FC<Props> = ({ onSelectAlert }) => {
  const [alerts, setAlerts] = useState<SafetyAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const isAck = statusFilter === 'acknowledged' ? true : (statusFilter === 'unresolved' ? false : undefined);
      const res = await api.getAlerts({
        search: search.trim() || undefined,
        severity: severityFilter || undefined,
        category: categoryFilter || undefined,
        is_acknowledged: isAck
      });
      setAlerts(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [search, severityFilter, categoryFilter, statusFilter]);

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'HIGH':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'MEDIUM':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'LOW':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-slate-100 text-slate-800 border-slate-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Medication Safety Alerts Management</h1>
          <p className="text-xs text-slate-500">
            Review, triage, and acknowledge prioritized clinical findings grounded in authoritative reference rules.
          </p>
        </div>
        <button
          onClick={fetchAlerts}
          className="px-3 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg text-xs font-semibold hover:bg-slate-50 transition flex items-center space-x-1.5 shadow-sm"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Alerts</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row gap-3 items-center justify-between">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search alerts by title or description..."
            className="w-full pl-9 pr-3 py-2 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto text-xs">
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="border border-slate-200 rounded-lg px-2.5 py-2 bg-slate-50 focus:outline-none"
          >
            <option value="">All Severities</option>
            <option value="HIGH">High Priority</option>
            <option value="MEDIUM">Medium Priority</option>
            <option value="LOW">Low / Info</option>
          </select>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="border border-slate-200 rounded-lg px-2.5 py-2 bg-slate-50 focus:outline-none"
          >
            <option value="">All Risk Categories</option>
            <option value="DRUG_DRUG_INTERACTION">Drug Interactions</option>
            <option value="DUPLICATE_ACTIVE_INGREDIENT">Duplicate Ingredients</option>
            <option value="DUPLICATE_THERAPY">Duplicate Therapy</option>
            <option value="RENAL_RISK">Renal Risks</option>
            <option value="CONTRAINDICATION">Contraindications</option>
            <option value="ALLERGY_RISK">Allergy Risks</option>
            <option value="NAME_AMBIGUITY">Name Ambiguity</option>
            <option value="MISSING_DATA_LIMITATION">Missing Data Limitation</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="border border-slate-200 rounded-lg px-2.5 py-2 bg-slate-50 focus:outline-none"
          >
            <option value="">All Review Statuses</option>
            <option value="unresolved">Unresolved Pending</option>
            <option value="acknowledged">Acknowledged / Reviewed</option>
          </select>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase text-[10px] tracking-wider">
                <th className="py-3 px-4">Alert ID</th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Category & Title</th>
                <th className="py-3 px-4">Patient ID</th>
                <th className="py-3 px-4">Medicines Involved</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={7} className="text-center py-10 text-slate-400">
                    <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-600" />
                    Loading alerts...
                  </td>
                </tr>
              ) : alerts.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-12 text-slate-400">
                    No safety alerts matching the specified criteria.
                  </td>
                </tr>
              ) : (
                alerts.map((alert) => (
                  <tr
                    key={alert.id}
                    className="hover:bg-slate-50/80 transition-colors cursor-pointer"
                    onClick={() => onSelectAlert(alert)}
                  >
                    <td className="py-3 px-4 font-mono font-bold text-slate-900">
                      {alert.id}
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getSeverityBadge(alert.severity)}`}>
                        {alert.severity}
                      </span>
                    </td>
                    <td className="py-3 px-4 max-w-xs">
                      <div className="font-semibold text-slate-900 truncate">{alert.title}</div>
                      <div className="text-[11px] text-slate-400">
                        {alert.category.replace(/_/g, ' ')}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-slate-700 font-mono">
                      {alert.patient_id || 'Ad-Hoc'}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex flex-wrap gap-1 max-w-xs">
                        {alert.drugs_involved.map((d, i) => (
                          <span key={i} className="px-1.5 py-0.5 bg-slate-100 text-slate-700 rounded text-[10px]">
                            {d}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      {alert.is_acknowledged ? (
                        <span className="inline-flex items-center text-[10px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded">
                          <UserCheck className="w-3 h-3 mr-1" />
                          Reviewed
                        </span>
                      ) : (
                        <span className="text-[10px] font-semibold text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded">
                          Unresolved
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectAlert(alert);
                        }}
                        className="text-xs text-blue-600 font-semibold hover:underline"
                      >
                        Inspect Evidence
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
