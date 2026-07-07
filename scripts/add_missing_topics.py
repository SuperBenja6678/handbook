"""
Add ~120 missing disease topics to master-topics.json.
Run this first, then use batch_generate.py to generate the entries.
"""
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
MASTER_PATH = PROJECT_ROOT / "data" / "master-topics.json"

# Load existing
master = json.loads(MASTER_PATH.read_text(encoding="utf-8"))
existing_titles = {t["title"] for t in master["topics"]}

# ============================================================
# MISSING TOPICS — organised by system
# ============================================================
NEW_TOPICS = [
    # ---- CARDIOVASCULAR ----
    {"title": "TIA (Transient Ischaemic Attack)", "system": "Neurology", "subSystem": "Stroke", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "AV Block / Heart Block (1st, 2nd, 3rd Degree)", "system": "Cardiovascular", "subSystem": "Arrhythmia", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Cardiogenic Shock", "system": "Cardiovascular", "subSystem": "Shock", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Long QT Syndrome", "system": "Cardiovascular", "subSystem": "Arrhythmia", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Brugada Syndrome", "system": "Cardiovascular", "subSystem": "Arrhythmia", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Takotsubo Cardiomyopathy", "system": "Cardiovascular", "subSystem": "Cardiomyopathy", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Wolff-Parkinson-White Syndrome", "system": "Cardiovascular", "subSystem": "Arrhythmia", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Constrictive Pericarditis", "system": "Cardiovascular", "subSystem": "Pericardial disease", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Hyperlipidaemia & Familial Hypercholesterolaemia", "system": "Cardiovascular", "subSystem": "Risk factors", "acuity": "CHRONIC", "priority": "WEEK_3"},

    # ---- RESPIRATORY ----
    {"title": "Cystic Fibrosis — Overview", "system": "Respiratory", "subSystem": "Suppurative", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Allergic Rhinitis", "system": "ENT", "subSystem": "Nasal", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Acute Sinusitis", "system": "ENT", "subSystem": "Sinonasal", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Vocal Cord Dysfunction", "system": "Respiratory", "subSystem": "Upper airway", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Hypersensitivity Pneumonitis", "system": "Respiratory", "subSystem": "ILD", "acuity": "CHRONIC", "priority": "WEEK_5"},

    # ---- GASTROENTEROLOGY / HEPATOLOGY ----
    {"title": "Acute Hepatitis (Viral — Hep A & E)", "system": "Hepatology & Pancreaticobiliary", "subSystem": "Viral hepatitis", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Alcoholic Hepatitis", "system": "Hepatology & Pancreaticobiliary", "subSystem": "Alcoholic liver", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Volvulus", "system": "General Surgery", "subSystem": "Obstruction", "acuity": "EMERGENCY", "priority": "WEEK_2"},
    {"title": "Intussusception", "system": "General Surgery", "subSystem": "Obstruction", "acuity": "EMERGENCY", "priority": "WEEK_4"},
    {"title": "Haemorrhoids", "system": "General Surgery", "subSystem": "Anorectal", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Anal Fissure", "system": "General Surgery", "subSystem": "Anorectal", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Perianal Abscess & Fistula", "system": "General Surgery", "subSystem": "Anorectal", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Barrett's Oesophagus", "system": "Gastroenterology", "subSystem": "Upper GI", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Achalasia", "system": "Gastroenterology", "subSystem": "Upper GI", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Ischaemic Colitis", "system": "Gastroenterology", "subSystem": "Lower GI", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Microscopic Colitis", "system": "Gastroenterology", "subSystem": "Lower GI", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Wilson's Disease", "system": "Hepatology & Pancreaticobiliary", "subSystem": "Metabolic liver", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Budd-Chiari Syndrome", "system": "Hepatology & Pancreaticobiliary", "subSystem": "Vascular liver", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Liver Abscess", "system": "Hepatology & Pancreaticobiliary", "subSystem": "Infection", "acuity": "URGENT", "priority": "WEEK_4"},

    # ---- NEPHROLOGY / UROLOGY ----
    {"title": "SIADH (Syndrome of Inappropriate ADH)", "system": "Nephrology & Electrolytes", "subSystem": "Electrolyte", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Diabetes Insipidus", "system": "Endocrinology", "subSystem": "Pituitary", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Acute Urinary Retention", "system": "Urology", "subSystem": "Emergency", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Rhabdomyolysis", "system": "Nephrology & Electrolytes", "subSystem": "AKI", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Prostate Cancer", "system": "Urology", "subSystem": "Malignancy", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Benign Prostatic Hyperplasia (BPH)", "system": "Urology", "subSystem": "Lower urinary tract", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Epididymo-Orchitis", "system": "Urology", "subSystem": "Scrotal", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Testicular Cancer", "system": "Urology", "subSystem": "Malignancy", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Prostatitis", "system": "Urology", "subSystem": "Infection", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Fournier's Gangrene", "system": "Urology", "subSystem": "Emergency", "acuity": "EMERGENCY", "priority": "WEEK_4"},
    {"title": "Polycystic Kidney Disease (ADPKD)", "system": "Nephrology & Electrolytes", "subSystem": "CKD", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Renal Artery Stenosis", "system": "Nephrology & Electrolytes", "subSystem": "Vascular", "acuity": "CHRONIC", "priority": "WEEK_5"},

    # ---- NEUROLOGY ----
    {"title": "Cluster Headache", "system": "Neurology", "subSystem": "Headache", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Tension Headache", "system": "Neurology", "subSystem": "Headache", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Cerebral Venous Sinus Thrombosis", "system": "Neurology", "subSystem": "Stroke", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Cervical Artery Dissection", "system": "Neurology", "subSystem": "Stroke", "acuity": "EMERGENCY", "priority": "WEEK_4"},
    {"title": "Wernicke-Korsakoff Syndrome", "system": "Neurology", "subSystem": "Metabolic", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Peripheral Neuropathy — Approach", "system": "Neurology", "subSystem": "Neuropathy", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Vertigo — Approach (BPPV, Labyrinthitis, Ménière's)", "system": "Neurology", "subSystem": "Vertigo", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Carpal Tunnel Syndrome", "system": "Neurology", "subSystem": "Entrapment", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Essential Tremor", "system": "Neurology", "subSystem": "Movement", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Functional Neurological Disorder", "system": "Neurology", "subSystem": "Functional", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Transverse Myelitis", "system": "Neurology", "subSystem": "Spinal cord", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Normal Pressure Hydrocephalus", "system": "Neurology", "subSystem": "Cognitive", "acuity": "CHRONIC", "priority": "WEEK_5"},

    # ---- ENDOCRINOLOGY ----
    {"title": "Pituitary Apoplexy", "system": "Endocrinology", "subSystem": "Pituitary", "acuity": "EMERGENCY", "priority": "WEEK_4"},
    {"title": "Hypopituitarism", "system": "Endocrinology", "subSystem": "Pituitary", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Sheehan Syndrome", "system": "Endocrinology", "subSystem": "Pituitary", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "MEN Syndromes (MEN1 & MEN2)", "system": "Endocrinology", "subSystem": "Syndromic", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Thyroid Cancer & Thyroid Nodule Workup", "system": "Endocrinology", "subSystem": "Thyroid", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Klinefelter Syndrome", "system": "Endocrinology", "subSystem": "Genetic", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Turner Syndrome", "system": "Endocrinology", "subSystem": "Genetic", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Gynaecomastia", "system": "Endocrinology", "subSystem": "Reproductive", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Erectile Dysfunction", "system": "Endocrinology", "subSystem": "Reproductive", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Congenital Adrenal Hyperplasia", "system": "Endocrinology", "subSystem": "Adrenal", "acuity": "CHRONIC", "priority": "WEEK_5"},

    # ---- HAEMATOLOGY ----
    {"title": "ALL (Acute Lymphoblastic Leukaemia)", "system": "Haematology", "subSystem": "Leukaemia", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "CML (Chronic Myeloid Leukaemia)", "system": "Haematology", "subSystem": "Leukaemia", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "TTP / HUS (Thrombotic Thrombocytopenic Purpura / Haemolytic Uraemic Syndrome)", "system": "Haematology", "subSystem": "Microangiopathy", "acuity": "EMERGENCY", "priority": "WEEK_2"},
    {"title": "Myelodysplastic Syndrome (MDS)", "system": "Haematology", "subSystem": "Bone marrow", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Polycythaemia Vera", "system": "Haematology", "subSystem": "Myeloproliferative", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Essential Thrombocythaemia", "system": "Haematology", "subSystem": "Myeloproliferative", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Myelofibrosis", "system": "Haematology", "subSystem": "Myeloproliferative", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Autoimmune Haemolytic Anaemia", "system": "Haematology", "subSystem": "Anaemia", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Aplastic Anaemia", "system": "Haematology", "subSystem": "Anaemia", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "G6PD Deficiency", "system": "Haematology", "subSystem": "Anaemia", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Hereditary Spherocytosis", "system": "Haematology", "subSystem": "Anaemia", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Transfusion Reactions", "system": "Haematology", "subSystem": "Transfusion", "acuity": "EMERGENCY", "priority": "WEEK_2"},
    {"title": "Amyloidosis", "system": "Haematology", "subSystem": "Plasma cell", "acuity": "CHRONIC", "priority": "WEEK_5"},

    # ---- INFECTIOUS DISEASES ----
    {"title": "COVID-19 — Acute Management", "system": "Infectious Diseases", "subSystem": "Viral", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Influenza", "system": "Infectious Diseases", "subSystem": "Viral", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Infectious Mononucleosis (EBV / Glandular Fever)", "system": "Infectious Diseases", "subSystem": "Viral", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Lyme Disease", "system": "Infectious Diseases", "subSystem": "Vector-borne", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Dengue", "system": "Infectious Diseases", "subSystem": "Tropical", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Measles", "system": "Infectious Diseases", "subSystem": "Viral", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Mumps", "system": "Infectious Diseases", "subSystem": "Viral", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Rubella", "system": "Infectious Diseases", "subSystem": "Viral", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Tetanus", "system": "Infectious Diseases", "subSystem": "Bacterial", "acuity": "EMERGENCY", "priority": "WEEK_5"},
    {"title": "Discitis / Vertebral Osteomyelitis", "system": "Infectious Diseases", "subSystem": "MSK infection", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Invasive Candidiasis", "system": "Infectious Diseases", "subSystem": "Fungal", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Invasive Aspergillosis", "system": "Infectious Diseases", "subSystem": "Fungal", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "CMV Infection", "system": "Infectious Diseases", "subSystem": "Viral", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Cryptococcal Meningitis", "system": "Infectious Diseases", "subSystem": "Fungal", "acuity": "URGENT", "priority": "WEEK_5"},

    # ---- RHEUMATOLOGY ----
    {"title": "Psoriatic Arthritis", "system": "Rheumatology & MSK", "subSystem": "Seronegative", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Sjögren Syndrome", "system": "Rheumatology & MSK", "subSystem": "Connective tissue", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Behçet Disease", "system": "Rheumatology & MSK", "subSystem": "Vasculitis", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Dermatomyositis / Polymyositis", "system": "Rheumatology & MSK", "subSystem": "Myositis", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Fibromyalgia", "system": "Rheumatology & MSK", "subSystem": "Chronic pain", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Pseudogout (CPPD)", "system": "Rheumatology & MSK", "subSystem": "Crystal", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Kawasaki Disease", "system": "Rheumatology & MSK", "subSystem": "Vasculitis", "acuity": "EMERGENCY", "priority": "WEEK_4"},
    {"title": "IgA Vasculitis (Henoch-Schönlein Purpura)", "system": "Rheumatology & MSK", "subSystem": "Vasculitis", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Polyarteritis Nodosa (PAN)", "system": "Rheumatology & MSK", "subSystem": "Vasculitis", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Takayasu Arteritis", "system": "Rheumatology & MSK", "subSystem": "Vasculitis", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Goodpasture Syndrome / Anti-GBM Disease", "system": "Rheumatology & MSK", "subSystem": "Vasculitis", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Osteomalacia", "system": "Rheumatology & MSK", "subSystem": "Metabolic bone", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Paget Disease of Bone", "system": "Rheumatology & MSK", "subSystem": "Metabolic bone", "acuity": "CHRONIC", "priority": "WEEK_5"},

    # ---- DERMATOLOGY ----
    {"title": "Squamous Cell Carcinoma (SCC)", "system": "Dermatology", "subSystem": "Malignancy", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Acne Vulgaris & Rosacea", "system": "Dermatology", "subSystem": "Inflammatory", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Scabies", "system": "Dermatology", "subSystem": "Parasitic", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Fungal Skin Infections (Tinea / Dermatophytosis)", "system": "Dermatology", "subSystem": "Fungal", "acuity": "ROUTINE", "priority": "WEEK_5"},
    {"title": "Pressure Ulcers", "system": "Dermatology", "subSystem": "Ulcer", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Herpes Simplex (Oral & Genital)", "system": "Dermatology", "subSystem": "Viral", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Drug Eruptions & DRESS Syndrome", "system": "Dermatology", "subSystem": "Drug reaction", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Pyoderma Gangrenosum", "system": "Dermatology", "subSystem": "Neutrophilic", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Hidradenitis Suppurativa", "system": "Dermatology", "subSystem": "Inflammatory", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Lichen Planus", "system": "Dermatology", "subSystem": "Inflammatory", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Erythema Nodosum", "system": "Dermatology", "subSystem": "Inflammatory", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Erythema Multiforme", "system": "Dermatology", "subSystem": "Reactive", "acuity": "URGENT", "priority": "WEEK_5"},

    # ---- PSYCHIATRY ----
    {"title": "PTSD (Post-Traumatic Stress Disorder)", "system": "Psychiatry", "subSystem": "Anxiety", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Panic Disorder", "system": "Psychiatry", "subSystem": "Anxiety", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "OCD (Obsessive-Compulsive Disorder)", "system": "Psychiatry", "subSystem": "Anxiety", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Personality Disorders — Borderline (EUPD)", "system": "Psychiatry", "subSystem": "Personality", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Postpartum Depression & Psychosis", "system": "Psychiatry", "subSystem": "Perinatal", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Serotonin Syndrome", "system": "Clinical Pharmacology", "subSystem": "Drug reaction", "acuity": "EMERGENCY", "priority": "WEEK_2"},
    {"title": "Neuroleptic Malignant Syndrome", "system": "Clinical Pharmacology", "subSystem": "Drug reaction", "acuity": "EMERGENCY", "priority": "WEEK_2"},
    {"title": "Lithium Toxicity & Monitoring", "system": "Clinical Pharmacology", "subSystem": "Drug monograph", "acuity": "EMERGENCY", "priority": "WEEK_4"},
    {"title": "ADHD in Adults", "system": "Psychiatry", "subSystem": "Neurodevelopmental", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Autism Spectrum Disorder in Adults", "system": "Psychiatry", "subSystem": "Neurodevelopmental", "acuity": "CHRONIC", "priority": "WEEK_5"},

    # ---- OBSTETRICS & GYNAECOLOGY ----
    {"title": "Endometrial Cancer", "system": "Gynaecology", "subSystem": "Malignancy", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Uterine Fibroids", "system": "Gynaecology", "subSystem": "Benign", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Ovarian Torsion", "system": "Gynaecology", "subSystem": "Emergency", "acuity": "EMERGENCY", "priority": "WEEK_4"},
    {"title": "Placenta Praevia", "system": "Obstetrics", "subSystem": "Obstetric emergency", "acuity": "EMERGENCY", "priority": "WEEK_4"},
    {"title": "Placental Abruption", "system": "Obstetrics", "subSystem": "Obstetric emergency", "acuity": "EMERGENCY", "priority": "WEEK_4"},
    {"title": "IUGR (Intrauterine Growth Restriction)", "system": "Obstetrics", "subSystem": "Fetal medicine", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Molar Pregnancy (Gestational Trophoblastic Disease)", "system": "Gynaecology", "subSystem": "Early pregnancy", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Mastitis & Breastfeeding Issues", "system": "Obstetrics", "subSystem": "Postpartum", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Shoulder Dystocia", "system": "Obstetrics", "subSystem": "Labour emergency", "acuity": "EMERGENCY", "priority": "WEEK_4"},
    {"title": "Cord Prolapse", "system": "Obstetrics", "subSystem": "Labour emergency", "acuity": "EMERGENCY", "priority": "WEEK_4"},
    {"title": "Amenorrhoea — Primary & Secondary", "system": "Gynaecology", "subSystem": "Menstrual", "acuity": "CHRONIC", "priority": "WEEK_5"},

    # ---- PAEDIATRICS ----
    {"title": "Childhood Vaccination Schedule", "system": "Paediatrics", "subSystem": "Prevention", "acuity": "ROUTINE", "priority": "WEEK_5"},
    {"title": "Congenital Heart Disease — Overview", "system": "Paediatrics", "subSystem": "Cardiology", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Pyloric Stenosis", "system": "Paediatrics", "subSystem": "Surgical", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Hirschsprung Disease", "system": "Paediatrics", "subSystem": "Surgical", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "SUFE (Slipped Upper Femoral Epiphysis)", "system": "Paediatrics", "subSystem": "Orthopaedic", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Perthes Disease", "system": "Paediatrics", "subSystem": "Orthopaedic", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Cerebral Palsy", "system": "Paediatrics", "subSystem": "Neurology", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "NEC (Necrotising Enterocolitis)", "system": "Paediatrics", "subSystem": "Neonatal", "acuity": "EMERGENCY", "priority": "WEEK_4"},
    {"title": "Neonatal Sepsis", "system": "Paediatrics", "subSystem": "Neonatal", "acuity": "EMERGENCY", "priority": "WEEK_4"},
    {"title": "Common Genetic Syndromes (Down, Marfan, Ehlers-Danlos, NF1, DiGeorge)", "system": "Paediatrics", "subSystem": "Genetics", "acuity": "CHRONIC", "priority": "WEEK_5"},

    # ---- ENT ----
    {"title": "Tonsillitis & Pharyngitis", "system": "ENT", "subSystem": "Throat", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Head & Neck Cancer — Overview", "system": "ENT", "subSystem": "Malignancy", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Sudden Sensorineural Hearing Loss", "system": "ENT", "subSystem": "Ear", "acuity": "EMERGENCY", "priority": "WEEK_4"},
    {"title": "Cholesteatoma", "system": "ENT", "subSystem": "Ear", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Salivary Gland Disease (Sialadenitis, Stones, Tumours)", "system": "ENT", "subSystem": "Salivary", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Acoustic Neuroma (Vestibular Schwannoma)", "system": "ENT", "subSystem": "Ear", "acuity": "CHRONIC", "priority": "WEEK_5"},

    # ---- OPHTHALMOLOGY ----
    {"title": "Diabetic Retinopathy", "system": "Ophthalmology", "subSystem": "Retina", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Macular Degeneration (AMD)", "system": "Ophthalmology", "subSystem": "Retina", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Anterior Uveitis / Iritis", "system": "Ophthalmology", "subSystem": "Uveitis", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Conjunctivitis", "system": "Ophthalmology", "subSystem": "Infection", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Optic Neuritis", "system": "Ophthalmology", "subSystem": "Neuro-ophthalmology", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Retinal Vein Occlusion (CRVO / BRVO)", "system": "Ophthalmology", "subSystem": "Retina", "acuity": "URGENT", "priority": "WEEK_4"},

    # ---- TOXICOLOGY ----
    {"title": "Benzodiazepine Overdose", "system": "Emergency Medicine", "subSystem": "Toxicology", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Beta Blocker & Calcium Channel Blocker Overdose", "system": "Emergency Medicine", "subSystem": "Toxicology", "acuity": "EMERGENCY", "priority": "WEEK_4"},
    {"title": "Digoxin Toxicity", "system": "Emergency Medicine", "subSystem": "Toxicology", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Ethylene Glycol & Methanol Poisoning", "system": "Emergency Medicine", "subSystem": "Toxicology", "acuity": "EMERGENCY", "priority": "WEEK_4"},
    {"title": "Iron Poisoning", "system": "Emergency Medicine", "subSystem": "Toxicology", "acuity": "EMERGENCY", "priority": "WEEK_5"},

    # ---- ONCOLOGY ----
    {"title": "Brain Tumours — Primary & Metastatic", "system": "Oncology", "subSystem": "CNS", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Mesothelioma", "system": "Respiratory", "subSystem": "Malignancy", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Cancer of Unknown Primary (CUP)", "system": "Oncology", "subSystem": "Syndromic", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Paraneoplastic Syndromes", "system": "Oncology", "subSystem": "Syndromic", "acuity": "URGENT", "priority": "WEEK_5"},

    # ---- ENVIRONMENTAL / EMERGENCY ----
    {"title": "Hypothermia", "system": "Emergency Medicine", "subSystem": "Environmental", "acuity": "EMERGENCY", "priority": "WEEK_2"},
    {"title": "Heat Stroke & Heat Exhaustion", "system": "Emergency Medicine", "subSystem": "Environmental", "acuity": "EMERGENCY", "priority": "WEEK_4"},
    {"title": "Drowning / Near-Drowning", "system": "Emergency Medicine", "subSystem": "Environmental", "acuity": "EMERGENCY", "priority": "WEEK_4"},
    {"title": "Snake Bites & Insect Stings", "system": "Emergency Medicine", "subSystem": "Environmental", "acuity": "EMERGENCY", "priority": "WEEK_5"},

    # ---- MISCELLANEOUS ----
    {"title": "Acute Porphyria", "system": "Haematology", "subSystem": "Metabolic", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Neurofibromatosis Type 1 & 2", "system": "Neurology", "subSystem": "Genetic", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Tuberous Sclerosis", "system": "Neurology", "subSystem": "Genetic", "acuity": "CHRONIC", "priority": "WEEK_5"},
]

# Filter out duplicates
actually_new = []
for topic in NEW_TOPICS:
    if topic["title"] not in existing_titles:
        actually_new.append(topic)
        existing_titles.add(topic["title"])
    else:
        print(f"SKIP (already exists): {topic['title']}")

print(f"\nTotal new topics to add: {len(actually_new)}")

if actually_new:
    master["topics"].extend(actually_new)
    master["count"] = len(master["topics"])

    # Save
    MASTER_PATH.write_text(
        json.dumps(master, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Updated master-topics.json: {master['count']} total topics")
    print(f"Saved -> {MASTER_PATH}")

    # Print new topics for user
    print("\nNew topics added:")
    for t in actually_new:
        print(f"  [{t['priority']}] {t['title']} ({t['system']} / {t['subSystem']})")
else:
    print("No new topics to add — all already present.")
