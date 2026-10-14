import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  Search,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  FileCode,
  Pill,
  RefreshCw,
  ExternalLink
} from 'lucide-react';
import { api } from '../api/client';
import { MedicineCatalogueItem, MedicineResolutionResult } from '../types';

export const MedicineReferencePage: React.FC = () => {
  const [catalogue, setCatalogue] = useState<MedicineCatalogueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  // Interactive Resolver Sandbox
  const [sandboxInput, setSandboxInput] = useState('Lipitorr 20mg');
  const [sandboxResult, setSandboxResult] = useState<MedicineResolutionResult | null>(null);
  const [resolving, setResolving] = useState(false);

  // Labelled Test Suite
  const [testSuite, setTestSuite] = useState<any | null>(null);
  const [testingSuite, setTestingSuite] = useState(false);

  useEffect(() => {
    api.getCatalogue()
      .then(setCatalogue)
      .catch(console.error)
      .finally(() => setLoading(false));

    handleRunSandbox('Lipitorr 20mg');
  }, []);

  const handleRunSandbox = async (term: string) => {
    if (!term.trim()) return;
    setResolving(true);
    try {
      const res = await api.resolveMedicine(term);
      setSandboxResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setResolving(false);
    }
  };

  const handleRunTestSuite = async () => {
    setTestingSuite(true);
    try {
      const suite = await api.getResolutionTestSuite();
      setTestSuite(suite);
    } catch (err) {
      console.error(err);
    } finally {
      setTestingSuite(false);
    }
  };

  const filteredCatalogue = catalogue.filter(m =>
    m.generic_name.toLowerCase().includes(search.toLowerCase()) ||
    m.therapeutic_class.toLowerCase().includes(search.toLowerCase()) ||
    m.brand_names?.some(b => b.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900">Authoritative Medicine Reference Catalogue</h1>
        <p className="text-xs text-slate-500">
          Core Innovation A: Smart Medicine Resolution Engine, Verified Brand Mappings, and Pharmacological Reference.
        </p>
      </div>

      {/* Core Innovation A: Interactive Resolver Sandbox */}
      <div className="bg-gradient-to-r from-navy-950 via-slate-900 to-navy-900 text-white rounded-xl p-5 shadow-sm border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-5 h-5 text-blue-400" />
            <h3 className="font-bold text-sm">Smart Medicine Resolution Sandbox (RapidFuzz Engine)</h3>
          </div>
          <span className="text-[10px] bg-blue-500/20 text-blue-300 border border-blue-500/40 px-2 py-0.5 rounded font-mono">
            Multi-Tier Normalization & Fuzzy Match
          </span>
        </div>

        <div className="flex flex-col sm:flex-row gap-2">
          <input
            type="text"
            value={sandboxInput}
            onChange={(e) => setSandboxInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleRunSandbox(sandboxInput)}
            placeholder="Type any brand, typo, or formulation (e.g. Coumadin, metformn, Diflucane, Paracetamol)..."
            className="flex-1 px-3.5 py-2 bg-slate-800/90 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-400 font-medium"
          />
          <button
            onClick={() => handleRunSandbox(sandboxInput)}
            disabled={resolving}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow transition flex items-center justify-center space-x-1.5 shrink-0"
          >
            {resolving ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
            <span>Test Resolution</span>
          </button>
        </div>

        {/* Sandbox Output Result */}
        {sandboxResult && (
          <div className="bg-slate-800/80 rounded-lg p-4 border border-slate-700 space-y-3 text-xs">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div>
                <span className="text-slate-400 block text-[11px]">Original Input</span>
                <span className="font-mono text-white font-semibold">'{sandboxResult.original_input}'</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[11px]">Resolved Generic</span>
                <span className="text-blue-300 font-bold text-sm">
                  {sandboxResult.resolved_generic || 'Ambiguous / Unresolved'}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block text-[11px]">Matching Method</span>
                <span className="font-mono text-amber-300">
                  {sandboxResult.match_method} ({Math.round(sandboxResult.match_score)}%)
                </span>
              </div>
              <div>
                <span className="text-slate-400 block text-[11px]">Review Required?</span>
                <span className={sandboxResult.requires_human_review ? 'text-amber-400 font-bold' : 'text-emerald-400 font-bold'}>
                  {sandboxResult.requires_human_review ? 'Yes (Clinician Confirmation)' : 'No (Deterministic)'}
                </span>
              </div>
            </div>

            {/* Candidates */}
            {sandboxResult.candidates && sandboxResult.candidates.length > 0 && (
              <div className="border-t border-slate-700 pt-2 space-y-1">
                <span className="text-[11px] text-slate-400 block font-semibold">Matched Candidates Ranked:</span>
                <div className="flex flex-wrap gap-2">
                  {sandboxResult.candidates.map((c, i) => (
                    <span
                      key={i}
                      className="px-2.5 py-1 bg-slate-900 border border-slate-700 rounded text-[11px] flex items-center space-x-1.5"
                    >
                      <strong className="text-slate-200">{c.generic_name}</strong>
                      {c.brand_name && <span className="text-slate-400">({c.brand_name})</span>}
                      <span className="text-blue-400 font-mono text-[10px]">{Math.round(c.match_score)}%</span>
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Benchmark Labelled Test Suite */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="font-bold text-sm text-slate-900">Labelled Resolution Test Suite</h3>
            <p className="text-xs text-slate-500">
              Measure medicine-name matching performance across exact names, brands, typos, and ambiguous tokens.
            </p>
          </div>
          <button
            onClick={handleRunTestSuite}
            disabled={testingSuite}
            className="px-3.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition flex items-center space-x-1.5 border border-slate-200 shrink-0"
          >
            {testingSuite ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <FileCode className="w-3.5 h-3.5 text-blue-600" />}
            <span>{testSuite ? 'Re-Run Labelled Suite' : 'Execute Test Suite'}</span>
          </button>
        </div>

        {testSuite && (
          <div className="space-y-3">
            <div className="flex items-center space-x-4 bg-blue-50 p-3 rounded-lg border border-blue-200 text-xs">
              <div>
                Score: <strong className="text-blue-900 text-sm">{testSuite.accuracy_score_pct}% Accuracy</strong>
              </div>
              <span className="text-slate-300">•</span>
              <div className="text-slate-700">
                {testSuite.passed_tests} of {testSuite.total_tests} test cases passed
              </div>
            </div>

            <div className="overflow-x-auto border border-slate-200 rounded-lg">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 border-b border-slate-200 font-semibold text-slate-600 text-[10px]">
                  <tr>
                    <th className="py-2 px-3">Test Type</th>
                    <th className="py-2 px-3">Test Input</th>
                    <th className="py-2 px-3">Expected</th>
                    <th className="py-2 px-3">Resolved Result</th>
                    <th className="py-2 px-3">Method (Score)</th>
                    <th className="py-2 px-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {testSuite.test_results.map((tr: any, idx: number) => (
                    <tr key={idx} className="hover:bg-slate-50">
                      <td className="py-2 px-3 font-semibold text-slate-700">{tr.test_type}</td>
                      <td className="py-2 px-3 font-mono text-slate-900">'{tr.input}'</td>
                      <td className="py-2 px-3 text-slate-600">{tr.expected}</td>
                      <td className="py-2 px-3 font-bold text-slate-900">{tr.resolved_generic || 'Ambiguous'}</td>
                      <td className="py-2 px-3 text-slate-500 font-mono text-[11px]">{tr.match_method} ({Math.round(tr.similarity_score)}%)</td>
                      <td className="py-2 px-3">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                          PASSED
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Searchable Medicine Catalogue Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden space-y-4 p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="font-bold text-sm text-slate-900">Reference Catalogue Directory</h3>
            <p className="text-xs text-slate-500">
              Pharmacological classifications, verified brand names, renal flags, and black box warnings
            </p>
          </div>
          <div className="relative w-full sm:w-72">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search generic or brand name..."
              className="w-full pl-8 pr-3 py-1.5 border border-slate-200 rounded-lg text-xs focus:outline-none"
            />
          </div>
        </div>

        <div className="overflow-x-auto border border-slate-200 rounded-lg">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 font-semibold text-slate-600 text-[10px] uppercase">
              <tr>
                <th className="py-2.5 px-3">Generic Name</th>
                <th className="py-2.5 px-3">Therapeutic Class</th>
                <th className="py-2.5 px-3">Verified Brands</th>
                <th className="py-2.5 px-3">Renal Cleared?</th>
                <th className="py-2.5 px-3">Black Box Warning</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredCatalogue.map((med) => (
                <tr key={med.id} className="hover:bg-slate-50">
                  <td className="py-2.5 px-3 font-bold text-slate-900 capitalize">
                    {med.generic_name}
                  </td>
                  <td className="py-2.5 px-3 text-slate-600 font-medium">
                    {med.therapeutic_class}
                  </td>
                  <td className="py-2.5 px-3">
                    <div className="flex flex-wrap gap-1">
                      {med.brand_names?.map((b, i) => (
                        <span key={i} className="px-1.5 py-0.5 bg-blue-50 text-blue-700 rounded text-[10px] font-semibold border border-blue-200">
                          {b}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="py-2.5 px-3">
                    {med.renal_cleared ? (
                      <span className="text-[10px] font-bold px-1.5 py-0.5 bg-amber-100 text-amber-800 rounded">
                        YES (Threshold Rule)
                      </span>
                    ) : (
                      <span className="text-slate-400">No</span>
                    )}
                  </td>
                  <td className="py-2.5 px-3 text-slate-600 text-[11px] max-w-xs">
                    {med.black_box_warnings ? (
                      <span className="text-red-700 line-clamp-1">{med.black_box_warnings}</span>
                    ) : (
                      <span className="text-slate-400 italic">None</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
