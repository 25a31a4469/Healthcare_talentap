from sqlalchemy.orm import Session
try:
    from backend.app.models import (
        MedicineCatalogue, BrandMapping, InteractionRule,
        DuplicateTherapyRule, RenalRiskRule, ContraindicationRule, DatasetMetadata
    )
except ImportError:
    from app.models import (
        MedicineCatalogue, BrandMapping, InteractionRule,
        DuplicateTherapyRule, RenalRiskRule, ContraindicationRule, DatasetMetadata
    )

MEDICINE_CATALOGUE_DATA = [
    {
        "generic_name": "warfarin",
        "therapeutic_class": "Anticoagulant (Vitamin K Antagonist)",
        "active_ingredients": ["warfarin"],
        "brand_names": ["Coumadin", "Jantoven"],
        "synonyms": ["warfarin sodium"],
        "common_misspellings": ["warfrin", "warfarine", "coumadinn"],
        "standard_dosing": "2 - 10 mg orally once daily adjusted by INR (target 2.0 - 3.0)",
        "renal_cleared": False,
        "black_box_warnings": "Major or fatal bleeding. Regular INR monitoring required."
    },
    {
        "generic_name": "fluconazole",
        "therapeutic_class": "Antifungal (Triazole)",
        "active_ingredients": ["fluconazole"],
        "brand_names": ["Diflucan"],
        "synonyms": ["fluconazol"],
        "common_misspellings": ["fluconazol", "diflucane", "fluconasole"],
        "standard_dosing": "100 - 400 mg orally once daily",
        "renal_cleared": True,
        "black_box_warnings": "Potent CYP2C9 inhibitor. QT prolongation and hepatic toxicity warnings."
    },
    {
        "generic_name": "metformin",
        "therapeutic_class": "Antidiabetic (Biguanide)",
        "active_ingredients": ["metformin"],
        "brand_names": ["Glucophage", "Glumetza", "Fortamet", "Riomet"],
        "synonyms": ["metformin hydrochloride", "metformin hcl"],
        "common_misspellings": ["metformn", "metformine", "glucophagee", "metformim"],
        "standard_dosing": "500 - 1000 mg orally twice daily with meals (max 2000-2550 mg/day)",
        "renal_cleared": True,
        "black_box_warnings": "Lactic acidosis risk, markedly elevated in renal impairment (eGFR < 30)."
    },
    {
        "generic_name": "ibuprofen",
        "therapeutic_class": "NSAID (Nonsteroidal Anti-inflammatory)",
        "active_ingredients": ["ibuprofen"],
        "brand_names": ["Advil", "Motrin", "Nurofen"],
        "synonyms": ["iso-butyl-propanoic-phenolic acid"],
        "common_misspellings": ["ibuprophen", "advill", "motrinn", "iburofen"],
        "standard_dosing": "200 - 800 mg orally every 6 to 8 hours as needed (max 2400 mg/day)",
        "renal_cleared": True,
        "black_box_warnings": "Increased risk of serious cardiovascular thrombotic events and gastrointestinal ulceration/bleeding."
    },
    {
        "generic_name": "acetaminophen",
        "therapeutic_class": "Analgesic / Antipyretic",
        "active_ingredients": ["acetaminophen"],
        "brand_names": ["Tylenol", "Panadol", "Calpol", "Mapap"],
        "synonyms": ["paracetamol", "apap"],
        "common_misspellings": ["acetaminophene", "tylenoll", "paracetemol", "paracetmol"],
        "standard_dosing": "325 - 650 mg orally every 4 to 6 hours (max 3000-4000 mg/day)",
        "renal_cleared": False,
        "black_box_warnings": "Severe hepatotoxicity associated with doses exceeding 4000 mg/24h or combination product duplication."
    },
    {
        "generic_name": "lisinopril",
        "therapeutic_class": "ACE Inhibitor (Antihypertensive)",
        "active_ingredients": ["lisinopril"],
        "brand_names": ["Zestril", "Prinivil", "Qbrelis"],
        "synonyms": ["lisinopril dihydrate"],
        "common_misspellings": ["lisinoprile", "zestrile", "lisinopri"],
        "standard_dosing": "10 - 40 mg orally once daily",
        "renal_cleared": True,
        "black_box_warnings": "Fetal toxicity: Discontinue as soon as pregnancy is detected."
    },
    {
        "generic_name": "spironolactone",
        "therapeutic_class": "Aldosterone Antagonist (Potassium-Sparing Diuretic)",
        "active_ingredients": ["spironolactone"],
        "brand_names": ["Aldactone", "CaroSpir"],
        "synonyms": ["spironolacton"],
        "common_misspellings": ["spironolacton", "aldacton", "spironalactone"],
        "standard_dosing": "25 - 100 mg orally once or twice daily",
        "renal_cleared": True,
        "black_box_warnings": "Hyperkalemia risk. Avoid in severe renal impairment or combination with potassium supplements/ACEi."
    },
    {
        "generic_name": "methotrexate",
        "therapeutic_class": "Antimetabolite / Immunosuppressant",
        "active_ingredients": ["methotrexate"],
        "brand_names": ["Trexall", "Otrexup", "Rasuvo"],
        "synonyms": ["amethopterin", "mtx"],
        "common_misspellings": ["methotrexat", "trexalll", "metotrexate"],
        "standard_dosing": "7.5 - 25 mg orally once weekly for rheumatoid arthritis/psoriasis",
        "renal_cleared": True,
        "black_box_warnings": "Bone marrow suppression, hepatotoxicity, opportunistic infections, fetal death/teratogenicity."
    },
    {
        "generic_name": "amoxicillin",
        "therapeutic_class": "Aminopenicillin Antibiotic",
        "active_ingredients": ["amoxicillin"],
        "brand_names": ["Amoxil", "Moxatag", "Trimox"],
        "synonyms": ["amoxicilline", "amoxycillin"],
        "common_misspellings": ["amoxacillin", "amoxicilln", "amoxil"],
        "standard_dosing": "500 - 875 mg orally every 8 to 12 hours",
        "renal_cleared": True,
        "black_box_warnings": "Severe anaphylactic and hypersensitivity reactions in penicillin-allergic patients."
    },
    {
        "generic_name": "atorvastatin",
        "therapeutic_class": "HMG-CoA Reductase Inhibitor (Statin)",
        "active_ingredients": ["atorvastatin"],
        "brand_names": ["Lipitor"],
        "synonyms": ["atorvastatin calcium"],
        "common_misspellings": ["atorvastatine", "lipitorr", "atorvastatn"],
        "standard_dosing": "10 - 80 mg orally once daily",
        "renal_cleared": False,
        "black_box_warnings": "Myopathy and rhabdomyolysis risk elevated with CYP3A4 inhibitors."
    },
    {
        "generic_name": "clarithromycin",
        "therapeutic_class": "Macrolide Antibiotic",
        "active_ingredients": ["clarithromycin"],
        "brand_names": ["Biaxin"],
        "synonyms": ["claritromycin"],
        "common_misspellings": ["clarithromycine", "biaxinn", "clarithromicin"],
        "standard_dosing": "250 - 500 mg orally every 12 hours",
        "renal_cleared": True,
        "black_box_warnings": "Potent CYP3A4 inhibitor; QT prolongation and fatal arrhythmia risks with concurrent statins/QT drugs."
    },
    {
        "generic_name": "citalopram",
        "therapeutic_class": "SSRI Antidepressant",
        "active_ingredients": ["citalopram"],
        "brand_names": ["Celexa"],
        "synonyms": ["citalopram hydrobromide"],
        "common_misspellings": ["citaloprame", "celexaa"],
        "standard_dosing": "20 - 40 mg orally once daily",
        "renal_cleared": False,
        "black_box_warnings": "Dose-dependent QT prolongation. Maximum recommended dose 20 mg in elderly."
    },
    {
        "generic_name": "ondansetron",
        "therapeutic_class": "5-HT3 Receptor Antagonist (Antiemetic)",
        "active_ingredients": ["ondansetron"],
        "brand_names": ["Zofran", "Zuplenz"],
        "synonyms": ["ondansetron hydrochloride"],
        "common_misspellings": ["ondansetronn", "zofrann", "ondansetrone"],
        "standard_dosing": "4 - 8 mg orally every 8 hours as needed",
        "renal_cleared": False,
        "black_box_warnings": "Dose-dependent QT interval prolongation and Torsades de Pointes."
    },
    {
        "generic_name": "digoxin",
        "therapeutic_class": "Cardiac Glycoside (Inotrope)",
        "active_ingredients": ["digoxin"],
        "brand_names": ["Lanoxin", "Digitek"],
        "synonyms": ["digitalis"],
        "common_misspellings": ["digoxine", "lanoxinn", "digoxn"],
        "standard_dosing": "0.125 - 0.25 mg orally once daily (therapeutic range 0.5 - 0.9 ng/mL)",
        "renal_cleared": True,
        "black_box_warnings": "Narrow therapeutic index; life-threatening arrhythmias with P-glycoprotein inhibitors or hypokalemia."
    },
    {
        "generic_name": "amiodarone",
        "therapeutic_class": "Class III Antiarrhythmic",
        "active_ingredients": ["amiodarone"],
        "brand_names": ["Pacerone", "Cordarone", "Nexterone"],
        "synonyms": ["amiodarone hydrochloride"],
        "common_misspellings": ["amiodaron", "cordaron", "paceronn"],
        "standard_dosing": "100 - 400 mg orally once daily",
        "renal_cleared": False,
        "black_box_warnings": "Pulmonary toxicity, hepatotoxicity, marked P-gp/CYP inhibition doubling digoxin levels."
    },
    {
        "generic_name": "clopidogrel",
        "therapeutic_class": "P2Y12 Antiplatelet Agent",
        "active_ingredients": ["clopidogrel"],
        "brand_names": ["Plavix"],
        "synonyms": ["clopidogrel bisulfate"],
        "common_misspellings": ["clopidogril", "plavixx", "clopidogrel"],
        "standard_dosing": "75 mg orally once daily",
        "renal_cleared": False,
        "black_box_warnings": "Diminished antiplatelet effect in CYP2C19 poor metabolizers or when co-administered with omeprazole."
    },
    {
        "generic_name": "omeprazole",
        "therapeutic_class": "Proton Pump Inhibitor (PPI)",
        "active_ingredients": ["omeprazole"],
        "brand_names": ["Prilosec", "Zegerid"],
        "synonyms": ["omeprazol"],
        "common_misspellings": ["omeprazol", "prilosecc", "omeprazole"],
        "standard_dosing": "20 - 40 mg orally once daily before morning meal",
        "renal_cleared": False,
        "black_box_warnings": "CYP2C19 competitive inhibition reduces clopidogrel active metabolite formation."
    },
    {
        "generic_name": "potassium chloride",
        "therapeutic_class": "Electrolyte Supplement",
        "active_ingredients": ["potassium chloride"],
        "brand_names": ["K-Dur", "Klor-Con", "Micro-K"],
        "synonyms": ["kcl"],
        "common_misspellings": ["klor con", "potassium chlorid"],
        "standard_dosing": "20 - 40 mEq orally daily in divided doses",
        "renal_cleared": True,
        "black_box_warnings": "Hyperkalemia risk markedly heightened when given with ACE inhibitors or aldosterone antagonists."
    },
    {
        "generic_name": "enoxaparin",
        "therapeutic_class": "Low Molecular Weight Heparin (LMWH)",
        "active_ingredients": ["enoxaparin"],
        "brand_names": ["Lovenox"],
        "synonyms": ["enoxaparin sodium"],
        "common_misspellings": ["enoxaparine", "lovenoxx"],
        "standard_dosing": "1 mg/kg subcutaneously every 12 hours (treatment) or 40 mg daily (prophylaxis)",
        "renal_cleared": True,
        "black_box_warnings": "Spinal/epidural hematomas. Bioaccumulation and fatal hemorrhage risk when CrCl < 30 mL/min without dose adjustment."
    },
    {
        "generic_name": "gabapentin",
        "therapeutic_class": "Anticonvulsant / Neuropathic Pain Agent",
        "active_ingredients": ["gabapentin"],
        "brand_names": ["Neurontin", "Gralise"],
        "synonyms": ["gabapentine"],
        "common_misspellings": ["gabapentine", "neurontinn"],
        "standard_dosing": "300 - 1800 mg orally daily in divided doses",
        "renal_cleared": True,
        "black_box_warnings": "CNS depression. Elimination 100% renal; requires strict dose titration based on renal clearance."
    },
    {
        "generic_name": "naproxen",
        "therapeutic_class": "NSAID (Nonsteroidal Anti-inflammatory)",
        "active_ingredients": ["naproxen"],
        "brand_names": ["Aleve", "Naprosyn", "Anaprox"],
        "synonyms": ["naproxen sodium"],
        "common_misspellings": ["naproxenn", "alevee", "naprosyn"],
        "standard_dosing": "250 - 500 mg orally twice daily",
        "renal_cleared": True,
        "black_box_warnings": "GI bleeding, ulceration, cardiovascular thrombotic risks."
    },
    {
        "generic_name": "propranolol",
        "therapeutic_class": "Non-selective Beta-Adrenergic Blocker",
        "active_ingredients": ["propranolol"],
        "brand_names": ["Inderal", "InnoPran"],
        "synonyms": ["propranolol hydrochloride"],
        "common_misspellings": ["propranalol", "inderal"],
        "standard_dosing": "40 - 160 mg orally daily in divided doses",
        "renal_cleared": False,
        "black_box_warnings": "Bronchospasm: Contraindicated in asthma and chronic obstructive airway disease."
    },
    {
        "generic_name": "apixaban",
        "therapeutic_class": "Direct Oral Anticoagulant (DOAC - Factor Xa Inhibitor)",
        "active_ingredients": ["apixaban"],
        "brand_names": ["Eliquis"],
        "synonyms": ["apixabane"],
        "common_misspellings": ["eliquiss", "apixaban"],
        "standard_dosing": "5 mg orally twice daily (2.5 mg if 2 of: age>=80, weight<=60kg, serum Cr>=1.5)",
        "renal_cleared": True,
        "black_box_warnings": "Premature discontinuation increases risk of thrombotic events. Bleeding risk."
    },
    {
        "generic_name": "furosemide",
        "therapeutic_class": "Loop Diuretic",
        "active_ingredients": ["furosemide"],
        "brand_names": ["Lasix"],
        "synonyms": ["frusemide"],
        "common_misspellings": ["lasixx", "furosemid"],
        "standard_dosing": "20 - 80 mg orally daily",
        "renal_cleared": True,
        "black_box_warnings": "Potent diuresis leading to electrolyte depletion and dehydration."
    },
    {
        "generic_name": "amlodipine",
        "therapeutic_class": "Dihydropyridine Calcium Channel Blocker",
        "active_ingredients": ["amlodipine"],
        "brand_names": ["Norvasc"],
        "synonyms": ["amlodipine besylate"],
        "common_misspellings": ["norvascc", "amlodipin"],
        "standard_dosing": "5 - 10 mg orally once daily",
        "renal_cleared": False,
        "black_box_warnings": "Peripheral edema and hypotension."
    },
    {
        "generic_name": "simvastatin",
        "therapeutic_class": "HMG-CoA Reductase Inhibitor (Statin)",
        "active_ingredients": ["simvastatin"],
        "brand_names": ["Zocor"],
        "synonyms": ["simvastatine"],
        "common_misspellings": ["simvastatn", "zocorr"],
        "standard_dosing": "10 - 40 mg orally once daily in evening",
        "renal_cleared": False,
        "black_box_warnings": "Myopathy and rhabdomyolysis risk; dose capped at 20 mg when co-prescribed with amlodipine."
    },
    {
        "generic_name": "ciprofloxacin",
        "therapeutic_class": "Fluoroquinolone Antibiotic",
        "active_ingredients": ["ciprofloxacin"],
        "brand_names": ["Cipro"],
        "synonyms": ["ciprofloxacin hydrochloride"],
        "common_misspellings": ["ciprofloxacine", "cipro"],
        "standard_dosing": "250 - 750 mg orally every 12 hours",
        "renal_cleared": True,
        "black_box_warnings": "Tendinitis, tendon rupture, peripheral neuropathy, and CNS effects. Strong CYP1A2 inhibitor contraindicated with tizanidine."
    },
    {
        "generic_name": "tizanidine",
        "therapeutic_class": "Central Alpha-2 Adrenergic Agonist (Muscle Relaxant)",
        "active_ingredients": ["tizanidine"],
        "brand_names": ["Zanaflex"],
        "synonyms": ["tizanidine hydrochloride"],
        "common_misspellings": ["tizanidin", "zanaflexx"],
        "standard_dosing": "2 - 8 mg orally three to four times daily",
        "renal_cleared": True,
        "black_box_warnings": "Concomitant use with ciprofloxacin or other potent CYP1A2 inhibitors is contraindicated due to profound hypotension and excessive sedation."
    },
    {
        "generic_name": "amoxicillin / clavulanate",
        "therapeutic_class": "Aminopenicillin / Beta-Lactamase Inhibitor Combination",
        "active_ingredients": ["amoxicillin", "clavulanate"],
        "brand_names": ["Augmentin"],
        "synonyms": ["co-amoxiclav", "amoxicillin clavulanate potassium"],
        "common_misspellings": ["augmentinn", "amox clav"],
        "standard_dosing": "500/125 - 875/125 mg orally every 12 hours",
        "renal_cleared": True,
        "black_box_warnings": "Severe anaphylactic and hypersensitivity reactions in penicillin-allergic patients."
    },
    {
        "generic_name": "oxycodone / acetaminophen",
        "therapeutic_class": "Opioid Agonist / Non-Opioid Analgesic Combination",
        "active_ingredients": ["oxycodone", "acetaminophen"],
        "brand_names": ["Percocet"],
        "synonyms": ["oxycodone and acetaminophen", "oxycodone-apap", "oxycodone/apap", "oxycodone apap", "apap/oxycodone"],
        "common_misspellings": ["percocett", "percocet 5/325"],
        "standard_dosing": "5/325 - 10/325 mg orally every 4 to 6 hours as needed",
        "renal_cleared": False,
        "black_box_warnings": "Severe hepatotoxicity from cumulative acetaminophen (>4000 mg/day); addiction, abuse, and life-threatening respiratory depression."
    },
    {
        "generic_name": "hydrocodone / acetaminophen",
        "therapeutic_class": "Opioid Agonist / Non-Opioid Analgesic Combination",
        "active_ingredients": ["hydrocodone", "acetaminophen"],
        "brand_names": ["Vicodin", "Norco"],
        "synonyms": ["hydrocodone and acetaminophen"],
        "common_misspellings": ["vicodinn", "norcoo"],
        "standard_dosing": "5/325 - 10/325 mg orally every 4 to 6 hours as needed",
        "renal_cleared": False,
        "black_box_warnings": "Severe hepatotoxicity risk from excessive acetaminophen; respiratory depression and addiction."
    },
    {
        "generic_name": "sitagliptin / metformin",
        "therapeutic_class": "DPP-4 Inhibitor / Biguanide Combination",
        "active_ingredients": ["sitagliptin", "metformin"],
        "brand_names": ["Janumet"],
        "synonyms": ["sitagliptin and metformin hydrochloride"],
        "common_misspellings": ["janumett"],
        "standard_dosing": "50/500 - 50/1000 mg orally twice daily with meals",
        "renal_cleared": True,
        "black_box_warnings": "Lactic acidosis risk with metformin component; contraindicated when eGFR < 30 mL/min/1.73m2."
    }
]

BRAND_MAPPINGS_DATA = [
    {"brand_name": "Coumadin", "generic_name": "warfarin", "active_ingredients": ["warfarin"]},
    {"brand_name": "Jantoven", "generic_name": "warfarin", "active_ingredients": ["warfarin"]},
    {"brand_name": "Diflucan", "generic_name": "fluconazole", "active_ingredients": ["fluconazole"]},
    {"brand_name": "Glucophage", "generic_name": "metformin", "active_ingredients": ["metformin"]},
    {"brand_name": "Glumetza", "generic_name": "metformin", "active_ingredients": ["metformin"]},
    {"brand_name": "Fortamet", "generic_name": "metformin", "active_ingredients": ["metformin"]},
    {"brand_name": "Janumet", "generic_name": "metformin / sitagliptin", "active_ingredients": ["metformin", "sitagliptin"]},
    {"brand_name": "Advil", "generic_name": "ibuprofen", "active_ingredients": ["ibuprofen"]},
    {"brand_name": "Motrin", "generic_name": "ibuprofen", "active_ingredients": ["ibuprofen"]},
    {"brand_name": "Nurofen", "generic_name": "ibuprofen", "active_ingredients": ["ibuprofen"]},
    {"brand_name": "Tylenol", "generic_name": "acetaminophen", "active_ingredients": ["acetaminophen"]},
    {"brand_name": "Panadol", "generic_name": "acetaminophen", "active_ingredients": ["acetaminophen"]},
    {"brand_name": "Calpol", "generic_name": "acetaminophen", "active_ingredients": ["acetaminophen"]},
    {"brand_name": "Mapap", "generic_name": "acetaminophen", "active_ingredients": ["acetaminophen"]},
    {"brand_name": "Excedrin", "generic_name": "acetaminophen / aspirin / caffeine", "active_ingredients": ["acetaminophen", "aspirin", "caffeine"]},
    {"brand_name": "Zestril", "generic_name": "lisinopril", "active_ingredients": ["lisinopril"]},
    {"brand_name": "Prinivil", "generic_name": "lisinopril", "active_ingredients": ["lisinopril"]},
    {"brand_name": "Aldactone", "generic_name": "spironolactone", "active_ingredients": ["spironolactone"]},
    {"brand_name": "Trexall", "generic_name": "methotrexate", "active_ingredients": ["methotrexate"]},
    {"brand_name": "Amoxil", "generic_name": "amoxicillin", "active_ingredients": ["amoxicillin"]},
    {"brand_name": "Lipitor", "generic_name": "atorvastatin", "active_ingredients": ["atorvastatin"]},
    {"brand_name": "Biaxin", "generic_name": "clarithromycin", "active_ingredients": ["clarithromycin"]},
    {"brand_name": "Celexa", "generic_name": "citalopram", "active_ingredients": ["citalopram"]},
    {"brand_name": "Zofran", "generic_name": "ondansetron", "active_ingredients": ["ondansetron"]},
    {"brand_name": "Lanoxin", "generic_name": "digoxin", "active_ingredients": ["digoxin"]},
    {"brand_name": "Cordarone", "generic_name": "amiodarone", "active_ingredients": ["amiodarone"]},
    {"brand_name": "Pacerone", "generic_name": "amiodarone", "active_ingredients": ["amiodarone"]},
    {"brand_name": "Plavix", "generic_name": "clopidogrel", "active_ingredients": ["clopidogrel"]},
    {"brand_name": "Prilosec", "generic_name": "omeprazole", "active_ingredients": ["omeprazole"]},
    {"brand_name": "Lovenox", "generic_name": "enoxaparin", "active_ingredients": ["enoxaparin"]},
    {"brand_name": "Neurontin", "generic_name": "gabapentin", "active_ingredients": ["gabapentin"]},
    {"brand_name": "Aleve", "generic_name": "naproxen", "active_ingredients": ["naproxen"]},
    {"brand_name": "Inderal", "generic_name": "propranolol", "active_ingredients": ["propranolol"]},
    {"brand_name": "Eliquis", "generic_name": "apixaban", "active_ingredients": ["apixaban"]},
    {"brand_name": "Lasix", "generic_name": "furosemide", "active_ingredients": ["furosemide"]},
    {"brand_name": "Norvasc", "generic_name": "amlodipine", "active_ingredients": ["amlodipine"]},
    {"brand_name": "Augmentin", "generic_name": "amoxicillin / clavulanate", "active_ingredients": ["amoxicillin", "clavulanate"]},
    {"brand_name": "Percocet", "generic_name": "oxycodone / acetaminophen", "active_ingredients": ["oxycodone", "acetaminophen"]},
    {"brand_name": "Vicodin", "generic_name": "hydrocodone / acetaminophen", "active_ingredients": ["hydrocodone", "acetaminophen"]},
    {"brand_name": "Norco", "generic_name": "hydrocodone / acetaminophen", "active_ingredients": ["hydrocodone", "acetaminophen"]},
    {"brand_name": "Janumet", "generic_name": "sitagliptin / metformin", "active_ingredients": ["sitagliptin", "metformin"]},
    {"brand_name": "Zestoretic", "generic_name": "lisinopril / hydrochlorothiazide", "active_ingredients": ["lisinopril", "hydrochlorothiazide"]},
    {"brand_name": "Hyzaar", "generic_name": "losartan / hydrochlorothiazide", "active_ingredients": ["losartan", "hydrochlorothiazide"]},
    {"brand_name": "Bactrim", "generic_name": "sulfamethoxazole / trimethoprim", "active_ingredients": ["sulfamethoxazole", "trimethoprim"]},
    {"brand_name": "Co-codamol", "generic_name": "codeine / acetaminophen", "active_ingredients": ["codeine", "acetaminophen"]},
    {"brand_name": "Zocor", "generic_name": "simvastatin", "active_ingredients": ["simvastatin"]},
    {"brand_name": "Cipro", "generic_name": "ciprofloxacin", "active_ingredients": ["ciprofloxacin"]},
    {"brand_name": "Zanaflex", "generic_name": "tizanidine", "active_ingredients": ["tizanidine"]}
]

INTERACTION_RULES_DATA = [
    {
        "id": "RULE-DDI-001",
        "drug_a": "warfarin",
        "drug_b": "fluconazole",
        "severity": "HIGH",
        "evidence_level": "Established - Level 1 Clinical Evidence",
        "mechanism": "Fluconazole is a potent inhibitor of CYP2C9, the primary metabolic pathway for the more potent S-warfarin enantiomer. This leads to marked accumulation of warfarin and severe coagulopathy.",
        "clinical_effect": "Dramatic elevation of INR (often > 5.0 to 10.0), significantly increasing the risk of life-threatening gastrointestinal and intracranial hemorrhage.",
        "recommendation": "Avoid combination if possible. If concurrent use is essential, empirically reduce warfarin dose by 50% upon starting fluconazole and monitor INR closely at days 2, 4, and 7.",
        "source_citation": "CPIC Guidelines / Stockley's Drug Interactions / FDA Coumadin Prescribing Information"
    },
    {
        "id": "RULE-DDI-002",
        "drug_a": "warfarin",
        "drug_b": "ibuprofen",
        "severity": "HIGH",
        "evidence_level": "Established - Level 1 Clinical Evidence",
        "mechanism": "Pharmacodynamic synergism: Ibuprofen inhibits COX-1, impairing platelet aggregation and causing gastric mucosal damage, while warfarin inhibits clotting factor synthesis.",
        "clinical_effect": "Synergistic 3- to 6-fold increase in major gastrointestinal bleeding and peptic ulceration.",
        "recommendation": "Avoid concurrent NSAID therapy in anticoagulated patients. Use acetaminophen for mild-to-moderate analgesia, or prescribe a gastroprotective PPI if NSAID use is unavoidable.",
        "source_citation": "Chest Antithrombotic Guidelines / American College of Gastroenterology"
    },
    {
        "id": "RULE-DDI-003",
        "drug_a": "lisinopril",
        "drug_b": "spironolactone",
        "severity": "HIGH",
        "evidence_level": "Established - Level 1 Clinical Evidence",
        "mechanism": "Additive potassium-sparing effect: Lisinopril inhibits angiotensin II synthesis, reducing aldosterone-mediated renal potassium excretion, while spironolactone directly blocks aldosterone receptors.",
        "clinical_effect": "Severe, life-threatening hyperkalemia (serum potassium > 6.0 mEq/L) leading to cardiac arrhythmias and arrest, especially in patients with reduced eGFR (< 60 mL/min).",
        "recommendation": "If co-prescribed for heart failure, start spironolactone at low doses (12.5-25 mg/day). Check baseline serum potassium and creatinine before initiation, then at 1 week, 4 weeks, and every 3-6 months. Discontinue potassium supplements.",
        "source_citation": "ACC/AHA Heart Failure Guidelines / KDIGO CKD Guidelines"
    },
    {
        "id": "RULE-DDI-004",
        "drug_a": "methotrexate",
        "drug_b": "amoxicillin",
        "severity": "HIGH",
        "evidence_level": "Established - Strong Case Reports & Mechanistic Evidence",
        "mechanism": "Penicillins compete with methotrexate for the organic anion transporter (OAT3) in the renal proximal tubules, significantly reducing methotrexate clearance.",
        "clinical_effect": "Elevated serum methotrexate concentrations causing pancytopenia, severe bone marrow suppression, mucositis, and acute kidney injury.",
        "recommendation": "Avoid concurrent high- or moderate-dose methotrexate and aminopenicillins. Consider alternative antimicrobial classes (e.g., macrolides, cephalosporins with monitoring) and monitor complete blood count and renal function.",
        "source_citation": "British National Formulary / Trexall FDA Label"
    },
    {
        "id": "RULE-DDI-005",
        "drug_a": "atorvastatin",
        "drug_b": "clarithromycin",
        "severity": "HIGH",
        "evidence_level": "Established - Level 1 Clinical Evidence",
        "mechanism": "Clarithromycin is a potent inhibitor of CYP3A4 and OATP1B1, dramatically increasing systemic exposure (AUC) of atorvastatin by up to 400-500%.",
        "clinical_effect": "Substantially increased risk of myopathy and fatal rhabdomyolysis with myoglobinuric acute renal failure.",
        "recommendation": "Temporarily suspend atorvastatin during the short course of clarithromycin therapy, or select an alternative antibiotic that does not inhibit CYP3A4 (e.g., azithromycin or amoxicillin).",
        "source_citation": "FDA Drug Safety Communication: Statins and Protease/Macrolide Inhibitors"
    },
    {
        "id": "RULE-DDI-006",
        "drug_a": "citalopram",
        "drug_b": "ondansetron",
        "severity": "HIGH",
        "evidence_level": "Established - Pharmacodynamic Synergism",
        "mechanism": "Both agents independently block the cardiac potassium channel (hERG), producing additive prolongation of the ventricular repolarization (QTc) interval.",
        "clinical_effect": "Cumulative QTc prolongation exceeding 500 ms, significantly heightening the risk of Torsades de Pointes (TdP) and sudden cardiac arrest.",
        "recommendation": "Avoid concurrent use. If antiemetic is required, consider alternatives with lower QTc risk. Obtain baseline ECG and monitor serum electrolytes (potassium, magnesium).",
        "source_citation": "CredibleMeds QTDrugs List / FDA Drug Safety Communication"
    },
    {
        "id": "RULE-DDI-007",
        "drug_a": "amiodarone",
        "drug_b": "digoxin",
        "severity": "HIGH",
        "evidence_level": "Established - Level 1 Clinical Evidence",
        "mechanism": "Amiodarone inhibits P-glycoprotein-mediated renal and biliary secretion of digoxin, increasing serum digoxin levels by 70% to 100%.",
        "clinical_effect": "Digoxin toxicity: severe bradycardia, heart block, visual disturbances, and lethal ventricular arrhythmias.",
        "recommendation": "Empirically reduce digoxin dose by 50% upon starting amiodarone. Measure serum digoxin level after 7 to 10 days and monitor ECG.",
        "source_citation": "Lanoxin Prescribing Information / ACC/AHA Guidelines"
    },
    {
        "id": "RULE-DDI-008",
        "drug_a": "clopidogrel",
        "drug_b": "omeprazole",
        "severity": "MEDIUM",
        "evidence_level": "Established - Moderate Clinical Evidence",
        "mechanism": "Omeprazole competitively inhibits CYP2C19, the enzyme responsible for converting clopidogrel prodrug into its active thiol metabolite.",
        "clinical_effect": "Reduced inhibition of ADP-induced platelet aggregation, potentially increasing the risk of recurrent ischemic events and stent thrombosis.",
        "recommendation": "Use a PPI with minimal CYP2C19 inhibition (e.g., pantoprazole) or an H2-receptor antagonist if gastroprotection is required during clopidogrel therapy.",
        "source_citation": "FDA Drug Safety Communication / ACCP Consensus"
    },
    {
        "id": "RULE-DDI-009",
        "drug_a": "lisinopril",
        "drug_b": "potassium chloride",
        "severity": "HIGH",
        "evidence_level": "Established - Pharmacodynamic Synergism",
        "mechanism": "ACE inhibitors reduce circulating aldosterone, impairing potassium excretion. Exogenous potassium supplements further load the extracellular compartment.",
        "clinical_effect": "Rapid development of severe hyperkalemia (> 6.5 mEq/L) causing fatal cardiac conduction defects.",
        "recommendation": "Avoid routine potassium supplementation with ACE inhibitors unless documented hypokalemia exists under continuous laboratory monitoring.",
        "source_citation": "KDIGO Guidelines / Zestril Prescribing Information"
    },
    {
        "id": "RULE-DDI-010",
        "drug_a": "apixaban",
        "drug_b": "ibuprofen",
        "severity": "HIGH",
        "evidence_level": "Established - Pharmacodynamic Synergism",
        "mechanism": "Combined platelet inhibition from NSAID COX-1 blockade with direct Factor Xa anticoagulation from apixaban.",
        "clinical_effect": "Substantial elevation in major bleeding risk, particularly gastrointestinal hemorrhage.",
        "recommendation": "Avoid concurrent use. Use acetaminophen or non-pharmacologic therapies for pain relief.",
        "source_citation": "Chest Antithrombotic Guidelines / Eliquis Prescribing Info"
    },
    {
        "id": "RULE-DDI-011",
        "drug_a": "simvastatin",
        "drug_b": "amlodipine",
        "severity": "HIGH",
        "evidence_level": "Established - Level 1 Clinical Evidence",
        "mechanism": "Amlodipine inhibits CYP3A4-mediated metabolism of simvastatin, increasing simvastatin systemic exposure by approximately 77%.",
        "clinical_effect": "Dose-dependent risk of statin-induced myopathy and rhabdomyolysis with secondary acute renal failure.",
        "recommendation": "Do not exceed simvastatin 20 mg daily when co-administered with amlodipine. Consider switching to pravastatin or rosuvastatin which do not rely on CYP3A4.",
        "source_citation": "FDA Drug Safety Communication / Simvastatin Prescribing Information"
    },
    {
        "id": "RULE-DDI-012",
        "drug_a": "ciprofloxacin",
        "drug_b": "tizanidine",
        "severity": "HIGH",
        "evidence_level": "Established - Level 1 Clinical Evidence",
        "mechanism": "Ciprofloxacin is a potent inhibitor of CYP1A2, which is responsible for the extensive first-pass hepatic metabolism of tizanidine.",
        "clinical_effect": "Up to a 10-fold increase in tizanidine AUC and a 7-fold increase in Cmax, leading to severe somnolence, profound hypotension, bradycardia, and psychomotor impairment.",
        "recommendation": "Concomitant use is strictly contraindicated. Select an alternative fluoroquinolone or non-CYP1A2 muscle relaxant.",
        "source_citation": "FDA Boxed Warning / Zanaflex Prescribing Information"
    },
    {
        "id": "RULE-DDI-013",
        "drug_a": "warfarin",
        "drug_b": "aspirin",
        "severity": "HIGH",
        "evidence_level": "Established - Level 1 Clinical Evidence",
        "mechanism": "Synergistic inhibition of hemostasis: Warfarin inhibits vitamin K-dependent clotting factor synthesis, while aspirin causes irreversible platelet cyclooxygenase-1 inhibition.",
        "clinical_effect": "Significant 3- to 5-fold increase in major and fatal gastrointestinal and intracranial bleeding events.",
        "recommendation": "Combine only when definitive clinical indication exists (e.g., mechanical heart valve plus recent acute coronary syndrome). Maintain target INR at lower end of therapeutic range and prescribe gastroprotective PPI.",
        "source_citation": "CHEST Antithrombotic Guidelines / AHA/ACC Guidelines"
    },
    {
        "id": "RULE-DDI-014",
        "drug_a": "methotrexate",
        "drug_b": "ibuprofen",
        "severity": "HIGH",
        "evidence_level": "Established - Level 1 Clinical Evidence",
        "mechanism": "NSAIDs competitively inhibit organic anion transporter (OAT1/OAT3) tubular secretion of methotrexate and reduce renal perfusion through prostaglandin synthesis inhibition.",
        "clinical_effect": "Severe methotrexate accumulation causing life-threatening bone marrow suppression, pancytopenia, severe stomatitis, and acute renal failure.",
        "recommendation": "Avoid concurrent NSAID administration with moderate-to-high dose methotrexate. If low-dose methotrexate is used for rheumatoid arthritis, monitor CBC, renal function, and liver enzymes closely.",
        "source_citation": "Trexall Prescribing Information / EULAR Guidelines"
    }
]

DUPLICATE_THERAPY_RULES_DATA = [
    {
        "id": "RULE-DUP-001",
        "target_identifier": "acetaminophen",
        "rule_type": "EXACT_INGREDIENT",
        "severity": "HIGH",
        "risk_description": "Duplicate active ingredient: The patient is prescribed multiple medications containing acetaminophen (paracetamol). Combined daily dosing may exceed the safe threshold of 4,000 mg/24h.",
        "recommendation": "Calculate cumulative 24-hour acetaminophen intake across all brand and combination products. Advise patient against simultaneous OTC use to prevent acute hepatotoxicity.",
        "source_citation": "FDA Acetaminophen Dosing Guidance / American Liver Foundation"
    },
    {
        "id": "RULE-DUP-002",
        "target_identifier": "ibuprofen",
        "rule_type": "EXACT_INGREDIENT",
        "severity": "HIGH",
        "risk_description": "Duplicate active ingredient: Multiple prescriptions containing ibuprofen detected (e.g. Advil and Motrin).",
        "recommendation": "Consolidate into a single prescription with clearly specified dose and frequency to prevent NSAID overdose and acute renal or gastrointestinal injury.",
        "source_citation": "American College of Rheumatology NSAID Guidelines"
    },
    {
        "id": "RULE-DUP-003",
        "target_identifier": "metformin",
        "rule_type": "EXACT_INGREDIENT",
        "severity": "HIGH",
        "risk_description": "Duplicate active ingredient: Metformin is present both as a single agent (e.g., Glucophage) and within a fixed-dose combination product (e.g., Janumet).",
        "recommendation": "Evaluate total daily metformin dose across all medications. Avoid exceeding 2,000 to 2,550 mg daily, and monitor renal function.",
        "source_citation": "American Diabetes Association (ADA) Standards of Care"
    },
    {
        "id": "RULE-DUP-004",
        "target_identifier": "NSAID",
        "rule_type": "THERAPEUTIC_CLASS",
        "severity": "MEDIUM",
        "risk_description": "Therapeutic class duplication: Co-prescription of two distinct systemic NSAIDs (e.g. ibuprofen and naproxen). There is no demonstrated additional therapeutic efficacy but an exponential increase in adverse events.",
        "recommendation": "Discontinue one NSAID. Concurrent use provides no additive analgesia and significantly increases gastric perforation, ulceration, and renal insufficiency.",
        "source_citation": "American College of Gastroenterology / NICE Guidelines"
    },
    {
        "id": "RULE-DUP-005",
        "target_identifier": "amoxicillin",
        "rule_type": "EXACT_INGREDIENT",
        "severity": "HIGH",
        "risk_description": "Duplicate active ingredient: Co-prescription of single-agent amoxicillin and combination amoxicillin/clavulanate (Augmentin).",
        "recommendation": "Consolidate into a single appropriate antimicrobial regimen to avoid excessive beta-lactam dosing and adverse events.",
        "source_citation": "Infectious Diseases Society of America (IDSA) Guidelines"
    },
    {
        "id": "RULE-DUP-006",
        "target_identifier": "ACE Inhibitor",
        "rule_type": "THERAPEUTIC_CLASS",
        "severity": "MEDIUM",
        "risk_description": "Therapeutic class duplication: Co-prescription of multiple ACE inhibitors (e.g. lisinopril and enalapril or ramipril).",
        "recommendation": "Discontinue redundant ACE inhibitor agent. Dual ACE inhibition confers no clinical benefit and drastically increases risks of severe hypotension, syncope, and hyperkalemia.",
        "source_citation": "AHA/ACC Hypertension Guidelines"
    }
]

RENAL_RISK_RULES_DATA = [
    {
        "id": "RULE-RENAL-001",
        "generic_name": "metformin",
        "threshold_type": "eGFR",
        "threshold_operator": "<",
        "threshold_value": 30.0,
        "unit": "mL/min/1.73m2",
        "severity": "HIGH",
        "risk_type": "CONTRAINDICATION",
        "clinical_guidance": "Metformin is strictly contraindicated in patients with eGFR < 30 mL/min/1.73m2 due to high risk of life-threatening metformin-associated lactic acidosis (MALA).",
        "source_citation": "FDA Drug Safety Communication: Revised warnings regarding use of metformin in patients with reduced kidney function"
    },
    {
        "id": "RULE-RENAL-002",
        "generic_name": "metformin",
        "threshold_type": "eGFR",
        "threshold_operator": "<",
        "threshold_value": 45.0,
        "unit": "mL/min/1.73m2",
        "severity": "MEDIUM",
        "risk_type": "DOSE_REDUCTION",
        "clinical_guidance": "In patients with eGFR 30 to 44 mL/min/1.73m2, initiation of metformin is not recommended. If already taking metformin, evaluate risk/benefit and limit maximum dose to 1000 mg daily with eGFR monitoring every 3 months.",
        "source_citation": "KDIGO Clinical Practice Guideline for Diabetes Management in CKD"
    },
    {
        "id": "RULE-RENAL-003",
        "generic_name": "enoxaparin",
        "threshold_type": "CrCl",
        "threshold_operator": "<",
        "threshold_value": 30.0,
        "unit": "mL/min",
        "severity": "HIGH",
        "risk_type": "DOSE_REDUCTION",
        "clinical_guidance": "Enoxaparin undergoes renal elimination. In severe renal impairment (CrCl < 30 mL/min), systemic clearance is decreased by 30%. Dose adjustment is required (e.g., reduce therapeutic dose to 1 mg/kg once daily, prophylaxis to 30 mg once daily) to avoid major hemorrhage.",
        "source_citation": "Lovenox FDA Prescribing Information / CHEST Guidelines"
    },
    {
        "id": "RULE-RENAL-004",
        "generic_name": "spironolactone",
        "threshold_type": "eGFR",
        "threshold_operator": "<",
        "threshold_value": 30.0,
        "unit": "mL/min/1.73m2",
        "severity": "HIGH",
        "risk_type": "CONTRAINDICATION",
        "clinical_guidance": "Spironolactone is contraindicated in patients with severe renal impairment (eGFR < 30 mL/min/1.73m2) or serum creatinine > 2.5 mg/dL due to the imminent risk of fatal hyperkalemia.",
        "source_citation": "Aldactone Prescribing Information / ACC/AHA Heart Failure Guidelines"
    },
    {
        "id": "RULE-RENAL-005",
        "generic_name": "ibuprofen",
        "threshold_type": "eGFR",
        "threshold_operator": "<",
        "threshold_value": 30.0,
        "unit": "mL/min/1.73m2",
        "severity": "HIGH",
        "risk_type": "CONTRAINDICATION",
        "clinical_guidance": "Systemic NSAIDs inhibit renal prostaglandin synthesis, abolishing compensatory afferent arteriolar vasodilation. Strongly contraindicated in advanced CKD (eGFR < 30 mL/min) due to acute-on-chronic kidney injury.",
        "source_citation": "KDIGO CKD Evaluation & Management Guidelines"
    },
    {
        "id": "RULE-RENAL-006",
        "generic_name": "gabapentin",
        "threshold_type": "eGFR",
        "threshold_operator": "<",
        "threshold_value": 60.0,
        "unit": "mL/min/1.73m2",
        "severity": "MEDIUM",
        "risk_type": "DOSE_REDUCTION",
        "clinical_guidance": "Gabapentin is eliminated solely by renal excretion. Dose reduction is mandatory when eGFR < 60 mL/min to prevent toxic drug accumulation, profound somnolence, and respiratory depression.",
        "source_citation": "Neurontin FDA Prescribing Information"
    },
    {
        "id": "RULE-RENAL-007",
        "generic_name": "methotrexate",
        "threshold_type": "eGFR",
        "threshold_operator": "<",
        "threshold_value": 30.0,
        "unit": "mL/min/1.73m2",
        "severity": "HIGH",
        "risk_type": "CONTRAINDICATION",
        "clinical_guidance": "Methotrexate is predominantly cleared by renal excretion. Severe renal impairment (eGFR < 30 mL/min) impairs clearance by >70%, leading to life-threatening accumulation, acute pancytopenia, bone marrow suppression, and multi-organ failure.",
        "source_citation": "KDIGO CKD Guidelines / Trexall FDA Prescribing Information"
    }
]

CONTRAINDICATION_RULES_DATA = [
    {
        "id": "RULE-CONTRA-001",
        "generic_name": "warfarin",
        "factor_name": "Peptic Ulcer",
        "factor_type": "CONDITION",
        "severity": "HIGH",
        "risk_description": "Active or recent peptic ulcer disease is an absolute contraindication to therapeutic anticoagulation with warfarin due to excessive risk of catastrophic gastrointestinal hemorrhage.",
        "recommendation": "Withhold warfarin until peptic ulcer lesion is completely healed and hemostasis is confirmed endoscopically. Consult gastroenterologist and hematologist.",
        "source_citation": "American College of Chest Physicians Antithrombotic Guidelines"
    },
    {
        "id": "RULE-CONTRA-002",
        "generic_name": "ibuprofen",
        "factor_name": "Peptic Ulcer",
        "factor_type": "CONDITION",
        "severity": "HIGH",
        "risk_description": "NSAIDs cause direct mucosal irritation and inhibit cytoprotective gastric prostaglandins, predisposing to recurrent ulceration and perforation in patients with peptic ulcer disease.",
        "recommendation": "Avoid all non-selective NSAIDs. Use non-ulcerogenic analgesics such as acetaminophen.",
        "source_citation": "American College of Gastroenterology Ulcer Prevention Guidelines"
    },
    {
        "id": "RULE-CONTRA-003",
        "generic_name": "propranolol",
        "factor_name": "Asthma",
        "factor_type": "CONDITION",
        "severity": "HIGH",
        "risk_description": "Non-selective beta-blockers antagonize beta-2 receptors in bronchial smooth muscle, triggering severe, potentially fatal bronchospasm and refractory asthma exacerbations.",
        "recommendation": "Contraindicated in asthma or history of bronchospastic disease. If beta-blockade is essential for cardiovascular indications, consider highly cardioselective agents (e.g. bisoprolol, metoprolol succinate) with extreme caution.",
        "source_citation": "Global Initiative for Asthma (GINA) Guidelines"
    },
    {
        "id": "RULE-CONTRA-004",
        "generic_name": "methotrexate",
        "factor_name": "Pregnancy",
        "factor_type": "PREGNANCY",
        "severity": "HIGH",
        "risk_description": "Methotrexate is a potent folic acid antagonist that causes congenital malformations (aminopterin syndrome), severe craniofacial abnormalities, and fetal death.",
        "recommendation": "Contraindicated in pregnant women. Must obtain negative pregnancy test prior to initiation and ensure effective dual contraception throughout therapy and for at least 6 months after.",
        "source_citation": "FDA Black Box Warning / Teratology Society"
    },
    {
        "id": "RULE-CONTRA-005",
        "generic_name": "lisinopril",
        "factor_name": "Pregnancy",
        "factor_type": "PREGNANCY",
        "severity": "HIGH",
        "risk_description": "Drugs acting directly on the renin-angiotensin system during the second and third trimesters cause fetal hypotension, oligohydramnios, neonatal skull hypoplasia, and anuria/death.",
        "recommendation": "Discontinue lisinopril immediately upon detection of pregnancy. Switch to pregnancy-safe antihypertensives such as labetalol, nifedipine, or methyldopa.",
        "source_citation": "FDA Boxed Warning: Fetal Toxicity / ACOG Guidelines"
    },
    {
        "id": "RULE-CONTRA-006",
        "generic_name": "amoxicillin",
        "factor_name": "Penicillin",
        "factor_type": "ALLERGY",
        "severity": "HIGH",
        "risk_description": "Amoxicillin shares the core beta-lactam bicyclic ring structure of penicillin. Administering to a penicillin-allergic patient carries a high risk of IgE-mediated anaphylaxis and angioedema.",
        "recommendation": "Contraindicated in verified penicillin allergy. Select non-beta-lactam antimicrobials (e.g. macrolides, fluoroquinolones, or doxycycline) or perform allergy skin testing if first-line therapy is critical.",
        "source_citation": "Joint Task Force on Practice Parameters: Drug Allergy Practice Parameter"
    }
]

def seed_reference_data(db: Session):
    """Seed all verified reference catalogue tables, ensuring new entries are inserted."""
    # 1. Medicines
    existing_meds = {m.generic_name.lower().strip() for m in db.query(MedicineCatalogue).all()}
    for med in MEDICINE_CATALOGUE_DATA:
        if med["generic_name"].lower().strip() not in existing_meds:
            db.add(MedicineCatalogue(**med))
    
    # 2. Brand Mappings
    existing_brands = {bm.brand_name.lower().strip() for bm in db.query(BrandMapping).all()}
    for bm in BRAND_MAPPINGS_DATA:
        if bm["brand_name"].lower().strip() not in existing_brands:
            db.add(BrandMapping(**bm))
            
    # 3. DDI Rules
    existing_rules = {r.id for r in db.query(InteractionRule).all()}
    for rule in INTERACTION_RULES_DATA:
        if rule["id"] not in existing_rules:
            db.add(InteractionRule(**rule))
            
    # 4. Duplicate Therapy Rules
    existing_dups = {r.id for r in db.query(DuplicateTherapyRule).all()}
    for rule in DUPLICATE_THERAPY_RULES_DATA:
        if rule["id"] not in existing_dups:
            db.add(DuplicateTherapyRule(**rule))
            
    # 5. Renal Risk Rules
    existing_renals = {r.id for r in db.query(RenalRiskRule).all()}
    for rule in RENAL_RISK_RULES_DATA:
        if rule["id"] not in existing_renals:
            db.add(RenalRiskRule(**rule))
            
    # 6. Contraindication Rules
    existing_contras = {r.id for r in db.query(ContraindicationRule).all()}
    for rule in CONTRAINDICATION_RULES_DATA:
        if rule["id"] not in existing_contras:
            db.add(ContraindicationRule(**rule))

    # 7. Metadata
    if db.query(DatasetMetadata).count() == 0:
        db.add(DatasetMetadata(
            name="Authoritative Clinical Medication Reference Rules",
            version="v1.4",
            description="Curated high-specificity clinical rule set for DDIs, renal risk thresholds, duplicate therapies, and contraindications.",
            record_count=len(MEDICINE_CATALOGUE_DATA) + len(INTERACTION_RULES_DATA) + len(RENAL_RISK_RULES_DATA),
            is_official_challenge=False
        ))
    db.commit()
