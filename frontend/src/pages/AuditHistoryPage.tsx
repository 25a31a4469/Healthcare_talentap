import React, { useState, useEffect } from 'react';
import { History, ShieldCheck, UserCheck, RefreshCw, Clock, FileText } from 'lucide-react';
import { api } from '../api/client';
import { AuditLog } from '../types';

export const AuditHistoryPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const data = await api.getAuditLogs();
      setLogs(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const getActionBadge = (action: string) => {
    if (action.includes('ACKNOWLEDGE')) return 'bg-emerald-100 text-emerald-800 border-emerald-200';
    if (action.includes('ANALYSIS')) return 'bg-blue-100 text-blue-800 border-blue-200';
    if (action.includes('CREATED') || action.includes('IMPORTED')) return 'bg-purple-100 text-purple-800 border-purple-200';
    if (action.includes('DELETED')) return 'bg-red-100 text-red-800 border-red-200';
    return 'bg-slate-100 text-slate-800 border-slate-200';
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Clinical Audit Trail & Traceability</h1>
          <p className="text-xs text-slate-500">
            Immutable log of all medication safety analyses, clinician acknowledgements, overrides, and data imports.
          </p>
        </div>
        <button
          onClick={fetchLogs}
          className="px-3 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg text-xs font-semibold hover:bg-slate-50 transition flex items-center space-x-1.5 shadow-sm"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Audit Trail</span>
        </button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase text-[10px] tracking-wider">
              <tr>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Clinician / User ID</th>
                <th className="py-3 px-4">Resource Target</th>
                <th className="py-3 px-4">Action Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={5} className="text-center py-10 text-slate-400">
                    <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-600" />
                    Loading audit trail...
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="text-center py-10 text-slate-400">
                    No audit records recorded yet.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-500 whitespace-nowrap">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getActionBadge(log.action)}`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-medium text-slate-800">
                      {log.user_id}
                    </td>
                    <td className="py-3 px-4 text-slate-600 font-mono text-[11px]">
                      {log.resource_type}: <strong>{log.resource_id || 'N/A'}</strong>
                    </td>
                    <td className="py-3 px-4 text-slate-600 max-w-sm">
                      <div className="text-[11px] font-mono bg-slate-50 px-2 py-1 rounded border border-slate-200 truncate">
                        {JSON.stringify(log.details)}
                      </div>
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
