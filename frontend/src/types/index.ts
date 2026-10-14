export interface Patient {
  id: string;
  age: number;
  gender: string;
  conditions: string[];
  allergies: string[];
  egfr?: number | null;
  egfr_unit: string;
  creatinine_clearance?: number | null;
  crcl_unit: string;
  serum_creatinine?: number | null;
  scr_unit: string;
  is_pregnant?: boolean | null;
  data_source: string;
  notes?: string | null;
  medications: PatientMedication[];
  created_at: string;
  updated_at: string;
}

export interface PatientMedication {
  id: number;
  raw_name: string;
  resolved_generic_name: string;
  brand_name?: string | null;
  dose?: string | null;
  frequency?: string | null;
  route?: string;
  resolution_method: string;
  confidence_score: number;
  is_confirmed: boolean;
}

export interface MedicineInput {
  name: string;
  brand_name?: string;
  dose?: string;
  frequency?: string;
  route?: string;
}

export interface ResolvedCandidate {
  generic_name: string;
  brand_name?: string | null;
  active_ingredients: string[];
  therapeutic_class: string;
  match_score: number;
  match_method: string;
  is_ambiguous: boolean;
  standard_dosing?: string | null;
}

export interface MedicineResolutionResult {
  original_input: string;
  resolved_generic?: string | null;
  brand_name?: string | null;
  active_ingredients: string[];
  therapeutic_class?: string | null;
  match_score: number;
  match_method: string;
  is_ambiguous: boolean;
  candidates: ResolvedCandidate[];
  requires_human_review: boolean;
  confidence_level: 'HIGH' | 'MEDIUM' | 'LOW' | 'UNRESOLVED';
}

export interface SafetyAlert {
  id: string;
  analysis_id: string;
  patient_id?: string | null;
  category: string;
  severity: 'HIGH' | 'MEDIUM' | 'LOW' | 'INFORMATIONAL';
  priority_rank: number;
  drugs_involved: string[];
  rule_id?: string | null;
  evidence_source: string;
  title: string;
  what_detected: string;
  why_flagged: string;
  clinical_recommendation: string;
  missing_patient_info: string[];
  limitations_disclaimer?: string | null;
  is_deterministic: boolean;
  requires_manual_review: boolean;
  name_matching_confidence: number;
  matching_method: string;
  is_acknowledged: boolean;
  acknowledged_by?: string | null;
  acknowledged_at?: string | null;
  review_notes?: string | null;
  status: 'UNRESOLVED' | 'REVIEWED_ACCEPTED' | 'REVIEWED_OVERRIDDEN';
  created_at: string;
  evidence_summary?: {
    what_detected: string;
    medicines_involved: string[];
    why_flagged: string;
    exact_rule_or_reference: string;
    missing_patient_information: string[];
    clinician_action_items: string;
    verification_status: string;
    plain_language_summary: string;
  };
}

export interface MedicationAnalysis {
  id: string;
  patient_id?: string | null;
  analysis_mode: string;
  input_medications: any[];
  resolved_medications: MedicineResolutionResult[];
  total_alerts_raw: number;
  total_alerts_prioritised: number;
  high_priority_count: number;
  medium_priority_count: number;
  low_priority_count: number;
  missing_data_warnings_count: number;
  alerts: SafetyAlert[];
  created_at: string;
}

export interface DashboardSummary {
  patient_count: number;
  reviews_count: number;
  high_priority_alerts: number;
  medium_priority_alerts: number;
  unresolved_alerts_count: number;
  manual_review_needed_count: number;
  alert_distribution: Record<string, number>;
  severity_distribution: Record<string, number>;
  recent_analyses: {
    id: string;
    patient_id?: string;
    analysis_mode: string;
    total_alerts: number;
    high_priority_count: number;
    created_at: string;
  }[];
  recent_alerts: SafetyAlert[];
  dataset_status: {
    is_official: boolean;
    name: string;
    version: string;
    source_label: string;
  };
  active_reference_version: string;
  alert_volume_reduction_pct?: number;
  baseline_raw_alerts_total?: number;
  prioritised_alerts_total?: number;
}

export interface MedicineCatalogueItem {
  id: number;
  generic_name: string;
  therapeutic_class: string;
  active_ingredients: string[];
  brand_names: string[];
  synonyms: string[];
  standard_dosing?: string | null;
  renal_cleared: boolean;
  black_box_warnings?: string | null;
}

export interface AuditLog {
  id: number;
  timestamp: string;
  action: string;
  user_id: string;
  resource_type: string;
  resource_id?: string | null;
  details: Record<string, any>;
}

export interface EvaluationRunResult {
  evaluation_id: string;
  cohort_type?: string;
  dataset_name: string;
  total_records: number;
  total_near_miss_seeded: number;
  serious_issue_recall: number;
  precision: number;
  specificity?: number | null;
  f1_score?: number | null;
  false_positive_rate?: number | null;
  false_positive_count: number;
  false_negative_count: number;
  name_matching_accuracy: number;
  near_miss_recall: number;
  alerts_per_patient_raw: number;
  alerts_per_patient_prioritised: number;
  alert_fatigue_reduction_pct: number;
  confusion_matrix: {
    true_positives: number;
    false_positives: number;
    false_negatives: number;
    true_negatives: number;
    total?: number;
    cohort_type?: string;
    precision?: number;
    recall?: number;
    specificity?: number | null;
    f1_score?: number | null;
    false_positive_rate?: number;
    low_severity_raw?: number;
    low_severity_prioritised?: number;
    serious_retained_pct?: number;
  };
  breakdown_by_category: Record<string, number>;
  breakdown_by_severity: Record<string, number>;
  created_at: string;
}
