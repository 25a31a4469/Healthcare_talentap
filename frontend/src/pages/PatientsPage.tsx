import React, { useState, useEffect } from 'react';
import {
  Users,
  Search,
  Filter,
  Plus,
  Download,
  Upload,
  ChevronRight,
  Pill,
  Activity,
  AlertTriangle,
  RefreshCw,
  FileSpreadsheet,
  X,
  Check
} from 'lucide-react';
import { api } from '../api/client';
import { Patient, MedicineInput } from '../types';

interface Props {
  onCheckPatient: (patient: Patient) => void;
}

export const PatientsPage: React.FC<Props> = ({ onCheckPatient }) => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedCondition, setSelectedCondition] = useState('');
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);

  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);

  // Create Form State
  const [newId, setNewId] = useState('');
  const [newAge, setNewAge] = useState(55);
  const [newGender, setNewGender] = useState('Male');
  const [newConditions, setNewConditions] = useState('');
  const [newAllergies, setNewAllergies] = useState('');
  const [newEgfr, setNewEgfr] = useState<string>('');
  const [newPreg, setNewPreg] = useState<string>('unknown');
  const [newNotes, setNewNotes] = useState('');
  const [newMeds, setNewMeds] = useState<MedicineInput[]>([
    { name: '', dose: '', frequency: '' }
  ]);
  const [createSubmitting, setCreateSubmitting] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  // Import State
  const [importFile, setImportFile] = useState<File | null>(null);
  const [importStatus, setImportStatus] = useState<string | null>(null);
  const [importLoading, setImportLoading] = useState(false);

  const fetchPatients = async () => {
    setLoading(true);
    try {
      const pts = await api.getPatients({
        query: search.trim() || undefined,
        condition: selectedCondition.trim() || undefined
      });
      setPatients(pts);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, [search, selectedCondition]);

  const handleAddMedRow = () => {
    setNewMeds([...newMeds, { name: '', dose: '', frequency: '' }]);
  };

  const handleMedChange = (index: number, field: keyof MedicineInput, val: string) => {
    const updated = [...newMeds];
    updated[index][field] = val;
    setNewMeds(updated);
  };

  const handleRemoveMedRow = (index: number) => {
    setNewMeds(newMeds.filter((_, i) => i !== index));
  };

  const handleCreatePatient = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateSubmitting(true);
    setCreateError(null);
    try {
      const conds = newConditions.split(',').map(c => c.trim()).filter(Boolean);
      const algs = newAllergies.split(',').map(a => a.trim()).filter(Boolean);
      const validMeds = newMeds.filter(m => m.name.trim());

      const payload = {
        id: newId.trim() || undefined,
        age: Number(newAge),
        gender: newGender,
        conditions: conds,
        allergies: algs,
        egfr: newEgfr ? Number(newEgfr) : null,
        is_pregnant: newPreg === 'yes' ? true : (newPreg === 'no' ? false : null),
        notes: newNotes.trim() || undefined,
        initial_medications: validMeds
      };

      await api.createPatient(payload);
      setShowCreateModal(false);
      // Reset form
      setNewId('');
      setNewConditions('');
      setNewAllergies('');
      setNewEgfr('');
      setNewNotes('');
      setNewMeds([{ name: '', dose: '', frequency: '' }]);
      fetchPatients();
    } catch (err: any) {
      setCreateError(err.message || 'Failed to create patient');
    } finally {
      setCreateSubmitting(false);
    }
  };

  const handleImport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!importFile) return;
    setImportLoading(true);
    setImportStatus(null);
    try {
      const formData = new FormData();
      formData.append('file', importFile);
      const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/patients/import`, {
        method: 'POST',
        body: formData
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Import failed');
      }
      const data = await res.json();
      setImportStatus(`Success: ${data.message} (${data.imported_records} records added).`);
      fetchPatients();
      setTimeout(() => setShowImportModal(false), 2000);
    } catch (err: any) {
      setImportStatus(`Error: ${err.message}`);
    } finally {
      setImportLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Synthetic Patient Records</h1>
          <p className="text-xs text-slate-500">
            Manage de-identified and synthetic clinical patient profiles, medication histories, and laboratory values.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <a
            href={api.exportPatientsCsvUrl}
            className="px-3 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg text-xs font-semibold hover:bg-slate-50 transition flex items-center space-x-1.5 shadow-sm"
          >
            <Download className="w-3.5 h-3.5 text-slate-500" />
            <span>Export CSV</span>
          </a>
          <button
            onClick={() => setShowImportModal(true)}
            className="px-3 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg text-xs font-semibold hover:bg-slate-50 transition flex items-center space-x-1.5 shadow-sm"
          >
            <Upload className="w-3.5 h-3.5 text-slate-500" />
            <span>Import CSV</span>
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-navy-900 text-white rounded-lg text-xs font-semibold hover:bg-navy-800 transition flex items-center space-x-1.5 shadow-sm"
          >
            <Plus className="w-3.5 h-3.5 text-blue-400" />
            <span>Add Patient Profile</span>
          </button>
        </div>
      </div>

      {/* Filter / Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row gap-3 items-center justify-between">
        <div className="relative w-full md:w-96">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by ID, notes, or identifier..."
            className="w-full pl-9 pr-3 py-2 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center space-x-2 w-full md:w-auto">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={selectedCondition}
            onChange={(e) => setSelectedCondition(e.target.value)}
            className="text-xs border border-slate-200 rounded-lg px-3 py-2 bg-slate-50 focus:outline-none w-full md:w-auto"
          >
            <option value="">All Diagnosed Conditions</option>
            <option value="Diabetes">Type 2 Diabetes</option>
            <option value="Hypertension">Hypertension</option>
            <option value="Kidney">Kidney Disease / CKD</option>
            <option value="Asthma">Asthma</option>
            <option value="Peptic Ulcer">Peptic Ulcer</option>
            <option value="Atrial Fibrillation">Atrial Fibrillation</option>
          </select>

          <button
            onClick={fetchPatients}
            className="p-2 border border-slate-200 rounded-lg text-slate-500 hover:bg-slate-50"
            title="Refresh list"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Patients Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase text-[10px] tracking-wider">
                <th className="py-3 px-4">Patient ID</th>
                <th className="py-3 px-4">Demographics</th>
                <th className="py-3 px-4">Active Conditions</th>
                <th className="py-3 px-4">Renal Status (eGFR)</th>
                <th className="py-3 px-4">Current Medications</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={6} className="text-center py-10 text-slate-400">
                    <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-600" />
                    Loading patient cohort...
                  </td>
                </tr>
              ) : patients.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-12 text-slate-400">
                    No matching patient records found.
                  </td>
                </tr>
              ) : (
                patients.map((pt) => (
                  <tr
                    key={pt.id}
                    className="hover:bg-slate-50/80 transition-colors cursor-pointer"
                    onClick={() => setSelectedPatient(pt)}
                  >
                    <td className="py-3 px-4 font-mono font-bold text-navy-900">
                      {pt.id}
                    </td>
                    <td className="py-3 px-4 text-slate-700">
                      {pt.age} yrs • {pt.gender}
                      {pt.is_pregnant && (
                        <span className="ml-1.5 text-[10px] bg-purple-100 text-purple-800 px-1.5 py-0.5 rounded font-semibold">
                          Pregnant
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex flex-wrap gap-1 max-w-xs">
                        {pt.conditions && pt.conditions.length > 0 ? (
                          pt.conditions.slice(0, 2).map((c, i) => (
                            <span key={i} className="px-1.5 py-0.5 bg-slate-100 text-slate-700 rounded text-[11px]">
                              {c}
                            </span>
                          ))
                        ) : (
                          <span className="text-slate-400 italic">None recorded</span>
                        )}
                        {pt.conditions && pt.conditions.length > 2 && (
                          <span className="text-[10px] text-slate-400 self-center">
                            +{pt.conditions.length - 2} more
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      {pt.egfr !== null && pt.egfr !== undefined ? (
                        <span
                          className={`font-semibold px-2 py-0.5 rounded text-[11px] ${
                            pt.egfr < 30
                              ? 'bg-red-100 text-red-800 border border-red-200'
                              : pt.egfr < 60
                              ? 'bg-amber-100 text-amber-800 border border-amber-200'
                              : 'bg-emerald-50 text-emerald-800'
                          }`}
                        >
                          {pt.egfr} mL/min
                        </span>
                      ) : (
                        <span className="text-slate-400 italic text-[11px]">Unknown (Not measured)</span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-1.5 text-slate-800 font-medium">
                        <Pill className="w-3.5 h-3.5 text-blue-600" />
                        <span>{pt.medications ? pt.medications.length : 0} prescribed</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-right space-x-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onCheckPatient(pt);
                        }}
                        className="px-2.5 py-1 bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 rounded font-semibold text-xs transition"
                      >
                        Run Safety Check
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Patient Detail Drawer / Modal */}
      {selectedPatient && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/50 backdrop-blur-xs flex justify-end">
          <div className="w-full max-w-xl bg-white h-full shadow-2xl p-6 overflow-y-auto space-y-6 border-l border-slate-200 flex flex-col justify-between">
            <div className="space-y-6">
              <div className="flex items-center justify-between border-b border-slate-200 pb-4">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-bold text-lg text-navy-950">{selectedPatient.id}</span>
                    <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-medium">
                      {selectedPatient.data_source}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500">
                    Synthetic Clinical Dossier • Created {new Date(selectedPatient.created_at).toLocaleDateString()}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedPatient(null)}
                  className="p-1 text-slate-400 hover:text-slate-600 rounded"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Clinical Attributes Grid */}
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                  <span className="text-slate-500 block mb-0.5">Demographics</span>
                  <span className="font-semibold text-slate-900">{selectedPatient.age} yrs • {selectedPatient.gender}</span>
                </div>
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                  <span className="text-slate-500 block mb-0.5">Pregnancy Status</span>
                  <span className="font-semibold text-slate-900">
                    {selectedPatient.is_pregnant === true ? 'Yes' : (selectedPatient.is_pregnant === false ? 'No' : 'Unknown / Unrecorded')}
                  </span>
                </div>
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                  <span className="text-slate-500 block mb-0.5">eGFR</span>
                  <span className="font-semibold text-slate-900">
                    {selectedPatient.egfr !== null ? `${selectedPatient.egfr} ${selectedPatient.egfr_unit}` : 'Unknown'}
                  </span>
                </div>
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                  <span className="text-slate-500 block mb-0.5">Serum Creatinine</span>
                  <span className="font-semibold text-slate-900">
                    {selectedPatient.serum_creatinine !== null ? `${selectedPatient.serum_creatinine} ${selectedPatient.scr_unit}` : 'Unknown'}
                  </span>
                </div>
              </div>

              {/* Conditions & Allergies */}
              <div className="space-y-3 text-xs">
                <div>
                  <span className="font-bold text-slate-700 block mb-1">Diagnosed Conditions:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedPatient.conditions && selectedPatient.conditions.length > 0 ? (
                      selectedPatient.conditions.map((c, i) => (
                        <span key={i} className="px-2 py-1 bg-blue-50 text-blue-800 border border-blue-200 rounded">
                          {c}
                        </span>
                      ))
                    ) : (
                      <span className="text-slate-400 italic">No conditions recorded</span>
                    )}
                  </div>
                </div>

                <div>
                  <span className="font-bold text-slate-700 block mb-1">Recorded Drug Allergies:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedPatient.allergies && selectedPatient.allergies.length > 0 ? (
                      selectedPatient.allergies.map((a, i) => (
                        <span key={i} className="px-2 py-1 bg-red-50 text-red-800 border border-red-200 rounded font-semibold">
                          {a}
                        </span>
                      ))
                    ) : (
                      <span className="text-slate-400 italic">No allergies recorded</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Current Prescriptions */}
              <div className="space-y-2 text-xs">
                <span className="font-bold text-slate-700 block">Current Active Medications:</span>
                <div className="border border-slate-200 rounded-lg divide-y divide-slate-100 overflow-hidden">
                  {selectedPatient.medications && selectedPatient.medications.length > 0 ? (
                    selectedPatient.medications.map((m) => (
                      <div key={m.id} className="p-3 bg-white flex items-start justify-between">
                        <div>
                          <div className="font-bold text-slate-900">{m.raw_name}</div>
                          <div className="text-[11px] text-slate-500">
                            Generic: <strong className="text-slate-700">{m.resolved_generic_name}</strong>
                            {m.brand_name && ` (Brand: ${m.brand_name})`}
                          </div>
                          {m.dose && (
                            <div className="text-[11px] text-slate-600">
                              Dose: {m.dose} • {m.frequency || 'Daily'} • {m.route || 'Oral'}
                            </div>
                          )}
                        </div>
                        <span className="text-[10px] font-mono bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">
                          {m.resolution_method} ({Math.round(m.confidence_score * 100)}%)
                        </span>
                      </div>
                    ))
                  ) : (
                    <div className="p-4 text-center text-slate-400 italic">No medications recorded</div>
                  )}
                </div>
              </div>

              {selectedPatient.notes && (
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs text-slate-700">
                  <span className="font-bold text-slate-800 block mb-1">Clinical Intake Notes:</span>
                  <p>{selectedPatient.notes}</p>
                </div>
              )}
            </div>

            <div className="pt-4 border-t border-slate-200 flex space-x-2">
              <button
                onClick={() => {
                  onCheckPatient(selectedPatient);
                  setSelectedPatient(null);
                }}
                className="flex-1 py-2.5 bg-blue-600 text-white rounded-lg text-xs font-semibold hover:bg-blue-700 transition text-center shadow"
              >
                Launch Decision Support Analysis
              </button>
              <button
                onClick={() => setSelectedPatient(null)}
                className="px-4 py-2.5 bg-slate-100 text-slate-700 rounded-lg text-xs font-semibold hover:bg-slate-200 transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Patient Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full border border-slate-200 p-6 space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <h3 className="font-bold text-base text-slate-900">Add Synthetic Patient Record</h3>
              <button onClick={() => setShowCreateModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            {createError && (
              <div className="p-3 bg-red-50 text-red-700 rounded-lg text-xs border border-red-200">
                {createError}
              </div>
            )}

            <form onSubmit={handleCreatePatient} className="space-y-3.5 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Patient ID (Optional):</label>
                  <input
                    type="text"
                    value={newId}
                    onChange={(e) => setNewId(e.target.value)}
                    placeholder="e.g. SYN-PT-2001"
                    className="w-full px-3 py-1.5 border border-slate-300 rounded text-xs"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Age:</label>
                  <input
                    type="number"
                    value={newAge}
                    onChange={(e) => setNewAge(Number(e.target.value))}
                    min={0}
                    max={125}
                    required
                    className="w-full px-3 py-1.5 border border-slate-300 rounded text-xs"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Gender:</label>
                  <select
                    value={newGender}
                    onChange={(e) => setNewGender(e.target.value)}
                    className="w-full px-3 py-1.5 border border-slate-300 rounded text-xs"
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Unknown">Unknown</option>
                  </select>
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Pregnancy Status:</label>
                  <select
                    value={newPreg}
                    onChange={(e) => setNewPreg(e.target.value)}
                    className="w-full px-3 py-1.5 border border-slate-300 rounded text-xs"
                  >
                    <option value="unknown">Unknown / Not recorded</option>
                    <option value="no">Not Pregnant</option>
                    <option value="yes">Pregnant (True)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">eGFR (mL/min/1.73m²):</label>
                  <input
                    type="number"
                    value={newEgfr}
                    onChange={(e) => setNewEgfr(e.target.value)}
                    placeholder="e.g. 28 or 85"
                    step="0.1"
                    className="w-full px-3 py-1.5 border border-slate-300 rounded text-xs"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Allergies (comma-sep):</label>
                  <input
                    type="text"
                    value={newAllergies}
                    onChange={(e) => setNewAllergies(e.target.value)}
                    placeholder="e.g. Penicillin, Sulfa"
                    className="w-full px-3 py-1.5 border border-slate-300 rounded text-xs"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Medical Conditions (comma-sep):</label>
                <input
                  type="text"
                  value={newConditions}
                  onChange={(e) => setNewConditions(e.target.value)}
                  placeholder="e.g. Type 2 Diabetes, Peptic Ulcer, Asthma"
                  className="w-full px-3 py-1.5 border border-slate-300 rounded text-xs"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="font-semibold text-slate-700">Initial Prescriptions:</label>
                  <button
                    type="button"
                    onClick={handleAddMedRow}
                    className="text-[11px] text-blue-600 font-semibold hover:underline"
                  >
                    + Add Medicine
                  </button>
                </div>
                <div className="space-y-1.5 max-h-36 overflow-y-auto border border-slate-200 p-2 rounded-lg bg-slate-50">
                  {newMeds.map((m, idx) => (
                    <div key={idx} className="flex gap-2 items-center">
                      <input
                        type="text"
                        value={m.name}
                        onChange={(e) => handleMedChange(idx, 'name', e.target.value)}
                        placeholder="Medicine name (e.g. Metformin 500mg)"
                        className="flex-1 px-2.5 py-1 border border-slate-300 rounded text-xs bg-white"
                      />
                      <input
                        type="text"
                        value={m.dose || ''}
                        onChange={(e) => handleMedChange(idx, 'dose', e.target.value)}
                        placeholder="Dose"
                        className="w-20 px-2 py-1 border border-slate-300 rounded text-xs bg-white"
                      />
                      {newMeds.length > 1 && (
                        <button
                          type="button"
                          onClick={() => handleRemoveMedRow(idx)}
                          className="text-red-500 p-1 hover:text-red-700"
                        >
                          <X className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Notes / Intake History:</label>
                <textarea
                  value={newNotes}
                  onChange={(e) => setNewNotes(e.target.value)}
                  rows={2}
                  placeholder="Clinical background, reasons for referral..."
                  className="w-full px-3 py-1.5 border border-slate-300 rounded text-xs"
                />
              </div>

              <div className="pt-2 flex justify-end space-x-2 border-t border-slate-200">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg text-xs font-semibold hover:bg-slate-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createSubmitting}
                  className="px-4 py-2 bg-navy-900 text-white rounded-lg text-xs font-semibold hover:bg-navy-800 disabled:opacity-50"
                >
                  {createSubmitting ? 'Creating...' : 'Save Patient Profile'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* CSV Import Modal */}
      {showImportModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <div className="flex items-center space-x-2">
                <FileSpreadsheet className="w-5 h-5 text-blue-600" />
                <h3 className="font-bold text-base text-slate-900">Import CSV Patient Records</h3>
              </div>
              <button onClick={() => setShowImportModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-slate-600">
              Upload a valid CSV file with columns: <br />
              <code className="text-blue-700 font-mono text-[11px]">PatientID, Age, Gender, Conditions, Allergies, eGFR, Medications</code>
            </p>

            {importStatus && (
              <div className={`p-3 rounded-lg text-xs border ${importStatus.startsWith('Success') ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-red-50 text-red-800 border-red-200'}`}>
                {importStatus}
              </div>
            )}

            <form onSubmit={handleImport} className="space-y-4">
              <input
                type="file"
                accept=".csv"
                onChange={(e) => setImportFile(e.target.files ? e.target.files[0] : null)}
                required
                className="w-full text-xs text-slate-600 border border-slate-200 rounded-lg p-2"
              />

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowImportModal(false)}
                  className="px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-100 rounded"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={importLoading || !importFile}
                  className="px-4 py-1.5 bg-blue-600 text-white rounded text-xs font-semibold hover:bg-blue-700 disabled:opacity-50"
                >
                  {importLoading ? 'Validating & Uploading...' : 'Upload & Process'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
