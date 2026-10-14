import React from 'react';
import { AlertCircle, ShieldAlert, CheckCircle2 } from 'lucide-react';

interface Props {
  isBackendHealthy: boolean;
  referenceVersion?: string;
}

export const DisclaimerBanner: React.FC<Props> = ({ isBackendHealthy, referenceVersion = 'v1.4' }) => {
  return (
    <div className="bg-slate-900 text-slate-100 border-b border-slate-800 px-4 py-2 text-xs">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
        <div className="flex items-center space-x-2">
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-blue-900/60 text-blue-200 border border-blue-700">
            DEMO MODE
          </span>
          <span className="text-slate-300">
            Illustrative Synthetic Demo Cohort & Validated Reference Rules ({referenceVersion})
          </span>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1.5 text-slate-400">
            <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
            <span>Clinical Decision Support Only • Never Autonomously Prescribes</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className={`w-2 h-2 rounded-full ${isBackendHealthy ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
            <span className="text-slate-300">
              {isBackendHealthy ? 'API Connected' : 'API Offline'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
