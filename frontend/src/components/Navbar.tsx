import React from 'react';
import { Eye, ShieldCheck, Activity, Database, AlertTriangle } from 'lucide-react';

interface Props {
  isBackendHealthy: boolean;
  activeReferenceVersion: string;
}

export const Navbar: React.FC<Props> = ({ isBackendHealthy, activeReferenceVersion }) => {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-navy-900 flex items-center justify-center text-white shadow-md shadow-blue-900/20">
              <Eye className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg text-navy-950 tracking-tight">H4</span>
                <span className="text-slate-400 font-light">|</span>
                <span className="font-semibold text-slate-800 text-sm sm:text-base">
                  The Medication Safety Second Pair of Eyes
                </span>
              </div>
              <p className="text-[11px] text-slate-500 hidden sm:block">
                Catch the right risks. Reduce unnecessary alerts. Explain every warning.
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="hidden md:flex items-center px-2.5 py-1 rounded-md bg-slate-100 border border-slate-200 text-xs text-slate-600">
              <Database className="w-3.5 h-3.5 mr-1.5 text-blue-600" />
              <span>Rules: <strong className="text-slate-800 font-semibold">{activeReferenceVersion}</strong></span>
            </div>

            <div className={`flex items-center px-2.5 py-1 rounded-md text-xs font-medium border ${
              isBackendHealthy
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                : 'bg-rose-50 text-rose-700 border-rose-200'
            }`}>
              <Activity className="w-3.5 h-3.5 mr-1.5" />
              <span>{isBackendHealthy ? 'Backend Active' : 'Offline'}</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
