import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  Info,
  Server,
  FileText,
  Lock,
  Code2,
  ExternalLink,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import { api, BASE_URL } from '../api/client';

export const SettingsAboutPage: React.FC = () => {
  const [datasetStatus, setDatasetStatus] = useState<any | null>(null);

  useEffect(() => {
    api.getDatasetStatus().then(setDatasetStatus).catch(console.error);
  }, []);

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900">System Architecture, Privacy & Clinical Disclaimers</h1>
        <p className="text-xs text-slate-500">
          Governance policies, architectural design, data sources, and regulatory boundaries.
        </p>
      </div>

      {/* Mandatory Clinical Notice */}
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-5 text-xs text-amber-950 space-y-2">
        <div className="flex items-center space-x-2 font-bold text-sm text-amber-900">
          <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0" />
          <span>Clinical Decision Support System (CDSS) Limitations Notice</span>
        </div>
        <p className="leading-relaxed">
          <strong>H4 — The Medication Safety Second Pair of Eyes</strong> is an algorithmic research and hackathon prototype designed exclusively to aid licensed clinicians in reviewing medication lists.
        </p>
        <ul className="list-disc list-inside space-y-1 text-amber-900 font-medium pl-2">
          <li>The system <strong>NEVER</strong> independently prescribes, discontinues, or alters any medication or dosage.</li>
          <li>The system is <strong>NOT</strong> medically certified, NOT CE-marked, and NOT approved by FDA as an autonomous medical device.</li>
          <li>Absence of an alert does not imply a medication regimen is entirely free of adverse effects. Clinician judgment is always paramount.</li>
        </ul>
      </div>

      {/* System Architecture */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4">
        <h3 className="font-bold text-sm text-slate-900 flex items-center space-x-2">
          <Server className="w-4 h-4 text-blue-600" />
          <span>System Architecture & Data Flow</span>
        </h3>

        <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 font-mono text-xs text-slate-700 leading-relaxed overflow-x-auto">
          <pre>{`[Prescription Input / Patient Cohort]
                 ↓
  [1. String Normalization & Cleaning]
                 ↓
  [2. RapidFuzz & Verified Brand/Generic Map] → [Ambiguity Flag & Confirmation]
                 ↓
  [3. Deterministic Clinical Rules Engine]
      ├── Drug-Drug Interactions (CPIC / FDA)
      ├── Duplicate Active Ingredients & Therapies
      ├── Renal Threshold Validation (eGFR / CrCl)
      └── Patient Contraindications & Allergies
                 ↓
  [4. Risk-First Alert Prioritisation & Deduplication]
                 ↓
  [5. Evidence-Backed 7-Point Explanation & Audit Trail]`}</pre>
        </div>
      </div>

      {/* Dataset & Reference Catalogues */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4 text-xs">
        <h3 className="font-bold text-sm text-slate-900 flex items-center space-x-2">
          <FileText className="w-4 h-4 text-purple-600" />
          <span>Active Clinical Reference Rules & Ground Truth</span>
        </h3>

        {datasetStatus ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
              <span className="text-slate-500 block text-[11px]">Rule Set Version</span>
              <strong className="text-slate-900 font-bold">{datasetStatus.version}</strong>
            </div>
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
              <span className="text-slate-500 block text-[11px]">DDI Rule Pairs</span>
              <strong className="text-slate-900 font-bold">{datasetStatus.interaction_rules_count} rules</strong>
            </div>
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
              <span className="text-slate-500 block text-[11px]">Renal Cutoff Rules</span>
              <strong className="text-slate-900 font-bold">{datasetStatus.renal_rules_count} rules</strong>
            </div>
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
              <span className="text-slate-500 block text-[11px]">Brand Mappings</span>
              <strong className="text-slate-900 font-bold">{datasetStatus.verified_brand_mappings} verified</strong>
            </div>
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
              <span className="text-slate-500 block text-[11px]">Contraindication Rules</span>
              <strong className="text-slate-900 font-bold">{datasetStatus.contraindication_rules_count} rules</strong>
            </div>
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
              <span className="text-slate-500 block text-[11px]">Synthetic Patients</span>
              <strong className="text-slate-900 font-bold">{datasetStatus.patient_records_count} loaded</strong>
            </div>
          </div>
        ) : (
          <div className="text-slate-400">Loading reference status...</div>
        )}
      </div>

      {/* Privacy & Security */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-3 text-xs text-slate-700">
        <h3 className="font-bold text-sm text-slate-900 flex items-center space-x-2">
          <Lock className="w-4 h-4 text-emerald-600" />
          <span>Security, Privacy & De-Identification Safeguards</span>
        </h3>
        <ul className="list-disc list-inside space-y-1 pl-2">
          <li><strong>No Real Patient Identifiers:</strong> Only synthetic demo IDs (<code className="font-mono text-blue-700">SYN-PT-xxxx</code>) are stored.</li>
          <li><strong>Zero Secrets in Frontend:</strong> All database credentials and clinical engines remain securely on the backend.</li>
          <li><strong>CSV Formula Injection Shield:</strong> All data export cells are sanitized to prevent DDE formula execution.</li>
          <li><strong>Interactive OpenAPI Documentation:</strong> Verified endpoints available at <a href={BASE_URL ? `${BASE_URL}/docs` : '/docs'} target="_blank" rel="noreferrer" className="text-blue-600 underline font-semibold">/docs</a>.</li>
        </ul>
      </div>
    </div>
  );
};
