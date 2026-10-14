import {
  Patient, PatientMedication, MedicineInput, MedicineResolutionResult,
  SafetyAlert, MedicationAnalysis, DashboardSummary, MedicineCatalogueItem,
  AuditLog, EvaluationRunResult
} from '../types';

export const BASE_URL: string = (
  import.meta.env.VITE_API_BASE_URL !== undefined
    ? import.meta.env.VITE_API_BASE_URL
    : import.meta.env.VITE_API_URL !== undefined
      ? import.meta.env.VITE_API_URL
      : ''
).replace(/\/+$/, '');

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  try {
    const res = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {})
      },
      ...options
    });

    if (!res.ok) {
      let errorMsg = `HTTP Error ${res.status}`;
      try {
        const errJson = await res.json();
        errorMsg = errJson.detail || errJson.message || errorMsg;
      } catch (_) {}
      throw new Error(errorMsg);
    }
    return await res.json();
  } catch (err: any) {
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      throw new Error(`Cannot reach backend at ${BASE_URL}. Ensure FastAPI backend server is running.`);
    }
    throw err;
  }
}

export const api = {
  // Health & Status
  getHealth: () => request<{ status: string; patient_records: number; reference_rules: number }>('/api/health'),
  getDatasetStatus: () => request<any>('/api/dataset-status'),

  // Dashboard
  getDashboardSummary: () => request<DashboardSummary>('/api/dashboard/summary'),

  // Patients
  getPatients: (params?: { query?: string; condition?: string; gender?: string }) => {
    const queryParts: string[] = [];
    if (params?.query) queryParts.push(`query=${encodeURIComponent(params.query)}`);
    if (params?.condition) queryParts.push(`condition=${encodeURIComponent(params.condition)}`);
    if (params?.gender) queryParts.push(`gender=${encodeURIComponent(params.gender)}`);
    const qStr = queryParts.length ? `?${queryParts.join('&')}` : '';
    return request<Patient[]>(`/api/patients${qStr}`);
  },
  getPatient: (id: string) => request<Patient>(`/api/patients/${id}`),
  createPatient: (data: Partial<Patient> & { initial_medications?: MedicineInput[] }) =>
    request<Patient>('/api/patients', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  updatePatient: (id: string, data: Partial<Patient>) =>
    request<Patient>(`/api/patients/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    }),
  deletePatient: (id: string) =>
    request<{ message: string; id: string }>(`/api/patients/${id}`, {
      method: 'DELETE'
    }),
  importPatients: async (formData: FormData): Promise<{ message: string; imported_records: number }> => {
    const url = `${BASE_URL}/api/patients/import`;
    const res = await fetch(url, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      let errorMsg = `HTTP Error ${res.status}`;
      try {
        const errJson = await res.json();
        errorMsg = errJson.detail || errJson.message || errorMsg;
      } catch (_) {}
      throw new Error(errorMsg);
    }
    return res.json();
  },
  exportPatientsCsvUrl: `${BASE_URL}/api/patients/export/csv`,

  // Medicine Resolution & Catalogue
  resolveMedicine: (name: string) =>
    request<MedicineResolutionResult>(`/api/medicines/resolve?name=${encodeURIComponent(name)}`, {
      method: 'POST'
    }),
  searchMedicines: (q: string) =>
    request<{ query: string; resolved: MedicineResolutionResult; candidates: any[] }>(
      `/api/medicines/search?q=${encodeURIComponent(q)}`
    ),
  getCatalogue: () => request<MedicineCatalogueItem[]>('/api/medicines/catalogue'),
  getBrandMappings: () => request<any[]>('/api/medicines/brand-mappings'),
  getResolutionTestSuite: () => request<any>('/api/medicines/test-suite'),

  // Medication Safety Checker
  runSafetyCheck: (payload: {
    patient_id?: string;
    age?: number;
    gender?: string;
    conditions?: string[];
    allergies?: string[];
    egfr?: number | null;
    egfr_unit?: string;
    creatinine_clearance?: number | null;
    serum_creatinine?: number | null;
    is_pregnant?: boolean | null;
    medications: MedicineInput[];
  }) =>
    request<MedicationAnalysis>('/api/checker/analyze', {
      method: 'POST',
      body: JSON.stringify(payload)
    }),

  // Alerts
  getAlerts: (params?: { severity?: string; category?: string; patient_id?: string; is_acknowledged?: boolean; search?: string }) => {
    const qParts: string[] = [];
    if (params?.severity) qParts.push(`severity=${encodeURIComponent(params.severity)}`);
    if (params?.category) qParts.push(`category=${encodeURIComponent(params.category)}`);
    if (params?.patient_id) qParts.push(`patient_id=${encodeURIComponent(params.patient_id)}`);
    if (params?.is_acknowledged !== undefined) qParts.push(`is_acknowledged=${params.is_acknowledged}`);
    if (params?.search) qParts.push(`search=${encodeURIComponent(params.search)}`);
    const qStr = qParts.length ? `?${qParts.join('&')}` : '';
    return request<SafetyAlert[]>(`/api/alerts${qStr}`);
  },
  getAlertDetail: (id: string) => request<SafetyAlert>(`/api/alerts/${id}`),
  acknowledgeAlert: (id: string, payload: { reviewer_id: string; action: string; review_notes?: string }) =>
    request<any>(`/api/alerts/${id}/acknowledge`, {
      method: 'POST',
      body: JSON.stringify(payload)
    }),

  // Evaluation
  runEvaluation: (cohortType = 'seeded_near_miss_300', cohortSize = 300, nearMissCount = 300) =>
    request<EvaluationRunResult>(
      `/api/evaluation/run?cohort_type=${encodeURIComponent(cohortType)}&cohort_size=${cohortSize}&near_miss_count=${nearMissCount}`,
      { method: 'POST' }
    ),
  getLatestEvaluation: (cohortType?: string) => {
    const q = cohortType ? `?cohort_type=${encodeURIComponent(cohortType)}` : '';
    return request<EvaluationRunResult>(`/api/evaluation/latest${q}`);
  },
  exportEvaluationCsvUrl: `${BASE_URL}/api/evaluation/export-csv`,

  // Audit Logs
  getAuditLogs: (limit = 100) => request<AuditLog[]>(`/api/audit/logs?limit=${limit}`)
};
