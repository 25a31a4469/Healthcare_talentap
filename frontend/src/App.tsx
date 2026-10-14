import React, { useState, useEffect } from 'react';
import { DisclaimerBanner } from './components/DisclaimerBanner';
import { Navbar } from './components/Navbar';
import { Sidebar, NavItem } from './components/Sidebar';
import { AlertDetailModal } from './components/AlertDetailModal';

// Pages
import { DashboardPage } from './pages/DashboardPage';
import { PatientsPage } from './pages/PatientsPage';
import { SafetyCheckerPage } from './pages/SafetyCheckerPage';
import { AlertsPage } from './pages/AlertsPage';
import { MedicineReferencePage } from './pages/MedicineReferencePage';
import { EvaluationPage } from './pages/EvaluationPage';
import { AuditHistoryPage } from './pages/AuditHistoryPage';
import { SettingsAboutPage } from './pages/SettingsAboutPage';

import { api } from './api/client';
import { SafetyAlert, Patient } from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<NavItem>('dashboard');
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean>(false);
  const [referenceVersion, setReferenceVersion] = useState<string>('v1.4');
  const [unresolvedAlertsCount, setUnresolvedAlertsCount] = useState<number>(0);
  const [patientCount, setPatientCount] = useState<number>(0);

  // Modals & Cross-page state
  const [selectedAlert, setSelectedAlert] = useState<SafetyAlert | null>(null);
  const [patientToCheck, setPatientToCheck] = useState<Patient | null>(null);

  const checkHealth = async () => {
    try {
      const health = await api.getHealth();
      setIsBackendHealthy(health.status === 'healthy');
      setPatientCount(health.patient_records || 0);

      const ds = await api.getDatasetStatus();
      if (ds && ds.version) {
        setReferenceVersion(ds.version);
      }

      const summary = await api.getDashboardSummary();
      if (summary) {
        setUnresolvedAlertsCount(summary.unresolved_alerts_count || 0);
      }
    } catch (err) {
      setIsBackendHealthy(false);
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleCheckPatient = (pt: Patient) => {
    setPatientToCheck(pt);
    setActiveTab('checker');
  };

  const handleAlertAcknowledged = () => {
    checkHealth();
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900 selection:bg-blue-100 selection:text-blue-900">
      {/* 1. Persistent Clinical Disclaimer Banner */}
      <DisclaimerBanner
        isBackendHealthy={isBackendHealthy}
        referenceVersion={referenceVersion}
      />

      {/* 2. Top Header / Navbar */}
      <Navbar
        isBackendHealthy={isBackendHealthy}
        activeReferenceVersion={referenceVersion}
      />

      {/* 3. Main Application Body */}
      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        {/* Navigation Sidebar */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={(tab) => {
            if (tab !== 'checker') setPatientToCheck(null);
            setActiveTab(tab);
          }}
          unresolvedAlertsCount={unresolvedAlertsCount}
          patientCount={patientCount}
        />

        {/* Page Content View */}
        <main className="flex-1 p-6 overflow-y-auto">
          {activeTab === 'dashboard' && (
            <DashboardPage
              onNavigate={setActiveTab}
              onSelectAlert={setSelectedAlert}
            />
          )}

          {activeTab === 'patients' && (
            <PatientsPage
              onCheckPatient={handleCheckPatient}
            />
          )}

          {activeTab === 'checker' && (
            <SafetyCheckerPage
              initialPatient={patientToCheck}
              onSelectAlert={setSelectedAlert}
            />
          )}

          {activeTab === 'alerts' && (
            <AlertsPage
              onSelectAlert={setSelectedAlert}
            />
          )}

          {activeTab === 'reference' && (
            <MedicineReferencePage />
          )}

          {activeTab === 'evaluation' && (
            <EvaluationPage />
          )}

          {activeTab === 'audit' && (
            <AuditHistoryPage />
          )}

          {activeTab === 'settings' && (
            <SettingsAboutPage />
          )}
        </main>
      </div>

      {/* 4. Global 7-Point Evidence Modal */}
      {selectedAlert && (
        <AlertDetailModal
          alert={selectedAlert}
          onClose={() => setSelectedAlert(null)}
          onAcknowledged={handleAlertAcknowledged}
        />
      )}
    </div>
  );
};

export default App;
