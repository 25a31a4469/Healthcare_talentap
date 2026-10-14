import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  Search,
  Plus,
  Trash2,
  AlertTriangle,
  CheckCircle2,
  Pill,
  Sparkles,
  Info,
  Clock,
  ChevronDown,
  RefreshCw,
  ExternalLink
} from 'lucide-react';
import { api } from '../api/client';
import { Patient, MedicineInput, MedicationAnalysis, SafetyAlert, MedicineResolutionResult } from '../types';

interface Props {
  initialPatient?: Patient | null;
  onSelectAlert: (alert: SafetyAlert) => void;
}

export const SafetyCheckerPage: React.FC<Props> = ({ initialPatient, onSelectAlert }) => {
  const [patientList, setPatientList] = useState<Patient[]>([]);
  const [selectedPatientId, setSelectedPatientId] = useState<string>(initialPatient?.id || '');

  // Patient Clinical Context Form
  const [age, setAge] = useState<number>(initialPatient?.age || 55);
  const [gender, setGender] = useState<string>(initialPatient?.gender || 'Male');
  const [conditions, setConditions] = useState<string>(initialPatient?.conditions?.join(', ') || '');
  const [allergies, setAllergies] = useState<string>(initialPatient?.allergies?.join(', ') || '');
  const [egfr, setEgfr] = useState<string>(initialPatient?.egfr !== undefined && initialPatient?.egfr !== null ? String(initialPatient.egfr) : '');
  const [isPregnant, setIsPregnant] = useState<string>(
    initialPatient?.is_pregnant === true ? 'yes' : (initialPatient?.is_pregnant === false ? 'no' : 'unknown')
  );

  // Medication Rows
  const [meds, setMeds] = useState<MedicineInput[]>(
    initialPatient?.medications && initialPatient.medications.length > 0
      ? initialPatient.medications.map(m => ({
          name: m.raw_name,
          dose: m.dose || '',
          frequency: m.frequency || '',
          route: m.route || 'Oral'
        }))
      : [
          { name: 'Coumadin 5mg', dose: '5 mg', frequency: 'once daily' },
          { name: 'Diflucan 200mg', dose: '200 mg', frequency: 'once daily' }
        ]
  );

  // Live Resolution Previews for each row
  const [resolutions, setResolutions] = useState<Record<number, MedicineResolutionResult>>({});
  const [resolvingIdx, setResolvingIdx] = useState<number | null>(null);

  // Analysis Result
  const [analysis, setAnalysis] = useState<MedicationAnalysis | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Preload patient list
  useEffect(() => {
    api.getPatients().then(setPatientList).catch(console.error);
  }, []);

  // When selectedPatientId changes, update fields
  const handleSelectPatient = (ptId: string) => {
    setSelectedPatientId(ptId);
    if (!ptId) return;
    const pt = patientList.find(p => p.id === ptId);
    if (pt) {
      setAge(pt.age);
      setGender(pt.gender);
      setConditions(pt.conditions?.join(', ') || '');
      setAllergies(pt.allergies?.join(', ') || '');
      setEgfr(pt.egfr !== null && pt.egfr !== undefined ? String(pt.egfr) : '');
      setIsPregnant(pt.is_pregnant === true ? 'yes' : (pt.is_pregnant === false ? 'no' : 'unknown'));
      if (pt.medications && pt.medications.length > 0) {
        const mapped = pt.medications.map(m => ({
          name: m.raw_name,
          dose: m.dose || '',
          frequency: m.frequency || '',
          route: m.route || 'Oral'
        }));
        setMeds(mapped);
        // Trigger live resolution for loaded meds
        mapped.forEach((m, idx) => resolveSingleRow(idx, m.name));
      }
    }
  };

  const resolveSingleRow = async (index: number, name: string) => {
    if (!name.trim()) return;
    setResolvingIdx(index);
    try {
      const res = await api.resolveMedicine(name.trim());
      setResolutions(prev => ({ ...prev, [index]: res }));
    } catch (err) {
      // Non-blocking
    } finally {
      setResolvingIdx(null);
    }
  };

  const handleMedChange = (index: number, field: keyof MedicineInput, val: string) => {
    const updated = [...meds];
    updated[index][field] = val;
    setMeds(updated);
  };

  const handleAddMed = () => {
    setMeds([...meds, { name: '', dose: '', frequency: '', route: 'Oral' }]);
  };

  const handleRemoveMed = (index: number) => {
    const updated = meds.filter((_, i) => i !== index);
    setMeds(updated);
    const newRes = { ...resolutions };
    delete newRes[index];
    setResolutions(newRes);
  };

  // Run full analysis
  const handleRunAnalysis = async (e: React.FormEvent) => {
    e.preventDefault();
    const validMeds = meds.filter(m => m.name.trim());
    if (validMeds.length === 0) {
      setError('Please add at least one medication to analyze.');
      return;
    }

    setAnalyzing(true);
    setError(null);
    try {
      const condList = conditions.split(',').map(c => c.trim()).filter(Boolean);
      const algList = allergies.split(',').map(a => a.trim()).filter(Boolean);

      const payload = {
        patient_id: selectedPatientId || undefined,
        age: Number(age),
        gender,
        conditions: condList,
        allergies: algList,
        egfr: egfr ? Number(egfr) : null,
        is_pregnant: isPregnant === 'yes' ? true : (isPregnant === 'no' ? false : null),
        medications: validMeds
      };

      const result = await api.runSafetyCheck(payload);
      setAnalysis(result);
    } catch (err: any) {
      setError(err.message || 'Error executing safety check pipeline');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900">Medication Safety Decision Support Checker</h1>
        <p className="text-xs text-slate-500">
          Analyze complex medication regimens through the 10-step deterministic clinical validation pipeline.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Form (Inputs) */}
        <div className="lg:col-span-5 space-y-4">
          <form onSubmit={handleRunAnalysis} className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4 text-xs">
            {/* Quick Patient Loader */}
            <div>
              <label className="block font-bold text-slate-700 mb-1">
                Select Existing Patient Cohort Record (Optional):
              </label>
              <select
                value={selectedPatientId}
                onChange={(e) => handleSelectPatient(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-slate-50 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="">-- Manual Ad-Hoc Test Entry --</option>
                {patientList.map(p => (
                  <option key={p.id} value={p.id}>
                    {p.id} ({p.age}y {p.gender}) • {p.medications?.length || 0} meds
                  </option>
                ))}
              </select>
            </div>

            {/* Clinical Parameters */}
            <div className="border-t border-slate-200 pt-3 space-y-3">
              <span className="font-bold text-slate-800 text-[11px] uppercase tracking-wider block">
                Patient Clinical Context
              </span>

              <div className="grid grid-cols-2 gap-2.5">
                <div>
                  <label className="block text-slate-600 mb-1">Age:</label>
                  <input
                    type="number"
                    value={age}
                    onChange={(e) => setAge(Number(e.target.value))}
                    className="w-full px-2.5 py-1.5 border border-slate-300 rounded text-xs"
                    required
                  />
                </div>
                <div>
                  <label className="block text-slate-600 mb-1">Gender:</label>
                  <select
                    value={gender}
                    onChange={(e) => setGender(e.target.value)}
                    className="w-full px-2.5 py-1.5 border border-slate-300 rounded text-xs"
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Unknown">Unknown</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2.5">
                <div>
                  <label className="block text-slate-600 mb-1">eGFR (mL/min/1.73m²):</label>
                  <input
                    type="number"
                    value={egfr}
                    onChange={(e) => setEgfr(e.target.value)}
                    placeholder="Leave empty if unrecorded"
                    step="0.1"
                    className="w-full px-2.5 py-1.5 border border-slate-300 rounded text-xs"
                  />
                </div>
                <div>
                  <label className="block text-slate-600 mb-1">Pregnancy:</label>
                  <select
                    value={isPregnant}
                    onChange={(e) => setIsPregnant(e.target.value)}
                    className="w-full px-2.5 py-1.5 border border-slate-300 rounded text-xs"
                  >
                    <option value="unknown">Unknown</option>
                    <option value="no">Not Pregnant</option>
                    <option value="yes">Pregnant</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-600 mb-1">Diagnosed Conditions (comma-separated):</label>
                <input
                  type="text"
                  value={conditions}
                  onChange={(e) => setConditions(e.target.value)}
                  placeholder="e.g. Peptic Ulcer, Asthma, CKD"
                  className="w-full px-2.5 py-1.5 border border-slate-300 rounded text-xs"
                />
              </div>

              <div>
                <label className="block text-slate-600 mb-1">Known Allergies (comma-separated):</label>
                <input
                  type="text"
                  value={allergies}
                  onChange={(e) => setAllergies(e.target.value)}
                  placeholder="e.g. Penicillin"
                  className="w-full px-2.5 py-1.5 border border-slate-300 rounded text-xs"
                />
              </div>
            </div>

            {/* Prescriptions List */}
            <div className="border-t border-slate-200 pt-3 space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-800 text-[11px] uppercase tracking-wider">
                  Medication Orders ({meds.length})
                </span>
                <button
                  type="button"
                  onClick={handleAddMed}
                  className="text-xs text-blue-600 font-semibold hover:underline flex items-center space-x-1"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add Medicine</span>
                </button>
              </div>

              <div className="space-y-2">
                {meds.map((m, idx) => {
                  const res = resolutions[idx];
                  return (
                    <div key={idx} className="p-3 border border-slate-200 rounded-lg bg-slate-50 space-y-2">
                      <div className="flex gap-2 items-center">
                        <input
                          type="text"
                          value={m.name}
                          onChange={(e) => handleMedChange(idx, 'name', e.target.value)}
                          onBlur={(e) => resolveSingleRow(idx, e.target.value)}
                          placeholder="Medicine name (e.g. Coumadin or Metformn)"
                          required
                          className="flex-1 px-2.5 py-1.5 border border-slate-300 rounded text-xs bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 font-medium"
                        />
                        <input
                          type="text"
                          value={m.dose || ''}
                          onChange={(e) => handleMedChange(idx, 'dose', e.target.value)}
                          placeholder="Dose"
                          className="w-20 px-2.5 py-1.5 border border-slate-300 rounded text-xs bg-white"
                        />
                        {meds.length > 1 && (
                          <button
                            type="button"
                            onClick={() => handleRemoveMed(idx)}
                            className="text-red-500 hover:text-red-700 p-1"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>

                      {/* Live Resolution Feedback Pill */}
                      {res && (
                        <div className="text-[11px] flex items-center justify-between bg-white px-2.5 py-1 rounded border border-slate-200">
                          <div className="flex items-center space-x-1.5">
                            <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                            <span>
                              Resolved: <strong className="text-slate-800">{res.resolved_generic || 'Ambiguous'}</strong>
                            </span>
                            {res.brand_name && (
                              <span className="text-slate-400">({res.brand_name})</span>
                            )}
                          </div>
                          <span
                            className={`px-1.5 py-0.2 rounded font-mono text-[10px] ${
                              res.is_ambiguous
                                ? 'bg-amber-100 text-amber-800'
                                : res.match_score >= 90
                                ? 'bg-emerald-100 text-emerald-800'
                                : 'bg-blue-100 text-blue-800'
                            }`}
                          >
                            {res.match_method} ({Math.round(res.match_score)}%)
                          </span>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {error && (
              <div className="p-3 bg-red-50 text-red-700 rounded-lg text-xs border border-red-200">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={analyzing}
              className="w-full py-3 bg-navy-900 text-white rounded-lg font-bold text-xs hover:bg-navy-800 transition shadow flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {analyzing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin text-blue-400" />
                  <span>Evaluating 10-Step Clinical Pipeline...</span>
                </>
              ) : (
                <>
                  <ShieldAlert className="w-4 h-4 text-blue-400" />
                  <span>Execute Clinical Safety Analysis</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Right Output (Pipeline & Findings) */}
        <div className="lg:col-span-7 space-y-4">
          {!analysis && !analyzing ? (
            <div className="bg-white rounded-xl border border-slate-200 p-10 text-center space-y-4 shadow-sm min-h-[450px] flex flex-col items-center justify-center">
              <div className="w-14 h-14 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center">
                <ShieldAlert className="w-7 h-7" />
              </div>
              <div className="space-y-1 max-w-sm">
                <h3 className="font-bold text-slate-800 text-base">Awaiting Medication Input</h3>
                <p className="text-xs text-slate-500">
                  Select a test patient or enter prescriptions on the left to evaluate potential drug-drug interactions, duplicate active ingredients, and contraindications.
                </p>
              </div>
              <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200 text-left text-[11px] text-slate-600 space-y-1.5 w-full max-w-md">
                <span className="font-bold text-slate-800 block">Demonstration Quick-Loads:</span>
                <div className="flex flex-wrap gap-1.5">
                  <button
                    onClick={() => handleSelectPatient('SYN-PT-1001')}
                    className="px-2 py-1 bg-white border border-slate-200 rounded hover:border-blue-400 transition"
                  >
                    1. Warfarin + Fluconazole DDI
                  </button>
                  <button
                    onClick={() => handleSelectPatient('SYN-PT-1002')}
                    className="px-2 py-1 bg-white border border-slate-200 rounded hover:border-blue-400 transition"
                  >
                    2. Tylenol + Panadol Duplicate
                  </button>
                  <button
                    onClick={() => handleSelectPatient('SYN-PT-1003')}
                    className="px-2 py-1 bg-white border border-slate-200 rounded hover:border-blue-400 transition"
                  >
                    3. Metformin in eGFR 24
                  </button>
                  <button
                    onClick={() => handleSelectPatient('SYN-PT-1004')}
                    className="px-2 py-1 bg-white border border-slate-200 rounded hover:border-blue-400 transition"
                  >
                    4. Misspelled "Lipitorr" & "Metformn"
                  </button>
                </div>
              </div>
            </div>
          ) : analysis ? (
            <div className="space-y-4">
              {/* Summary Metrics Bar */}
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between text-xs">
                <div>
                  <span className="text-slate-500 block">Analysis Results</span>
                  <span className="font-bold text-slate-900 text-sm">
                    {analysis.total_alerts_prioritised} Clinical Finding{analysis.total_alerts_prioritised !== 1 ? 's' : ''}
                  </span>
                </div>

                <div className="flex items-center space-x-3">
                  <span className="px-2 py-1 bg-red-100 text-red-800 rounded font-bold border border-red-200">
                    {analysis.high_priority_count} HIGH
                  </span>
                  <span className="px-2 py-1 bg-amber-100 text-amber-800 rounded font-bold border border-amber-200">
                    {analysis.medium_priority_count} MEDIUM
                  </span>
                  <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded font-bold border border-purple-200">
                    {analysis.missing_data_warnings_count} LIMITATION
                  </span>
                </div>
              </div>

              {/* Resolved Medications Strip */}
              {analysis.resolved_medications && analysis.resolved_medications.length > 0 && (
                <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-1.5">
                  <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider block">
                    Medicine Resolution Audit:
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {analysis.resolved_medications.map((m, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center px-2 py-1 rounded bg-white border border-slate-200 text-xs shadow-2xs"
                      >
                        <span className="text-slate-500 font-mono text-[10px] mr-1">'{m.original_input}'</span>
                        <span className="text-slate-400 mr-1">→</span>
                        <strong className="text-slate-900 font-semibold">{m.resolved_generic || 'Ambiguous'}</strong>
                        <span className="ml-1.5 text-[10px] text-blue-700 bg-blue-50 px-1 rounded">
                          {Math.round(m.match_score)}%
                        </span>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Alerts List */}
              <div className="space-y-3">
                {analysis.alerts.length === 0 ? (
                  <div className="bg-emerald-50 border border-emerald-200 p-8 rounded-xl text-center text-emerald-900 space-y-2">
                    <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto" />
                    <h4 className="font-bold text-sm">No Safety Issues Detected</h4>
                    <p className="text-xs text-emerald-700 max-w-md mx-auto">
                      All prescribed medications passed supported reference checks for drug-drug interactions, duplicate therapies, renal thresholds, and patient contraindications.
                    </p>
                  </div>
                ) : (
                  analysis.alerts.map((alert) => (
                    <div
                      key={alert.id}
                      onClick={() => onSelectAlert(alert)}
                      className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm hover:border-blue-400 transition cursor-pointer space-y-2.5"
                    >
                      <div className="flex items-start justify-between gap-3">
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
                            <span className="text-xs font-mono text-slate-400">
                              {alert.category.replace(/_/g, ' ')}
                            </span>
                          </div>
                          <h4 className="font-bold text-sm text-slate-900">
                            {alert.title}
                          </h4>
                        </div>
                        <span className="text-xs text-blue-600 font-semibold flex items-center shrink-0">
                          View Evidence <ExternalLink className="w-3 h-3 ml-1" />
                        </span>
                      </div>

                      <p className="text-xs text-slate-700 leading-relaxed">
                        {alert.what_detected}
                      </p>

                      <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200 text-xs text-slate-700">
                        <span className="font-semibold text-slate-800">Action: </span>
                        {alert.clinical_recommendation}
                      </div>

                      <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
                        <span>Rule: <strong>{alert.rule_id}</strong></span>
                        <span>{alert.evidence_source}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
};
