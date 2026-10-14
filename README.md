# H4 — The Medication Safety Second Pair of Eyes

> **Tagline:** *"Catch the right risks. Reduce unnecessary alerts. Explain every warning."*

[![Backend Tests](https://img.shields.io/badge/pytest-18%20passed-brightgreen.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)]()
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg)]()
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue.svg)]()
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC.svg)]()
[![License](https://img.shields.io/badge/License-MIT%20Prototype-lightgrey.svg)]()

---

## ⚠️ Important Clinical Disclaimer

> **CLINICAL DECISION-SUPPORT DEMONSTRATION PROTOTYPE ONLY**
> 
> **H4 — The Medication Safety Second Pair of Eyes** is an assistive software prototype developed strictly for decision-support research, demonstration, and hackathon evaluation.
> 
> - **Never independently prescribes, modifies, or discontinues medication.**
> - **Must never be used as a standalone or primary diagnostic or prescribing tool.**
> - **Not approved or cleared by the FDA, EMA, or any healthcare regulatory body for clinical deployment.**
> - All patients, identifiers, and scenarios demonstrated within this prototype are **synthetic or de-identified test records**.

---

## 1. System Architecture

The application is structured into a clean decoupled architecture: a high-performance **FastAPI (Python 3.12)** backend serving a rule-based deterministic clinical engine, and a modern **React 18 + TypeScript + Vite + Tailwind CSS** clinical decision cockpit.

```mermaid
flowchart TD
    subgraph Client["Clinical Decision Cockpit (React 18 + TypeScript)"]
        UI_Dash["1. Overview Dashboard"]
        UI_Patients["2. Patient Management & CSV/JSON Import"]
        UI_Checker["3. Interactive Safety Checker"]
        UI_Alerts["4. Triage & Alert Acknowledgement"]
        UI_Ref["5. Medicine & Rule Reference Catalogue"]
        UI_Eval["6. Evaluation & Benchmark Suite"]
        UI_Audit["7. Immutable Audit Trail"]
        UI_Settings["8. System Settings & Compliance"]
    end

    subgraph API["FastAPI REST Services (/api)"]
        Router["API Router & Middleware"]
        Pydantic["Pydantic v2 Schema Validation"]
    end

    subgraph CoreEngine["Clinical Decision-Support Core Engine"]
        Resolver["Core Innovation A:<br/>Multi-Tier Medicine Resolver<br/>(Exact, Brand, RapidFuzz Typo, Ambiguity Flag)"]
        Pipeline["10-Step Deterministic Rules Engine"]
        Prioritiser["Core Innovation B:<br/>Risk-First Prioritisation & Deduplication Engine"]
        Explainer["Core Innovation C:<br/>7-Point Grounded Evidence Generator"]
        Evaluator["Benchmark Evaluator<br/>(Recall, Precision, Near-Miss, Alert Fatigue)"]
    end

    subgraph DataStore["Persistence Layer (SQLAlchemy 2.0)"]
        DB[("SQLite / PostgreSQL Compatible DB")]
        Catalogue[("Medicine Catalogue & Verified Brand Mappings")]
        RulesStore[("CPIC / FDA Interactions, KDIGO Renal, Contraindications")]
        PatientStore[("Synthetic Patient Cohort & Medication Lists")]
        AlertStore[("Safety Alerts, Acknowledgements & Audit Logs")]
    end

    Client <-->|"REST / JSON (Axios Client) API"| API
    API --> CoreEngine
    CoreEngine --> DataStore
```

---

## 2. The 10-Step Medication Safety Pipeline

```mermaid
flowchart TD
    S1["Step 1: Input Validation & Sanitization"] --> S2["Step 2: String Normalization (Lower, Punctuation, Whitespace)"]
    S2 --> S3["Step 3: Exact Generic & Verified Brand Resolution"]
    S3 --> S4["Step 4: RapidFuzz Typo Matching & Ambiguity Detection"]
    S4 --> S5["Step 5: Duplicate Active-Ingredient & Class Redundancy Check"]
    S5 --> S6["Step 6: Drug–Drug Interaction (DDI) Pair Evaluation"]
    S6 --> S7["Step 7: Kidney-Function Risk Check (eGFR / CrCl Thresholds)"]
    S7 --> S8["Step 8: Recorded Contraindication & Allergy Check"]
    S8 --> S9["Step 9: Alert Deduplication & Risk-First Prioritisation"]
    S9 --> S10["Step 10: 7-Point Evidence-Backed Explanation Synthesis"]
```

---

## 3. Core Innovations

### 🌟 Core Innovation A: Smart Multi-Tier Medicine Resolver
Clinical entry often includes brand names (e.g., *Glucophage*), synonyms, or typos (e.g., *Metfornin*). 
- **Tier 1 (Exact Generic):** Deterministic case-insensitive matching against curated INN generic names.
- **Tier 2 (Verified Brand):** Resolves verified brand names to their authoritative active pharmaceutical ingredient(s).
- **Tier 3 (RapidFuzz Typo Matching):** Uses normalized token-sort Levenshtein scoring. Scores $\ge 82\%$ surface candidate generic matches.
- **Ambiguity Guardrail:** If multiple generic candidates have similar proximity scores, the system **never guesses silently**; it flags `requires_confirmation = true` and surfaces selectable options to the clinician.
- **Confidence Decoupling:** Medicine-name resolution confidence is strictly reported separately from clinical risk severity.

### 🛡️ Core Innovation B: Risk-First Alert Prioritisation & Deduplication
To combat life-threatening **alert fatigue**:
- **Severity-First Ordering:** Alerts are ranked strictly by reference-defined risk (`HIGH` $\to$ `MEDIUM` $\to$ `LOW`).
- **Semantic Deduplication:** Multiple alerts pointing to the same underlying clinical pair or mechanism are consolidated into a single actionable card with grouped references.
- **Insufficient Information Flags:** Missing renal lab values or clinical context produce explicit `Missing Information` warnings rather than silently suppressing risks or assuming zero risk.

### 📋 Core Innovation C: 7-Point Grounded Evidence Explanations
Every generated alert includes a structured, fully explainable 7-point clinical dossier:
1. **Detected Issue:** Precise clinical classification (e.g., *Major Drug-Drug Interaction: Anticoagulant + Antiplatelet*).
2. **Medicines Involved:** Exact medications and active ingredients implicated.
3. **Clinical Rationale:** Pharmacodynamic or pharmacokinetic mechanism.
4. **Authoritative Reference:** Formal guideline source (e.g., *CPIC Guidelines*, *FDA Package Insert*, *KDIGO 2024*).
5. **Missing Information:** Explicit callout of unrecorded lab values (e.g., *Current INR or baseline bleeding assessment missing*).
6. **Clinician Action:** Objective recommendation (e.g., *Evaluate bleeding risk; consider gastroprotection; review indication*).
7. **Confirmation Status:** Clear badge distinguishing deterministic rule match from fuzzy-matched review.

---

## 4. Pre-Seeded Synthetic Demo Cohort

The database initialises automatically with 7 distinct synthetic test cases designed to demonstrate every challenge requirement:

| Patient ID | Name | Case Profile | Expected Safety Findings |
|---|---|---|---|
| `SYN-001` | Robert Vance (68M) | **Warfarin + Aspirin** | **HIGH Severity DDI:** Synergistic bleeding risk (CPIC / FDA). |
| `SYN-002` | Eleanor Rigby (54F) | **Glucophage + Metformin** | **HIGH Severity Duplicate:** Brand (*Glucophage*) + Generic (*Metformin*) active ingredient redundancy. |
| `SYN-003` | Arthur Dent (62M) | **"Metfornin" (Typo) + Lisinopril** | **Resolver Match:** RapidFuzz resolves typo to *Metformin* with 94.7% confidence; executes safety rules. |
| `SYN-004` | Chloe Decker (39F) | **"Amlo" (Ambiguous Entry)** | **Ambiguity Flag:** Prompts clinician confirmation between *Amlodipine* vs. *Amiloride*. |
| `SYN-005` | Walter White (71M) | **Metformin + eGFR 24 mL/min** | **HIGH Severity Renal Risk:** Contraindicated at eGFR < 30 mL/min/1.73m² (Lactic acidosis risk, KDIGO 2024). |
| `SYN-006` | Sarah Connor (45F) | **Lisinopril + Unrecorded Creatinine** | **Missing Data Warning:** Explicit notification that kidney function lab is unrecorded for ACE-inhibitor. |
| `SYN-007` | Bruce Wayne (38M) | **Atorvastatin + Omeprazole** | **Clean Medication List:** Zero safety contraindications or interactions identified under supported rules. |

---

## 5. Main Navigation Modules

1. **Overview Dashboard:** Live KPI cards (patients, analyses, unresolved alerts, fuzzy matches), alert distribution charts, recent activity log, and dataset status banner.
2. **Patient Records:** Patient directory with search, condition/allergy filters, detailed clinical profile modal, and working **CSV/JSON Import & Export**.
3. **Medication Safety Checker:** Live testing harness allowing clinicians to select existing patients or build ad-hoc medication lists with instant 10-step safety analysis.
4. **Medication Alerts:** Triage queue with multi-dimensional filtering, 7-point evidence dossier viewer, and persistent **clinician acknowledgement & note taking**.
5. **Medicine Reference:** Searchable browser of 40+ drugs, verified brand aliases, DDI interaction rules, and KDIGO renal thresholds.
6. **Evaluation & Testing:** Live validation suite running benchmark datasets; generates **Recall, Precision, Near-Miss Recall, Confusion Matrix, and Alert Fatigue Reduction** comparisons.
7. **Audit History:** Tamper-evident chronological audit log recording every analysis, acknowledgement, and import.
8. **Settings & About:** Reference data provenance, clinical disclaimers, system health diagnostics, and environment toggles.

---

## 6. Installation, Environment & Production Deployment

### Prerequisites
- **Python:** 3.11+ (Python 3.12 recommended)
- **Node.js:** v18+ or v20+ LTS

---

### Environment Configuration & Variables

The project supports both unified root and decoupled service-level environment files:
- **Root Template:** `.env.example` (Unified template for monorepo development)
- **Backend Template:** `backend/.env.example` (FastAPI backend service configuration)
- **Frontend Template:** `frontend/.env.example` (React/Vite client public configuration)

> [!IMPORTANT]
> Never commit real secrets, private keys, or credentials to version control. The repository `.gitignore` automatically blocks `.env`, `.env.*`, and credentials files while keeping all `.env.example` templates tracked.

#### Documented Environment Variables

| Variable | Scope | Type | Default Value | Required in Prod | Description |
|---|---|---|---|---|---|
| `ENVIRONMENT` | Backend | String | `development` | Yes (`production`) | Application runtime environment (`development` or `production`) |
| `DEBUG` | Backend | Boolean | `true` | Yes (`false`) | Enables detailed exception tracing and API debug flags |
| `LOG_LEVEL` | Backend | String | `INFO` | No | Server logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `APP_HOST` | Backend | String | `127.0.0.1` | No (`0.0.0.0`) | Host interface for the Uvicorn ASGI server |
| `APP_PORT` | Backend | Integer | `8000` | No | Port number for the FastAPI backend |
| `DATABASE_URL` | Backend | String | `sqlite:///./healthcare.db` | Yes | SQLAlchemy database URI (SQLite or PostgreSQL) |
| `CORS_ORIGINS` | Backend | String/List | `http://localhost:5173,...` | Yes | Comma-separated or JSON list of authorized frontend origins |
| `ALLOWED_ORIGINS` | Backend | String/List | `None` | Optional | Optional alias for additional CORS allowed origins |
| `DEMO_MODE` | Backend | Boolean | `true` | No | Enables pre-seeded synthetic test cohort and near-miss benchmarks |
| `SYNTHETIC_DATA_BANNER` | Backend | Boolean | `true` | No | Surfaces synthetic data compliance header across API responses |
| `VITE_API_BASE_URL` | Frontend | String | `""` (empty string) | Yes in decoupled prod | Public backend API URL (leave empty in dev for Vite proxy) |
| `VITE_APP_TITLE` | Frontend | String | `"H4 — The Medication Safety..."` | No | Browser title and header title in the clinical cockpit |

---

### Local Development Setup

#### 1. Backend Setup
```bash
# 1. Clone repository & enter workspace
cd healthcare

# 2. Create and activate virtual environment
python -m venv .venv

# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# 3. Install backend dependencies
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings python-dotenv pandas rapidfuzz pytest httpx python-multipart

# 4. Copy environment template
cp .env.example .env

# 5. Initialize database schema and load verified reference data
python -m backend.app.seed_demo

# 6. Start the backend API server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API is now running at **http://127.0.0.1:8000** with OpenAPI Swagger documentation at **http://127.0.0.1:8000/docs**.

#### 2. Frontend Setup
```bash
# In a new terminal window:
cd healthcare/frontend

# 1. Copy frontend environment template
cp .env.example .env

# 2. Install dependencies
npm install

# 3. Start Vite development server (proxies /api to http://127.0.0.1:8000)
npm run dev -- --host 127.0.0.1 --port 5173
```
Open your browser to **http://127.0.0.1:5173** to access the Clinical Decision Cockpit.

---

### Secure Production Deployment Guide

#### 1. Database Safety & Pre-Deployment Backup
The application uses SQLite (`healthcare.db`) by default with automatic relational foreign-key enforcement (`PRAGMA foreign_keys=ON`).
Before applying updates or deploying to production, always create a safe database backup:

```bash
# Create timestamped database backup
cp healthcare.db healthcare.db.bak_$(date +%Y%m%d_%H%M%S)
```

To migrate to production PostgreSQL:
1. Provision a PostgreSQL instance (e.g., Amazon RDS, Cloud SQL, Supabase).
2. Set `DATABASE_URL=postgresql+psycopg2://user:password@db-host:5432/medication_safety` in `backend/.env`.
3. Run `python -m backend.app.seed_demo` to initialize reference tables and seed initial catalogue records.

#### 2. Backend Production Run
In production, run Uvicorn with multiple workers or behind Gunicorn:
```bash
# In backend directory with production .env configured:
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 4 --no-access-log
```

Ensure `CORS_ORIGINS` in your production `.env` is set to your exact HTTPS frontend domain (e.g., `https://cockpit.medicationsafety.example.com`).

#### 3. Frontend Production Build
Compile the optimized static bundle:
```bash
cd healthcare/frontend

# Set production API URL in frontend/.env:
# VITE_API_BASE_URL=https://api.medicationsafety.example.com

npm run build
```
The production bundle will be generated in `frontend/dist/`. Serve these static files via Nginx, AWS S3 + CloudFront, Cloudflare Pages, or Vercel.

#### 4. Example Production Nginx Reverse Proxy
```nginx
server {
    listen 443 ssl http2;
    server_name medicationsafety.example.com;

    # SSL Certificates
    ssl_certificate /etc/letsencrypt/live/medicationsafety.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/medicationsafety.example.com/privkey.pem;

    # Security Headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Frontend Static Cockpit
    location / {
        root /var/www/healthcare/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API Proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Swagger Documentation
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
    }
}
```

---

## 7. Automated Test Suite

Run the comprehensive pytest suite covering the resolver, rules engine, alert prioritiser, evaluation benchmark, and REST endpoints:

```bash
# In the project root with .venv activated:
pytest backend/tests/ -v
```

### Verified Test Results (22 Passed)
```text
============================= test session starts =============================
platform win32 -- Python 3.12.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\user\OneDrive\healthcare
plugins: anyio-4.15.1
collected 22 items

backend/tests/test_api.py::test_health_endpoint PASSED                   [  4%]
backend/tests/test_api.py::test_dataset_status_endpoint PASSED           [  9%]
backend/tests/test_api.py::test_dashboard_summary_endpoint PASSED        [ 13%]
backend/tests/test_api.py::test_patients_crud PASSED                     [ 18%]
backend/tests/test_api.py::test_safety_checker_analysis PASSED           [ 22%]
backend/tests/test_api.py::test_alert_acknowledgement PASSED             [ 27%]
backend/tests/test_evaluation.py::test_safe_division_edge_cases PASSED   [ 31%]
backend/tests/test_evaluation.py::test_seeded_near_miss_300_benchmark PASSED [ 36%]
backend/tests/test_evaluation.py::test_synthetic_cohort_500_benchmark PASSED [ 40%]
backend/tests/test_evaluation.py::test_alert_fatigue_reduction_measured PASSED [ 45%]
backend/tests/test_prioritiser.py::test_prioritisation_ordering PASSED   [ 50%]
backend/tests/test_prioritiser.py::test_alert_deduplication PASSED       [ 54%]
backend/tests/test_resolver.py::test_exact_generic_resolution PASSED     [ 59%]
backend/tests/test_resolver.py::test_exact_brand_resolution PASSED       [ 63%]
backend/tests/test_resolver.py::test_fuzzy_misspelling_resolution PASSED [ 68%]
backend/tests/test_resolver.py::test_brand_with_dosage_resolution PASSED [ 72%]
backend/tests/test_resolver.py::test_uncatalogued_medicine_handling PASSED [ 77%]
backend/tests/test_rules_engine.py::test_drug_drug_interaction_detection PASSED [ 81%]
backend/tests/test_rules_engine.py::test_duplicate_active_ingredient_detection PASSED [ 86%]
backend/tests/test_rules_engine.py::test_renal_risk_threshold_contraindication PASSED [ 90%]
backend/tests/test_rules_engine.py::test_missing_renal_data_limitation_warning PASSED [ 95%]
backend/tests/test_rules_engine.py::test_contraindication_condition_peptic_ulcer PASSED [100%]

======================= 22 passed, 11 warnings in 3.32s =======================
```

---

## 8. REST API Documentation

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check & service status |
| `GET` | `/api/dashboard/summary` | Real-time dashboard KPI summary |
| `GET` | `/api/patients` | List patients with search & condition filters |
| `POST` | `/api/patients` | Create a new patient record |
| `POST` | `/api/patients/import/csv` | Batch import synthetic patient CSV |
| `GET` | `/api/patients/export/csv` | Export safe de-identified CSV |
| `POST` | `/api/resolver/resolve` | Smart medicine resolution sandbox |
| `POST` | `/api/checker/analyze` | Execute 10-step medication safety analysis |
| `GET` | `/api/alerts` | List all safety alerts with severity filters |
| `POST` | `/api/alerts/{id}/acknowledge` | Clinician acknowledgement with notes |
| `GET` | `/api/reference/medicines` | Query authoritative medicine catalogue |
| `POST` | `/api/evaluation/run` | Execute benchmark evaluation suite |
| `GET` | `/api/audit/logs` | Query immutable audit events |

---

## 9. Security, Privacy & Compliance

- **Synthetic Identifiers Only:** All test patients utilize synthetic identifiers (`SYN-XXX`) to completely prevent Protected Health Information (PHI) exposure.
- **CSV Formula Injection Shielding:** Patient CSV exports strictly sanitize cell prefixes (`=`, `+`, `-`, `@`) to block spreadsheet formula injection attacks.
- **No Hardcoded Credentials:** Zero secrets in frontend; configurable via `.env.example`.
- **Foreign Key Integrity:** Database migrations enforce relational foreign key cascading and schema constraints.
- **Offline Reliability:** Operates with 100% offline autonomy using embedded deterministic reference tables—no external API dependencies required.

---

## 10. License

Developed for the **H4 Healthcare Clinical Decision-Support Hackathon**. Distributed under the MIT Prototype License. Not approved for clinical use.
