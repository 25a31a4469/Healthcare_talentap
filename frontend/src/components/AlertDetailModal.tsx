import React, { useState } from 'react';
import {
  X,
  AlertTriangle,
  ShieldAlert,
  CheckCircle2,
  FileText,
  HelpCircle,
  Stethoscope,
  Info,
  Clock,
  UserCheck
} from 'lucide-react';
import { SafetyAlert } from '../types';
import { api } from '../api/client';

interface Props {
  alert: SafetyAlert | null;
  onClose: () => void;
  onAcknowledged: (updatedAlertId: string) => void;
}

export const AlertDetailModal: React.FC<Props> = ({ alert, onClose, onAcknowledged }) => {
  if (!alert) return null;

  const [reviewerId, setReviewerId] = useState('Dr. S. Chen, PharmD');
  const [reviewNotes, setReviewNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'HIGH':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'MEDIUM':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      case 'LOW':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      default:
        return 'bg-slate-100 text-slate-800 border-slate-300';
    }
  };

  const handleAction = async (action: 'ACKNOWLEDGE' | 'OVERRIDE') => {
    if (!reviewerId.trim()) {
      setError('Please provide a reviewer / clinician identifier.');
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      await api.acknowledgeAlert(alert.id, {
        reviewer_id: reviewerId.trim(),
        action,
        review_notes: reviewNotes.trim() || undefined
      });
      onAcknowledged(alert.id);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to submit alert acknowledgement.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex items-start justify-between">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold border ${getSeverityBadge(alert.severity)}`}>
                {alert.severity} PRIORITY
              </span>
              <span className="text-xs font-mono text-slate-500">{alert.id}</span>
              {alert.patient_id && (
                <span className="text-xs bg-slate-200 text-slate-700 px-2 py-0.5 rounded font-medium">
                  {alert.patient_id}
                </span>
              )}
            </div>
            <h3 className="text-lg font-bold text-slate-900 leading-tight">
              {alert.title}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-200 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body: 7 Evidence-backed points */}
        <div className="p-6 overflow-y-auto space-y-5 text-sm">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-xs">
              {error}
            </div>
          )}

          {/* 1. What Detected */}
          <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200">
            <div className="flex items-center space-x-2 text-slate-700 font-semibold mb-1">
              <Info className="w-4 h-4 text-blue-600" />
              <span>1. What Was Detected</span>
            </div>
            <p className="text-slate-800 leading-relaxed pl-6">
              {alert.what_detected}
            </p>
          </div>

          {/* 2. Medicines Involved */}
          <div>
            <span className="font-semibold text-slate-700 block mb-1.5">2. Medicines Involved:</span>
            <div className="flex flex-wrap gap-1.5 pl-2">
              {alert.drugs_involved.map((drug, i) => (
                <span
                  key={i}
                  className="px-2.5 py-1 bg-blue-50 text-blue-900 border border-blue-200 rounded-md font-medium text-xs"
                >
                  {drug}
                </span>
              ))}
            </div>
          </div>

          {/* 3. Why Flagged */}
          <div>
            <span className="font-semibold text-slate-700 block mb-1">3. Why The System Flagged This Finding:</span>
            <p className="text-slate-700 bg-amber-50/60 p-3 rounded-lg border border-amber-200/80 leading-relaxed">
              {alert.why_flagged}
            </p>
          </div>

          {/* 4. Exact Rule & Citation */}
          <div className="border border-slate-200 p-3 rounded-lg bg-white space-y-1">
            <span className="font-semibold text-slate-700 flex items-center space-x-2">
              <FileText className="w-4 h-4 text-slate-500" />
              <span>4. Exact Rule Reference & Grounded Source:</span>
            </span>
            <p className="text-xs font-mono text-slate-600 pl-6">
              Rule ID: <strong>{alert.rule_id || 'SYSTEM-DETERMINISTIC'}</strong>
            </p>
            <p className="text-xs text-slate-600 pl-6">
              Source: <em className="text-slate-800">{alert.evidence_source}</em>
            </p>
          </div>

          {/* 5. Missing Patient Info */}
          <div>
            <span className="font-semibold text-slate-700 flex items-center space-x-2 mb-1">
              <HelpCircle className="w-4 h-4 text-purple-600" />
              <span>5. Missing Information & Limitations:</span>
            </span>
            {alert.missing_patient_info && alert.missing_patient_info.length > 0 ? (
              <ul className="list-disc list-inside text-slate-700 pl-4 space-y-0.5 text-xs">
                {alert.missing_patient_info.map((item, idx) => (
                  <li key={idx} className="text-amber-800 font-medium">{item}</li>
                ))}
              </ul>
            ) : (
              <p className="text-xs text-slate-500 pl-6">
                All primary clinical parameters evaluated were present in the record.
              </p>
            )}
            {alert.limitations_disclaimer && (
              <p className="text-[11px] text-slate-500 italic pl-6 mt-1">
                Notice: {alert.limitations_disclaimer}
              </p>
            )}
          </div>

          {/* 6. Clinician Review Recommendation */}
          <div className="bg-blue-50 p-3.5 rounded-lg border border-blue-200 text-blue-950">
            <div className="flex items-center space-x-2 font-semibold mb-1">
              <Stethoscope className="w-4 h-4 text-blue-700" />
              <span>6. Recommended Clinician Review Action:</span>
            </div>
            <p className="text-xs pl-6 leading-relaxed font-medium">
              {alert.clinical_recommendation}
            </p>
          </div>

          {/* 7. Verification Status */}
          <div className="flex items-center space-x-2 text-xs bg-slate-100 p-2.5 rounded-md text-slate-600">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>
              <strong>7. Verification Status:</strong>{' '}
              {alert.is_deterministic
                ? 'Grounded in deterministic clinical reference database. No automated AI hallucinations.'
                : 'Fuzzy / statistical approximation; clinician verification required.'}
            </span>
          </div>

          {/* Acknowledgement Status / Form */}
          <div className="border-t border-slate-200 pt-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-bold text-slate-900 text-sm">Review & Acknowledgement</span>
              {alert.is_acknowledged ? (
                <span className="flex items-center text-xs font-semibold text-emerald-700 bg-emerald-100 px-2.5 py-1 rounded-full">
                  <UserCheck className="w-3.5 h-3.5 mr-1" />
                  Reviewed by {alert.acknowledged_by || 'Clinician'}
                </span>
              ) : (
                <span className="text-xs text-amber-600 bg-amber-50 px-2.5 py-0.5 rounded border border-amber-200">
                  Unresolved Finding
                </span>
              )}
            </div>

            {alert.is_acknowledged ? (
              <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs space-y-1">
                <p>
                  <strong>Review Status:</strong> {alert.status}
                </p>
                {alert.acknowledged_at && (
                  <p className="text-slate-500">
                    Timestamp: {new Date(alert.acknowledged_at).toLocaleString()}
                  </p>
                )}
                {alert.review_notes && (
                  <p className="text-slate-700 mt-1 italic">
                    Clinical Note: "{alert.review_notes}"
                  </p>
                )}
              </div>
            ) : (
              <div className="space-y-3 bg-slate-50 p-3.5 rounded-lg border border-slate-200">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Reviewing Clinician Synthetic Identifier:
                  </label>
                  <input
                    type="text"
                    value={reviewerId}
                    onChange={(e) => setReviewerId(e.target.value)}
                    className="w-full px-3 py-1.5 border border-slate-300 rounded text-xs focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="e.g. Dr. S. Chen, PharmD"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Clinical Review Note (Optional):
                  </label>
                  <textarea
                    value={reviewNotes}
                    onChange={(e) => setReviewNotes(e.target.value)}
                    rows={2}
                    className="w-full px-3 py-1.5 border border-slate-300 rounded text-xs focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Document clinical rationale, dose adjustments, or monitoring orders..."
                  />
                </div>
                <div className="flex space-x-2 pt-1">
                  <button
                    disabled={submitting}
                    onClick={() => handleAction('ACKNOWLEDGE')}
                    className="flex-1 bg-navy-900 text-white font-medium py-2 px-3 rounded text-xs hover:bg-navy-800 transition shadow disabled:opacity-50"
                  >
                    Acknowledge & Accept Risk
                  </button>
                  <button
                    disabled={submitting}
                    onClick={() => handleAction('OVERRIDE')}
                    className="flex-1 bg-slate-200 text-slate-800 font-medium py-2 px-3 rounded text-xs hover:bg-slate-300 transition disabled:opacity-50"
                  >
                    Clinical Override
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-slate-100 border-t border-slate-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-200 transition"
          >
            Close Detail
          </button>
        </div>
      </div>
    </div>
  );
};
