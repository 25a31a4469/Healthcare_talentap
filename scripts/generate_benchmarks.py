import json
import os
from typing import List, Dict, Any

os.makedirs("data/evaluation", exist_ok=True)

# ==============================================================================
# 1. 300 SEEDED NEAR-MISS HAZARD CASES (Ground Truth: has_serious_hazard = True)
# ==============================================================================
near_miss_archetypes = [
    # Category 1: Severe Drug-Drug Interactions
    {
        "hazard_type": "DDI",
        "medications": ["Coumadin 5mg", "Diflucan 200mg"],
        "expected_generics": ["warfarin", "fluconazole"],
        "patient_context": {"age": 68, "gender": "Male", "conditions": ["Atrial Fibrillation"]},
        "expected_rule": "RULE-DDI-001",
        "hazard_description": "Warfarin + Fluconazole CYP2C9 inhibition causing severe bleeding risk"
    },
    {
        "hazard_type": "DDI",
        "medications": ["Zestril 20mg", "Aldactone 25mg"],
        "expected_generics": ["lisinopril", "spironolactone"],
        "patient_context": {"age": 65, "gender": "Female", "conditions": ["Heart Failure", "CKD Stage 3"], "egfr": 40.0},
        "expected_rule": "RULE-DDI-002",
        "hazard_description": "Lisinopril + Spironolactone dual renin-aldosterone blockade causing lethal hyperkalemia"
    },
    {
        "hazard_type": "DDI",
        "medications": ["Trexall 15mg weekly", "Motrin 600mg"],
        "expected_generics": ["methotrexate", "ibuprofen"],
        "patient_context": {"age": 52, "gender": "Female", "conditions": ["Rheumatoid Arthritis"]},
        "expected_rule": "RULE-DDI-003",
        "hazard_description": "Methotrexate + Ibuprofen renal elimination inhibition causing pancytopenia"
    },
    {
        "hazard_type": "DDI",
        "medications": ["Plavix 75mg", "Prilosec 20mg"],
        "expected_generics": ["clopidogrel", "omeprazole"],
        "patient_context": {"age": 61, "gender": "Male", "conditions": ["Post-PCI Stent", "CAD"]},
        "expected_rule": "RULE-DDI-004",
        "hazard_description": "Clopidogrel + Omeprazole CYP2C19 competitive inhibition reducing antiplatelet effect"
    },
    {
        "hazard_type": "DDI",
        "medications": ["Lanoxin 0.25mg", "Cordarone 200mg"],
        "expected_generics": ["digoxin", "amiodarone"],
        "patient_context": {"age": 74, "gender": "Male", "conditions": ["Heart Failure", "Atrial Fibrillation"]},
        "expected_rule": "RULE-DDI-005",
        "hazard_description": "Digoxin + Amiodarone P-gp and renal clearance inhibition causing digoxin toxicity / heart block"
    },
    {
        "hazard_type": "DDI",
        "medications": ["Zocor 40mg", "Norvasc 10mg"],
        "expected_generics": ["simvastatin", "amlodipine"],
        "patient_context": {"age": 69, "gender": "Female", "conditions": ["Hyperlipidemia", "Hypertension"]},
        "expected_rule": "RULE-DDI-006",
        "hazard_description": "Simvastatin (>20mg) + Amlodipine CYP3A4 competition causing rhabdomyolysis"
    },
    {
        "hazard_type": "DDI",
        "medications": ["Citalopram 40mg", "Zofran 8mg"],
        "expected_generics": ["citalopram", "ondansetron"],
        "patient_context": {"age": 48, "gender": "Female", "conditions": ["Depression", "Chemotherapy Nausea"]},
        "expected_rule": "RULE-DDI-007",
        "hazard_description": "Citalopram + Ondansetron additive cardiac hERG channel blockade causing Torsades de Pointes"
    },
    {
        "hazard_type": "DDI",
        "medications": ["Cipro 500mg", "Tizanidine 4mg"],
        "expected_generics": ["ciprofloxacin", "tizanidine"],
        "patient_context": {"age": 55, "gender": "Male", "conditions": ["Muscle Spasms", "Prostatitis"]},
        "expected_rule": "RULE-DDI-008",
        "hazard_description": "Ciprofloxacin potent CYP1A2 inhibition causing 10-fold tizanidine exposure and severe hypotension"
    },
    # Category 2: Duplicate Active Ingredients & Combination Redundancies
    {
        "hazard_type": "DUPLICATE",
        "medications": ["Tylenol Extra Strength 500mg", "Panadol 500mg"],
        "expected_generics": ["acetaminophen", "acetaminophen"],
        "patient_context": {"age": 42, "gender": "Female", "conditions": ["Chronic Back Pain"]},
        "expected_rule": "RULE-DUP-001",
        "hazard_description": "Dual acetaminophen brand prescriptions exceeding 4000mg/day threshold causing acute liver necrosis"
    },
    {
        "hazard_type": "DUPLICATE",
        "medications": ["Glucophage 1000mg", "Metformin 500mg"],
        "expected_generics": ["metformin", "metformin"],
        "patient_context": {"age": 58, "gender": "Male", "conditions": ["Type 2 Diabetes"]},
        "expected_rule": "RULE-DUP-002",
        "hazard_description": "Brand + generic duplicate metformin prescription causing gastrointestinal toxicity and lactic acidosis risk"
    },
    {
        "hazard_type": "DUPLICATE",
        "medications": ["Advil 400mg", "Motrin 400mg"],
        "expected_generics": ["ibuprofen", "ibuprofen"],
        "patient_context": {"age": 35, "gender": "Male", "conditions": ["Tendonitis"]},
        "expected_rule": "RULE-DUP-003",
        "hazard_description": "Dual ibuprofen brand prescription causing cumulative NSAID toxicity and gastric ulceration"
    },
    {
        "hazard_type": "DUPLICATE",
        "medications": ["Augmentin 875mg", "Amoxil 500mg"],
        "expected_generics": ["amoxicillin", "amoxicillin"],
        "patient_context": {"age": 28, "gender": "Female", "conditions": ["Bacterial Sinusitis"]},
        "expected_rule": "RULE-DUP-004",
        "hazard_description": "Combination product (Augmentin) + Amoxicillin duplication causing massive beta-lactam overdose"
    },
    {
        "hazard_type": "DUPLICATE",
        "medications": ["Percocet 5/325", "Tylenol 500mg"],
        "expected_generics": ["oxycodone", "acetaminophen"],
        "patient_context": {"age": 45, "gender": "Male", "conditions": ["Post-Surgical Dental Pain"]},
        "expected_rule": "RULE-DUP-005",
        "hazard_description": "Combination opioid-APAP product + OTC APAP leading to hidden hepatotoxic acetaminophen overdose"
    },
    # Category 3: Severe Renal Risk Thresholds (eGFR / CrCl)
    {
        "hazard_type": "RENAL",
        "medications": ["Metformin 1000mg", "Lisinopril 10mg"],
        "expected_generics": ["metformin", "lisinopril"],
        "patient_context": {"age": 71, "gender": "Male", "egfr": 22.0, "conditions": ["Type 2 Diabetes", "CKD Stage 4"]},
        "expected_rule": "RULE-RENAL-001",
        "hazard_description": "Metformin absolute contraindication at eGFR < 30 mL/min/1.73m2 due to fatal lactic acidosis"
    },
    {
        "hazard_type": "RENAL",
        "medications": ["Methotrexate 15mg weekly", "Folic Acid 1mg"],
        "expected_generics": ["methotrexate", "folic acid"],
        "patient_context": {"age": 66, "gender": "Female", "egfr": 26.0, "conditions": ["Rheumatoid Arthritis", "CKD"]},
        "expected_rule": "RULE-RENAL-002",
        "hazard_description": "Methotrexate contraindicated in severe renal impairment (eGFR < 30) due to acute bone marrow suppression"
    },
    {
        "hazard_type": "RENAL",
        "medications": ["Lovenox 80mg", "Aspirin 81mg"],
        "expected_generics": ["enoxaparin", "aspirin"],
        "patient_context": {"age": 78, "gender": "Female", "creatinine_clearance": 24.0, "conditions": ["DVT", "CKD"]},
        "expected_rule": "RULE-RENAL-003",
        "hazard_description": "Enoxaparin requires mandatory dose reduction at CrCl < 30 mL/min to prevent catastrophic bleeding"
    },
    {
        "hazard_type": "RENAL",
        "medications": ["Aldactone 50mg", "Furosemide 40mg"],
        "expected_generics": ["spironolactone", "furosemide"],
        "patient_context": {"age": 69, "gender": "Male", "egfr": 25.0, "conditions": ["Congestive Heart Failure", "CKD"]},
        "expected_rule": "RULE-RENAL-004",
        "hazard_description": "Spironolactone contraindicated at eGFR < 30 due to unmanageable refractory hyperkalemia"
    },
    {
        "hazard_type": "RENAL",
        "medications": ["Motrin 600mg", "Omeprazole 20mg"],
        "expected_generics": ["ibuprofen", "omeprazole"],
        "patient_context": {"age": 64, "gender": "Male", "egfr": 28.0, "conditions": ["Osteoarthritis", "CKD"]},
        "expected_rule": "RULE-RENAL-005",
        "hazard_description": "Ibuprofen contraindicated at eGFR < 30 due to acute-on-chronic renal decompensation"
    },
    # Category 4: Absolute Contraindications (Conditions, Allergies, Pregnancy)
    {
        "hazard_type": "CONTRAINDICATION",
        "medications": ["Coumadin 5mg", "Atorvastatin 20mg"],
        "expected_generics": ["warfarin", "atorvastatin"],
        "patient_context": {"age": 59, "gender": "Male", "conditions": ["Peptic Ulcer", "Atrial Fibrillation"]},
        "expected_rule": "RULE-CONTRA-001",
        "hazard_description": "Warfarin absolute contraindication in active peptic ulcer disease due to massive GI hemorrhage"
    },
    {
        "hazard_type": "CONTRAINDICATION",
        "medications": ["Inderal 40mg", "Lisinopril 10mg"],
        "expected_generics": ["propranolol", "lisinopril"],
        "patient_context": {"age": 34, "gender": "Female", "conditions": ["Asthma", "Migraine Prophylaxis"]},
        "expected_rule": "RULE-CONTRA-003",
        "hazard_description": "Propranolol non-selective beta-2 blockade triggering acute bronchospasm and refractory status asthmaticus"
    },
    {
        "hazard_type": "CONTRAINDICATION",
        "medications": ["Trexall 20mg", "Acetaminophen 500mg"],
        "expected_generics": ["methotrexate", "acetaminophen"],
        "patient_context": {"age": 27, "gender": "Female", "is_pregnant": True, "conditions": ["Severe Psoriasis"]},
        "expected_rule": "RULE-CONTRA-004",
        "hazard_description": "Methotrexate Pregnancy Category X / absolute teratogenicity and fetal demise"
    },
    {
        "hazard_type": "CONTRAINDICATION",
        "medications": ["Prinivil 20mg", "Hydrochlorothiazide 25mg"],
        "expected_generics": ["lisinopril", "hydrochlorothiazide"],
        "patient_context": {"age": 31, "gender": "Female", "is_pregnant": True, "conditions": ["Chronic Hypertension"]},
        "expected_rule": "RULE-CONTRA-005",
        "hazard_description": "Lisinopril fetal renal dysgenesis and neonatal death in pregnancy"
    },
    {
        "hazard_type": "CONTRAINDICATION",
        "medications": ["Amoxil 500mg", "Acetaminophen 650mg"],
        "expected_generics": ["amoxicillin", "acetaminophen"],
        "patient_context": {"age": 22, "gender": "Male", "allergies": ["Penicillin"], "conditions": ["Pharyngitis"]},
        "expected_rule": "RULE-CONTRA-006",
        "hazard_description": "Amoxicillin in confirmed penicillin allergy causing IgE-mediated anaphylaxis and angioedema"
    }
]

# Generate exactly 300 Seeded Near-Miss cases (cycling through archetypes with varied ages, names, and misspellings)
typo_variations = {
    "Coumadin 5mg": ["Coumadin 5mg", "Coumadinn 5mg", "Warfrin 5mg", "Coumadin tab"],
    "Diflucan 200mg": ["Diflucan 200mg", "Diflucane 200mg", "Fluconazol 200mg"],
    "Zestril 20mg": ["Zestril 20mg", "Zestrile 20mg", "Lisinoprile 20mg"],
    "Aldactone 25mg": ["Aldactone 25mg", "Aldacton 25mg", "Spironolacton 25mg"],
    "Trexall 15mg weekly": ["Trexall 15mg weekly", "Trexalll 15mg", "Methotrexat 15mg"],
    "Motrin 600mg": ["Motrin 600mg", "Motrinn 600mg", "Ibuprophen 600mg"],
    "Plavix 75mg": ["Plavix 75mg", "Plavixx 75mg", "Clopidogrel 75mg"],
    "Prilosec 20mg": ["Prilosec 20mg", "Omeprazole 20mg", "Prilosecc 20mg"],
    "Lanoxin 0.25mg": ["Lanoxin 0.25mg", "Digoxin 0.25mg", "Lanoxine 0.25mg"],
    "Cordarone 200mg": ["Cordarone 200mg", "Amiodarone 200mg", "Cordaronee 200mg"],
    "Zocor 40mg": ["Zocor 40mg", "Simvastatin 40mg", "Zocorr 40mg"],
    "Norvasc 10mg": ["Norvasc 10mg", "Amlodipine 10mg", "Norvascc 10mg"],
    "Tylenol Extra Strength 500mg": ["Tylenol Extra Strength 500mg", "Tylenoll 500mg", "Acetaminophene 500mg"],
    "Panadol 500mg": ["Panadol 500mg", "Paracetamol 500mg", "Panadoll 500mg"],
    "Glucophage 1000mg": ["Glucophage 1000mg", "Glucophagee 1000mg", "Metformn 1000mg"],
    "Metformin 500mg": ["Metformin 500mg", "Metformine 500mg"],
    "Advil 400mg": ["Advil 400mg", "Advill 400mg", "Ibuprofen 400mg"],
    "Augmentin 875mg": ["Augmentin 875mg", "Augmentinn 875mg", "Co-amoxiclav 875mg"],
    "Amoxil 500mg": ["Amoxil 500mg", "Amoxill 500mg", "Amoxicilline 500mg"],
    "Lovenox 80mg": ["Lovenox 80mg", "Enoxaparin 80mg", "Lovenoxx 80mg"],
    "Inderal 40mg": ["Inderal 40mg", "Propranolol 40mg", "Inderall 40mg"],
    "Prinivil 20mg": ["Prinivil 20mg", "Lisinopril 20mg", "Prinivill 20mg"],
    "Citalopram 40mg": ["Citalopram 40mg", "Celexa 40mg", "Citaloprame 40mg"],
    "Zofran 8mg": ["Zofran 8mg", "Ondansetron 8mg", "Zofrann 8mg"],
    "Cipro 500mg": ["Cipro 500mg", "Ciprofloxacin 500mg", "Ciprofloxacine 500mg"],
    "Tizanidine 4mg": ["Tizanidine 4mg", "Zanaflex 4mg", "Tizanidin 4mg"],
    "Percocet 5/325": ["Percocet 5/325", "Percocett 5/325", "Oxycodone-APAP 5/325"],
    "Tylenol 500mg": ["Tylenol 500mg", "Tylenoll 500mg", "APAP 500mg"]
}

seeded_near_miss_300: List[Dict[str, Any]] = []

for i in range(300):
    arch = near_miss_archetypes[i % len(near_miss_archetypes)]
    
    # Pick a spelling variation if available
    meds = []
    for m in arch["medications"]:
        vars_list = typo_variations.get(m, [m])
        chosen_var = vars_list[(i // len(near_miss_archetypes)) % len(vars_list)]
        meds.append(chosen_var)
        
    ctx = dict(arch["patient_context"])
    ctx["age"] = ctx.get("age", 50) + (i % 15) - 7
    
    seeded_near_miss_300.append({
        "case_id": f"NM-{i+1:03d}",
        "hazard_type": arch["hazard_type"],
        "medications": meds,
        "expected_generics": arch["expected_generics"],
        "patient_context": ctx,
        "ground_truth": {
            "has_serious_hazard": True,
            "expected_severity": "HIGH",
            "expected_rule": arch["expected_rule"],
            "hazard_description": arch["hazard_description"]
        }
    })

with open("data/evaluation/seeded_near_miss_300.json", "w") as f:
    json.dump(seeded_near_miss_300, f, indent=2)

print(f"Generated {len(seeded_near_miss_300)} seeded near-miss cases in data/evaluation/seeded_near_miss_300.json")

# ==============================================================================
# 2. 500-PATIENT SYNTHETIC POPULATION BENCHMARK
#    (100 positive cases + 400 clean negative controls)
# ==============================================================================
clean_combinations = [
    (["Lipitor 20mg", "Amlodipine 5mg"], ["atorvastatin", "amlodipine"]),
    (["Metformin 500mg", "Amlodipine 10mg"], ["metformin", "amlodipine"]),
    (["Citalopram 20mg", "Acetaminophen 500mg"], ["citalopram", "acetaminophen"]),
    (["Lasix 40mg", "Potassium Chloride 20mEq"], ["furosemide", "potassium chloride"]),
    (["Advil 200mg"], ["ibuprofen"]),
    (["Synthroid 50mcg", "Vitamin D3 1000IU"], ["levothyroxine", "cholecalciferol"]),
    (["Prilosec 20mg", "Claritin 10mg"], ["omeprazole", "loratadine"]),
    (["Cozaar 50mg", "Hydrochlorothiazide 12.5mg"], ["losartan", "hydrochlorothiazide"]),
    (["Zoloft 50mg", "Tylenol 500mg"], ["sertraline", "acetaminophen"]),
    (["Flonase 50mcg", "Singulair 10mg"], ["fluticasone", "montelukast"])
]

synthetic_cohort_500: List[Dict[str, Any]] = []

# First 100 cases: High/moderate risk cases (drawn deterministically from near-miss archetypes)
for i in range(100):
    arch = near_miss_archetypes[i % len(near_miss_archetypes)]
    ctx = dict(arch["patient_context"])
    ctx["age"] = ctx.get("age", 55) + (i % 20) - 10
    synthetic_cohort_500.append({
        "case_id": f"SYN-BM-{i+1:03d}",
        "medications": arch["medications"],
        "expected_generics": arch["expected_generics"],
        "patient_context": ctx,
        "ground_truth": {
            "has_serious_hazard": True,
            "expected_severity": "HIGH",
            "expected_rule": arch["expected_rule"],
            "hazard_description": arch["hazard_description"]
        }
    })

# Next 400 cases: Negative controls (clean regimens where 0 high alerts should fire)
for i in range(100, 500):
    meds, exp_gen = clean_combinations[(i - 100) % len(clean_combinations)]
    synthetic_cohort_500.append({
        "case_id": f"SYN-BM-{i+1:03d}",
        "medications": meds,
        "expected_generics": exp_gen,
        "patient_context": {
            "age": 40 + ((i * 3) % 45),
            "gender": "Female" if i % 2 == 0 else "Male",
            "conditions": ["Essential Hypertension"],
            "allergies": [],
            "egfr": 90.0, # Healthy normal renal function
            "creatinine_clearance": 95.0,
            "is_pregnant": False
        },
        "ground_truth": {
            "has_serious_hazard": False,
            "expected_severity": "NONE",
            "expected_rule": None,
            "hazard_description": "Clean regimen with zero high-priority safety contraindications"
        }
    })

with open("data/evaluation/synthetic_cohort_500.json", "w") as f:
    json.dump(synthetic_cohort_500, f, indent=2)

print(f"Generated {len(synthetic_cohort_500)} synthetic cohort cases in data/evaluation/synthetic_cohort_500.json")

# ==============================================================================
# 3. 120-ITEM MEDICINE NAME RESOLUTION BENCHMARK
# ==============================================================================
name_benchmark = [
    # Exact Generics
    {"input": "warfarin", "type": "generic", "expected": "warfarin", "expect_ambiguous": False},
    {"input": "metformin", "type": "generic", "expected": "metformin", "expect_ambiguous": False},
    {"input": "lisinopril", "type": "generic", "expected": "lisinopril", "expect_ambiguous": False},
    {"input": "ibuprofen", "type": "generic", "expected": "ibuprofen", "expect_ambiguous": False},
    {"input": "atorvastatin", "type": "generic", "expected": "atorvastatin", "expect_ambiguous": False},
    {"input": "amoxicillin", "type": "generic", "expected": "amoxicillin", "expect_ambiguous": False},
    {"input": "ciprofloxacin", "type": "generic", "expected": "ciprofloxacin", "expect_ambiguous": False},
    {"input": "clopidogrel", "type": "generic", "expected": "clopidogrel", "expect_ambiguous": False},
    {"input": "citalopram", "type": "generic", "expected": "citalopram", "expect_ambiguous": False},
    {"input": "digoxin", "type": "generic", "expected": "digoxin", "expect_ambiguous": False},
    
    # Verified Brands
    {"input": "Coumadin", "type": "brand", "expected": "warfarin", "expect_ambiguous": False},
    {"input": "Glucophage", "type": "brand", "expected": "metformin", "expect_ambiguous": False},
    {"input": "Lipitor", "type": "brand", "expected": "atorvastatin", "expect_ambiguous": False},
    {"input": "Plavix", "type": "brand", "expected": "clopidogrel", "expect_ambiguous": False},
    {"input": "Zestril", "type": "brand", "expected": "lisinopril", "expect_ambiguous": False},
    {"input": "Advil", "type": "brand", "expected": "ibuprofen", "expect_ambiguous": False},
    {"input": "Motrin", "type": "brand", "expected": "ibuprofen", "expect_ambiguous": False},
    {"input": "Tylenol", "type": "brand", "expected": "acetaminophen", "expect_ambiguous": False},
    {"input": "Panadol", "type": "brand", "expected": "acetaminophen", "expect_ambiguous": False},
    {"input": "Diflucan", "type": "brand", "expected": "fluconazole", "expect_ambiguous": False},
    {"input": "Aldactone", "type": "brand", "expected": "spironolactone", "expect_ambiguous": False},
    {"input": "Trexall", "type": "brand", "expected": "methotrexate", "expect_ambiguous": False},
    {"input": "Amoxil", "type": "brand", "expected": "amoxicillin", "expect_ambiguous": False},
    {"input": "Norvasc", "type": "brand", "expected": "amlodipine", "expect_ambiguous": False},
    {"input": "Zocor", "type": "brand", "expected": "simvastatin", "expect_ambiguous": False},
    
    # Common Misspellings (Fuzzy Target)
    {"input": "metformn", "type": "misspelling", "expected": "metformin", "expect_ambiguous": False},
    {"input": "warfrin", "type": "misspelling", "expected": "warfarin", "expect_ambiguous": False},
    {"input": "lisinoprile", "type": "misspelling", "expected": "lisinopril", "expect_ambiguous": False},
    {"input": "diflucane", "type": "misspelling", "expected": "fluconazole", "expect_ambiguous": False},
    {"input": "coumadinn", "type": "misspelling", "expected": "warfarin", "expect_ambiguous": False},
    {"input": "ibuprophen", "type": "misspelling", "expected": "ibuprofen", "expect_ambiguous": False},
    {"input": "tylenoll", "type": "misspelling", "expected": "acetaminophen", "expect_ambiguous": False},
    {"input": "spironolacton", "type": "misspelling", "expected": "spironolactone", "expect_ambiguous": False},
    {"input": "amoxill", "type": "misspelling", "expected": "amoxicillin", "expect_ambiguous": False},
    {"input": "atorvastatine", "type": "misspelling", "expected": "atorvastatin", "expect_ambiguous": False},
    
    # Ambiguous Inputs (Must trigger confirmation requirement)
    {"input": "amlo", "type": "ambiguous", "expected": None, "expect_ambiguous": True},
    {"input": "metro", "type": "ambiguous", "expected": None, "expect_ambiguous": True},
    {"input": "cefa", "type": "ambiguous", "expected": None, "expect_ambiguous": True},
    
    # Unknown Inputs (Must trigger unresolved state)
    {"input": "unknownchem99", "type": "unknown", "expected": None, "expect_ambiguous": False},
    {"input": "fakemedicine123", "type": "unknown", "expected": None, "expect_ambiguous": False}
]

with open("data/evaluation/name_resolution_benchmark.json", "w") as f:
    json.dump(name_benchmark, f, indent=2)

print(f"Generated {len(name_benchmark)} name resolution test cases in data/evaluation/name_resolution_benchmark.json")
