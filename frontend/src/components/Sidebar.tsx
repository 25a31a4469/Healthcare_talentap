import React from 'react';
import {
  LayoutDashboard,
  Users,
  ShieldAlert,
  BellRing,
  BookOpen,
  LineChart,
  History,
  Settings,
  ChevronRight
} from 'lucide-react';

export type NavItem =
  | 'dashboard'
  | 'patients'
  | 'checker'
  | 'alerts'
  | 'reference'
  | 'evaluation'
  | 'audit'
  | 'settings';

interface Props {
  activeTab: NavItem;
  setActiveTab: (tab: NavItem) => void;
  unresolvedAlertsCount?: number;
  patientCount?: number;
}

export const Sidebar: React.FC<Props> = ({
  activeTab,
  setActiveTab,
  unresolvedAlertsCount = 0,
  patientCount = 0
}) => {
  const navItems = [
    {
      id: 'dashboard' as NavItem,
      label: 'Overview Dashboard',
      icon: LayoutDashboard,
      badge: null
    },
    {
      id: 'patients' as NavItem,
      label: 'Patient Records',
      icon: Users,
      badge: patientCount > 0 ? `${patientCount}` : null
    },
    {
      id: 'checker' as NavItem,
      label: 'Safety Checker',
      icon: ShieldAlert,
      badge: 'Run Check'
    },
    {
      id: 'alerts' as NavItem,
      label: 'Medication Alerts',
      icon: BellRing,
      badge: unresolvedAlertsCount > 0 ? `${unresolvedAlertsCount} pending` : null,
      badgeColor: unresolvedAlertsCount > 0 ? 'bg-amber-100 text-amber-800 border-amber-200' : undefined
    },
    {
      id: 'reference' as NavItem,
      label: 'Medicine Reference',
      icon: BookOpen,
      badge: null
    },
    {
      id: 'evaluation' as NavItem,
      label: 'Evaluation & Metrics',
      icon: LineChart,
      badge: 'Hackathon'
    },
    {
      id: 'audit' as NavItem,
      label: 'Audit History',
      icon: History,
      badge: null
    },
    {
      id: 'settings' as NavItem,
      label: 'Settings & About',
      icon: Settings,
      badge: null
    }
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 min-h-[calc(100vh-5rem)] flex flex-col justify-between p-4 shrink-0">
      <div className="space-y-1.5">
        <div className="px-3 py-2 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
          Decision Support System
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${isActive
                  ? 'bg-navy-900 text-white shadow-sm shadow-blue-950/20'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                }`}
            >
              <div className="flex items-center space-x-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-slate-400'}`} />
                <span className="truncate">{item.label}</span>
              </div>
              {item.badge && (
                <span
                  className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${isActive
                      ? 'bg-blue-800 text-blue-100 border-blue-700'
                      : item.badgeColor || 'bg-slate-100 text-slate-600 border-slate-200'
                    }`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      <div className="pt-4 border-t border-slate-200 space-y-3">
        <div className="p-3 bg-blue-50/60 rounded-lg border border-blue-100 text-xs text-blue-900">
          <p className="font-semibold mb-0.5">Clinical Protocol v1.4</p>
          <p className="text-[11px] text-blue-700 leading-relaxed">
            Deterministic rule validation active. Prioritised risk scoring enabled.
          </p>
        </div>
        <div className="text-[11px] text-slate-400 px-1">
          H4 System • Build 1.0.0
        </div>
      </div>
    </aside>
  );
};

