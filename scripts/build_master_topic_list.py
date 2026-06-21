"""
Master topic list for the personal clinical handbook.

REVISED v2 — incorporates gaps identified after MVP testing:
  - Death verification & certification (FY1 critical)
  - Needlestick / bloodborne virus exposure
  - Consent & capacity (Mental Capacity Act, Gillick)
  - Adult safeguarding
  - Handover / SBAR
  - Common ward calls (agitated patient, line pulled, refusing treatment)
  - Drug monographs (warfarin, insulin, opioids, gentamicin, vancomycin, etc.)
  - Paediatric emergencies (anaphylaxis, septic child, meningococcal)
  - Blood transfusion administration
  - Procedural skills (IM/SC injection, ECG, drains, stoma care)
  - Post-operative complications overview

Saved to /home/z/my-project/data/master-topics.json for batch generation.

Each topic has:
  - title: the topic name (used as the generation prompt)
  - system: which body system / specialty
  - subSystem: more specific grouping
  - acuity: EMERGENCY / URGENT / ROUTINE / CHRONIC
  - priority: WEEK_1 / WEEK_2 / WEEK_3 / WEEK_4 / WEEK_5+ / ONGOING
              (controls generation order — acute emergencies first)
"""

import json
from pathlib import Path

# Generation priority:
#   WEEK_1    — first 50 acute emergencies (generate first, need on day 1)
#   WEEK_2    — common ward presentations (~100 topics)
#   WEEK_3    — chronic disease management (~150 topics)
#   WEEK_4    — system-specific deep dives (~250 topics)
#   WEEK_5    — specialty topics (~300 topics)
#   ONGOING   — quick-refs, interpretation, clinical skills (~100 topics)

TOPICS = [
    # ===========================================================
    # WEEK 1 — ACUTE EMERGENCIES (must generate first)
    # ===========================================================
    # Cardiac emergencies
    {"title": "Acute Coronary Syndrome — STEMI", "system": "Cardiovascular", "subSystem": "ACS", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Acute Coronary Syndrome — NSTEMI", "system": "Cardiovascular", "subSystem": "ACS", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Cardiac Arrest — Adult ALS", "system": "Emergency Medicine", "subSystem": "Resuscitation", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Cardiac Tamponade", "system": "Cardiovascular", "subSystem": "Pericardial disease", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Arrhythmia — Ventricular Fibrillation", "system": "Cardiovascular", "subSystem": "Arrhythmia", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Arrhythmia — Pulseless Ventricular Tachycardia", "system": "Cardiovascular", "subSystem": "Arrhythmia", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Arrhythmia — Torsades de Pointes", "system": "Cardiovascular", "subSystem": "Arrhythmia", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Shock — overview", "system": "Emergency Medicine", "subSystem": "Resuscitation", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Anaphylaxis", "system": "Allergy & Immunology", "subSystem": "Acute reaction", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Aortic Dissection", "system": "Cardiovascular", "subSystem": "Aortic disease", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Hypertensive Emergency", "system": "Cardiovascular", "subSystem": "Hypertension", "acuity": "EMERGENCY", "priority": "WEEK_1"},

    # Respiratory emergencies
    {"title": "Tension Pneumothorax", "system": "Respiratory", "subSystem": "Pneumothorax", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Massive Haemoptysis", "system": "Respiratory", "subSystem": "Haemoptysis", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Asthma — Acute Severe", "system": "Respiratory", "subSystem": "Asthma", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Asthma — Life-Threatening", "system": "Respiratory", "subSystem": "Asthma", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "COPD — Acidotic Exacerbation", "system": "Respiratory", "subSystem": "COPD", "acuity": "EMERGENCY", "priority": "WEEK_1"},

    # Neurological emergencies
    {"title": "Ischaemic Stroke", "system": "Neurology", "subSystem": "Stroke", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Haemorrhagic Stroke", "system": "Neurology", "subSystem": "Stroke", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Subarachnoid Haemorrhage", "system": "Neurology", "subSystem": "Stroke", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Status Epilepticus", "system": "Neurology", "subSystem": "Seizure", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Bacterial Meningitis", "system": "Neurology", "subSystem": "CNS infection", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Encephalitis", "system": "Neurology", "subSystem": "CNS infection", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Spinal Cord Compression", "system": "Neurology", "subSystem": "Cord compression", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Cauda Equina Syndrome", "system": "Neurology", "subSystem": "Cord compression", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Raised Intracranial Pressure", "system": "Neurology", "subSystem": "Neurocritical", "acuity": "EMERGENCY", "priority": "WEEK_1"},

    # Metabolic/endocrine emergencies
    {"title": "Diabetic Ketoacidosis (DKA)", "system": "Endocrinology", "subSystem": "Diabetes emergency", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Hyperosmolar Hyperglycaemic State (HHS)", "system": "Endocrinology", "subSystem": "Diabetes emergency", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Hypoglycaemia", "system": "Endocrinology", "subSystem": "Diabetes emergency", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Thyroid Storm", "system": "Endocrinology", "subSystem": "Thyroid emergency", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Myxoedema Coma", "system": "Endocrinology", "subSystem": "Thyroid emergency", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Adrenal Crisis", "system": "Endocrinology", "subSystem": "Adrenal emergency", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Severe Hyponatraemia", "system": "Nephrology & Electrolytes", "subSystem": "Electrolyte", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Severe Hyperkalaemia", "system": "Nephrology & Electrolytes", "subSystem": "Electrolyte", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Hypocalcaemia — symptomatic", "system": "Nephrology & Electrolytes", "subSystem": "Electrolyte", "acuity": "EMERGENCY", "priority": "WEEK_1"},

    # GI/surgical emergencies
    {"title": "Upper GI Bleed — Variceal", "system": "Gastroenterology", "subSystem": "GI bleed", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Upper GI Bleed — Non-Variceal", "system": "Gastroenterology", "subSystem": "GI bleed", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Acute Pancreatitis", "system": "Hepatology & Pancreaticobiliary", "subSystem": "Pancreatic", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Acute Cholangitis", "system": "Hepatology & Pancreaticobiliary", "subSystem": "Biliary", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Perforated Viscus", "system": "General Surgery", "subSystem": "Acute abdomen", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Mesenteric Ischaemia", "system": "Gastroenterology", "subSystem": "Acute abdomen", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Appendicitis", "system": "General Surgery", "subSystem": "Acute abdomen", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Ruptured Abdominal Aortic Aneurysm", "system": "Vascular Surgery", "subSystem": "Aortic", "acuity": "EMERGENCY", "priority": "WEEK_1"},

    # Sepsis & infection
    {"title": "Sepsis — Recognition & Management", "system": "Infectious Diseases", "subSystem": "Systemic", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Septic Shock", "system": "Infectious Diseases", "subSystem": "Systemic", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Neutropenic Sepsis", "system": "Haematology", "subSystem": "Oncologic emergency", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Toxic Shock Syndrome", "system": "Infectious Diseases", "subSystem": "Toxin-mediated", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Necrotising Fasciitis", "system": "Dermatology", "subSystem": "Skin emergency", "acuity": "EMERGENCY", "priority": "WEEK_1"},

    # Trauma
    {"title": "Major Trauma — Primary Survey", "system": "Emergency Medicine", "subSystem": "Trauma", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Head Injury — Severe", "system": "Neurology", "subSystem": "Trauma", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Burns — Initial Assessment", "system": "Emergency Medicine", "subSystem": "Burns", "acuity": "EMERGENCY", "priority": "WEEK_1"},

    # Tox / overdose
    {"title": "Poisoning — General Approach", "system": "Emergency Medicine", "subSystem": "Toxicology", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Paracetamol Overdose", "system": "Emergency Medicine", "subSystem": "Toxicology", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Salicylate Poisoning", "system": "Emergency Medicine", "subSystem": "Toxicology", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Tricyclic Antidepressant Poisoning", "system": "Emergency Medicine", "subSystem": "Toxicology", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Opioid Overdose", "system": "Emergency Medicine", "subSystem": "Toxicology", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Carbon Monoxide Poisoning", "system": "Emergency Medicine", "subSystem": "Toxicology", "acuity": "EMERGENCY", "priority": "WEEK_1"},

    # Obstetric emergencies
    {"title": "Postpartum Haemorrhage", "system": "Obstetrics", "subSystem": "Obstetric emergency", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Eclampsia", "system": "Obstetrics", "subSystem": "Hypertension in pregnancy", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Ectopic Pregnancy — Ruptured", "system": "Gynaecology", "subSystem": "Early pregnancy", "acuity": "EMERGENCY", "priority": "WEEK_1"},

    # Other
    {"title": "Acute Limb Ischaemia", "system": "Vascular Surgery", "subSystem": "Limb", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Testicular Torsion", "system": "Urology", "subSystem": "Acute scrotum", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Angioedema — Acute", "system": "Allergy & Immunology", "subSystem": "Acute reaction", "acuity": "EMERGENCY", "priority": "WEEK_1"},
    {"title": "Reduced GCS — Approach", "system": "Emergency Medicine", "subSystem": "Resuscitation", "acuity": "EMERGENCY", "priority": "WEEK_1"},

    # ===========================================================
    # WEEK 2 — COMMON WARD PRESENTATIONS
    # ===========================================================
    # Cardiology
    {"title": "Atrial Fibrillation", "system": "Cardiovascular", "subSystem": "Arrhythmia", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Atrial Flutter", "system": "Cardiovascular", "subSystem": "Arrhythmia", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Supraventricular Tachycardia", "system": "Cardiovascular", "subSystem": "Arrhythmia", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Ventricular Tachycardia — stable", "system": "Cardiovascular", "subSystem": "Arrhythmia", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Bradycardia — symptomatic", "system": "Cardiovascular", "subSystem": "Arrhythmia", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Heart Failure — Acute Decompensated", "system": "Cardiovascular", "subSystem": "Heart failure", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Acute Pericarditis", "system": "Cardiovascular", "subSystem": "Pericardial disease", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Infective Endocarditis", "system": "Cardiovascular", "subSystem": "Valvular/infection", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Deep Vein Thrombosis", "system": "Cardiovascular", "subSystem": "Venous", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Pulmonary Embolism", "system": "Cardiovascular", "subSystem": "Venous", "acuity": "EMERGENCY", "priority": "WEEK_2"},
    {"title": "Syncope — Approach", "system": "Cardiovascular", "subSystem": "Syncope", "acuity": "URGENT", "priority": "WEEK_2"},

    # Respiratory
    {"title": "Community-Acquired Pneumonia", "system": "Respiratory", "subSystem": "Infection", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Hospital-Acquired Pneumonia", "system": "Respiratory", "subSystem": "Infection", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "COPD — Exacerbation", "system": "Respiratory", "subSystem": "COPD", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Asthma — Chronic Management", "system": "Respiratory", "subSystem": "Asthma", "acuity": "CHRONIC", "priority": "WEEK_2"},
    {"title": "Pleural Effusion", "system": "Respiratory", "subSystem": "Pleural", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Pneumothorax — Spontaneous", "system": "Respiratory", "subSystem": "Pneumothorax", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Respiratory Failure — Type 1", "system": "Respiratory", "subSystem": "Respiratory failure", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Respiratory Failure — Type 2", "system": "Respiratory", "subSystem": "Respiratory failure", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Acute Respiratory Distress Syndrome", "system": "Critical Care / ICU", "subSystem": "Respiratory failure", "acuity": "EMERGENCY", "priority": "WEEK_2"},

    # GI
    {"title": "Acute Liver Failure", "system": "Hepatology & Pancreaticobiliary", "subSystem": "Hepatic emergency", "acuity": "EMERGENCY", "priority": "WEEK_2"},
    {"title": "Acute Cholecystitis", "system": "Hepatology & Pancreaticobiliary", "subSystem": "Biliary", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Lower GI Bleed", "system": "Gastroenterology", "subSystem": "GI bleed", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Bowel Obstruction", "system": "General Surgery", "subSystem": "Obstruction", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Diverticulitis", "system": "Gastroenterology", "subSystem": "Lower GI", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "C. difficile Infection", "system": "Infectious Diseases", "subSystem": "GI infection", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Infective Diarrhoea", "system": "Infectious Diseases", "subSystem": "GI infection", "acuity": "URGENT", "priority": "WEEK_2"},

    # Renal/electrolytes
    {"title": "Acute Kidney Injury", "system": "Nephrology & Electrolytes", "subSystem": "AKI", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "UTI — Complicated", "system": "Urology", "subSystem": "UTI", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Pyelonephritis — Acute", "system": "Urology", "subSystem": "UTI", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Hyponatraemia — Workup", "system": "Nephrology & Electrolytes", "subSystem": "Electrolyte", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Hypercalcaemia", "system": "Nephrology & Electrolytes", "subSystem": "Electrolyte", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Acid-Base Disorder — Approach", "system": "Nephrology & Electrolytes", "subSystem": "Acid-base", "acuity": "URGENT", "priority": "WEEK_2"},

    # Neuro
    {"title": "Delirium", "system": "Neurology", "subSystem": "Confusion", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "First Seizure", "system": "Neurology", "subSystem": "Seizure", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Subdural Haematoma", "system": "Neurology", "subSystem": "Trauma", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Headache — Red Flags", "system": "Neurology", "subSystem": "Headache", "acuity": "URGENT", "priority": "WEEK_2"},

    # Haematology
    {"title": "Anaemia — Workup", "system": "Haematology", "subSystem": "Anaemia", "acuity": "ROUTINE", "priority": "WEEK_2"},
    {"title": "Iron Deficiency Anaemia", "system": "Haematology", "subSystem": "Anaemia", "acuity": "ROUTINE", "priority": "WEEK_2"},
    {"title": "Venous Thromboembolism Prophylaxis", "system": "Haematology", "subSystem": "Thrombosis", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Disseminated Intravascular Coagulation", "system": "Haematology", "subSystem": "Coagulopathy", "acuity": "EMERGENCY", "priority": "WEEK_2"},

    # Common ward calls
    {"title": "The Hypotensive Patient", "system": "Emergency Medicine", "subSystem": "Ward call", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "The Tachycardic Patient", "system": "Emergency Medicine", "subSystem": "Ward call", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "The Agitated Patient", "system": "Psychiatry", "subSystem": "Acute behaviour", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "The Patient Who Fell", "system": "Geriatrics", "subSystem": "Falls", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Acute Kidney Injury on the Ward", "system": "Nephrology & Electrolytes", "subSystem": "AKI", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Post-Operative Fever", "system": "General Surgery", "subSystem": "Post-op", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Post-Operative Hypotension", "system": "General Surgery", "subSystem": "Post-op", "acuity": "URGENT", "priority": "WEEK_2"},
    {"title": "Oliguria on the Ward", "system": "Nephrology & Electrolytes", "subSystem": "AKI", "acuity": "URGENT", "priority": "WEEK_2"},

    # Derm emergencies
    {"title": "Stevens-Johnson Syndrome / TEN", "system": "Dermatology", "subSystem": "Skin emergency", "acuity": "EMERGENCY", "priority": "WEEK_2"},
    {"title": "Erythroderma", "system": "Dermatology", "subSystem": "Skin emergency", "acuity": "EMERGENCY", "priority": "WEEK_2"},
    {"title": "Cellulitis", "system": "Dermatology", "subSystem": "Skin infection", "acuity": "URGENT", "priority": "WEEK_2"},

    # ===========================================================
    # WEEK 3 — CHRONIC DISEASE MANAGEMENT
    # ===========================================================
    {"title": "Hypertension — Essential", "system": "Cardiovascular", "subSystem": "Hypertension", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Heart Failure — Chronic (HFrEF)", "system": "Cardiovascular", "subSystem": "Heart failure", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Stable Angina", "system": "Cardiovascular", "subSystem": "Ischaemic", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Aortic Stenosis", "system": "Cardiovascular", "subSystem": "Valvular", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Mitral Regurgitation", "system": "Cardiovascular", "subSystem": "Valvular", "acuity": "CHRONIC", "priority": "WEEK_3"},

    {"title": "COPD — Stable", "system": "Respiratory", "subSystem": "COPD", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Bronchiectasis", "system": "Respiratory", "subSystem": "Suppurative", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Idiopathic Pulmonary Fibrosis", "system": "Respiratory", "subSystem": "ILD", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Obstructive Sleep Apnoea", "system": "Respiratory", "subSystem": "Sleep", "acuity": "CHRONIC", "priority": "WEEK_3"},

    {"title": "Type 2 Diabetes Mellitus", "system": "Endocrinology", "subSystem": "Diabetes", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Type 1 Diabetes Mellitus", "system": "Endocrinology", "subSystem": "Diabetes", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Hypothyroidism", "system": "Endocrinology", "subSystem": "Thyroid", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Hyperthyroidism — Graves'", "system": "Endocrinology", "subSystem": "Thyroid", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Osteoporosis", "system": "Endocrinology", "subSystem": "Bone", "acuity": "CHRONIC", "priority": "WEEK_3"},

    {"title": "Chronic Kidney Disease", "system": "Nephrology & Electrolytes", "subSystem": "CKD", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Nephrotic Syndrome", "system": "Nephrology & Electrolytes", "subSystem": "Glomerular", "acuity": "CHRONIC", "priority": "WEEK_3"},

    {"title": "Ulcerative Colitis", "system": "Gastroenterology", "subSystem": "IBD", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Crohn's Disease", "system": "Gastroenterology", "subSystem": "IBD", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Irritable Bowel Syndrome", "system": "Gastroenterology", "subSystem": "Functional", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Coeliac Disease", "system": "Gastroenterology", "subSystem": "Malabsorption", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "GORD", "system": "Gastroenterology", "subSystem": "Upper GI", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Peptic Ulcer Disease", "system": "Gastroenterology", "subSystem": "Upper GI", "acuity": "CHRONIC", "priority": "WEEK_3"},

    {"title": "Cirrhosis — Compensated", "system": "Hepatology & Pancreaticobiliary", "subSystem": "Chronic liver", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Cirrhosis — Decompensated", "system": "Hepatology & Pancreaticobiliary", "subSystem": "Chronic liver", "acuity": "URGENT", "priority": "WEEK_3"},
    {"title": "Chronic Hepatitis B", "system": "Hepatology & Pancreaticobiliary", "subSystem": "Viral hepatitis", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Chronic Hepatitis C", "system": "Hepatology & Pancreaticobiliary", "subSystem": "Viral hepatitis", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "MASLD / MASH", "system": "Hepatology & Pancreaticobiliary", "subSystem": "Chronic liver", "acuity": "CHRONIC", "priority": "WEEK_3"},

    {"title": "Parkinson's Disease", "system": "Neurology", "subSystem": "Movement", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Multiple Sclerosis", "system": "Neurology", "subSystem": "Demyelinating", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Epilepsy — Chronic Management", "system": "Neurology", "subSystem": "Seizure", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Dementia — Overview", "system": "Neurology", "subSystem": "Cognitive", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Migraine", "system": "Neurology", "subSystem": "Headache", "acuity": "CHRONIC", "priority": "WEEK_3"},

    {"title": "Rheumatoid Arthritis", "system": "Rheumatology & MSK", "subSystem": "Inflammatory", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "SLE", "system": "Rheumatology & MSK", "subSystem": "Connective tissue", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Gout", "system": "Rheumatology & MSK", "subSystem": "Crystal", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Osteoarthritis", "system": "Rheumatology & MSK", "subSystem": "Degenerative", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Polymyalgia Rheumatica", "system": "Rheumatology & MSK", "subSystem": "Inflammatory", "acuity": "CHRONIC", "priority": "WEEK_3"},
    {"title": "Giant Cell Arteritis", "system": "Rheumatology & MSK", "subSystem": "Vasculitis", "acuity": "URGENT", "priority": "WEEK_3"},

    # ===========================================================
    # WEEK 4 — SYSTEM-SPECIFIC DEEP DIVES
    # ===========================================================
    # Cardio
    {"title": "Hypertrophic Cardiomyopathy", "system": "Cardiovascular", "subSystem": "Cardiomyopathy", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Dilated Cardiomyopathy", "system": "Cardiovascular", "subSystem": "Cardiomyopathy", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Myocarditis", "system": "Cardiovascular", "subSystem": "Myocardial", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Aortic Regurgitation", "system": "Cardiovascular", "subSystem": "Valvular", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Mitral Stenosis", "system": "Cardiovascular", "subSystem": "Valvular", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Rheumatic Fever", "system": "Cardiovascular", "subSystem": "Valvular", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Peripheral Arterial Disease", "system": "Cardiovascular", "subSystem": "Vascular", "acuity": "CHRONIC", "priority": "WEEK_4"},

    # Resp
    {"title": "Lung Cancer — NSCLC", "system": "Respiratory", "subSystem": "Malignancy", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Lung Cancer — SCLC", "system": "Respiratory", "subSystem": "Malignancy", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Tuberculosis — Pulmonary", "system": "Infectious Diseases", "subSystem": "TB", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Tuberculosis — Latent", "system": "Infectious Diseases", "subSystem": "TB", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Sarcoidosis", "system": "Respiratory", "subSystem": "ILD", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Pulmonary Hypertension", "system": "Cardiovascular", "subSystem": "Pulmonary vascular", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Aspiration Pneumonia", "system": "Respiratory", "subSystem": "Infection", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Empyema", "system": "Respiratory", "subSystem": "Pleural", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Lung Abscess", "system": "Respiratory", "subSystem": "Infection", "acuity": "URGENT", "priority": "WEEK_4"},

    # GI
    {"title": "Colorectal Cancer", "system": "Gastroenterology", "subSystem": "Malignancy", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Oesophageal Cancer", "system": "Gastroenterology", "subSystem": "Malignancy", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Gastric Cancer", "system": "Gastroenterology", "subSystem": "Malignancy", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Pancreatic Cancer", "system": "Hepatology & Pancreaticobiliary", "subSystem": "Malignancy", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Chronic Pancreatitis", "system": "Hepatology & Pancreaticobiliary", "subSystem": "Pancreatic", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Gallstones", "system": "Hepatology & Pancreaticobiliary", "subSystem": "Biliary", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Autoimmune Hepatitis", "system": "Hepatology & Pancreaticobiliary", "subSystem": "Chronic liver", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Primary Biliary Cholangitis", "system": "Hepatology & Pancreaticobiliary", "subSystem": "Chronic liver", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Primary Sclerosing Cholangitis", "system": "Hepatology & Pancreaticobiliary", "subSystem": "Chronic liver", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Haemochromatosis", "system": "Hepatology & Pancreaticobiliary", "subSystem": "Metabolic liver", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Hepatocellular Carcinoma", "system": "Hepatology & Pancreaticobiliary", "subSystem": "Malignancy", "acuity": "CHRONIC", "priority": "WEEK_4"},

    # Renal
    {"title": "IgA Nephropathy", "system": "Nephrology & Electrolytes", "subSystem": "Glomerular", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Renal Cell Carcinoma", "system": "Urology", "subSystem": "Malignancy", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Bladder Cancer", "system": "Urology", "subSystem": "Malignancy", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Nephrolithiasis", "system": "Urology", "subSystem": "Stones", "acuity": "URGENT", "priority": "WEEK_4"},

    # Endo
    {"title": "Addison's Disease", "system": "Endocrinology", "subSystem": "Adrenal", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Cushing's Syndrome", "system": "Endocrinology", "subSystem": "Adrenal", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Phaeochromocytoma", "system": "Endocrinology", "subSystem": "Adrenal", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Primary Hyperparathyroidism", "system": "Endocrinology", "subSystem": "Calcium", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Prolactinoma", "system": "Endocrinology", "subSystem": "Pituitary", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Acromegaly", "system": "Endocrinology", "subSystem": "Pituitary", "acuity": "CHRONIC", "priority": "WEEK_4"},

    # Neuro
    {"title": "Motor Neurone Disease", "system": "Neurology", "subSystem": "MND", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Huntington's Disease", "system": "Neurology", "subSystem": "Movement", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Guillain-Barré Syndrome", "system": "Neurology", "subSystem": "Neuropathy", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Myasthenia Gravis", "system": "Neurology", "subSystem": "Neuromuscular", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Bell's Palsy", "system": "Neurology", "subSystem": "Cranial nerve", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Trigeminal Neuralgia", "system": "Neurology", "subSystem": "Cranial nerve", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Idiopathic Intracranial Hypertension", "system": "Neurology", "subSystem": "Headache", "acuity": "URGENT", "priority": "WEEK_4"},

    # Haem
    {"title": "B12 Deficiency", "system": "Haematology", "subSystem": "Anaemia", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Sickle Cell Disease", "system": "Haematology", "subSystem": "Haemoglobinopathy", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Thalassaemia", "system": "Haematology", "subSystem": "Haemoglobinopathy", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Acute Myeloid Leukaemia", "system": "Haematology", "subSystem": "Leukaemia", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Chronic Lymphocytic Leukaemia", "system": "Haematology", "subSystem": "Leukaemia", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Hodgkin Lymphoma", "system": "Haematology", "subSystem": "Lymphoma", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Non-Hodgkin Lymphoma", "system": "Haematology", "subSystem": "Lymphoma", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Multiple Myeloma", "system": "Haematology", "subSystem": "Plasma cell", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "ITP", "system": "Haematology", "subSystem": "Platelet", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Haemophilia A", "system": "Haematology", "subSystem": "Coagulopathy", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "von Willebrand Disease", "system": "Haematology", "subSystem": "Coagulopathy", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Antiphospholipid Syndrome", "system": "Haematology", "subSystem": "Thrombophilia", "acuity": "CHRONIC", "priority": "WEEK_4"},

    # ID
    {"title": "HIV — Initial Workup", "system": "Infectious Diseases", "subSystem": "HIV", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Pneumocystis Jirovecii Pneumonia", "system": "Infectious Diseases", "subSystem": "Opportunistic", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Infective Endocarditis — prophylaxis", "system": "Cardiovascular", "subSystem": "Valvular/infection", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Malaria", "system": "Infectious Diseases", "subSystem": "Tropical", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Fever in Returning Traveller", "system": "Infectious Diseases", "subSystem": "Tropical", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Syphilis", "system": "Infectious Diseases", "subSystem": "STI", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Pelvic Inflammatory Disease", "system": "Gynaecology", "subSystem": "STI", "acuity": "URGENT", "priority": "WEEK_4"},

    # Rheum
    {"title": "Ankylosing Spondylitis", "system": "Rheumatology & MSK", "subSystem": "Seronegative", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Systemic Sclerosis", "system": "Rheumatology & MSK", "subSystem": "Connective tissue", "acuity": "CHRONIC", "priority": "WEEK_4"},
    {"title": "Vasculitis — ANCA-associated", "system": "Rheumatology & MSK", "subSystem": "Vasculitis", "acuity": "URGENT", "priority": "WEEK_4"},
    {"title": "Septic Arthritis", "system": "Rheumatology & MSK", "subSystem": "Acute joint", "acuity": "EMERGENCY", "priority": "WEEK_4"},
    {"title": "Osteomyelitis", "system": "Rheumatology & MSK", "subSystem": "Bone infection", "acuity": "URGENT", "priority": "WEEK_4"},

    # ===========================================================
    # WEEK 5 — SPECIALTY TOPICS
    # ===========================================================
    # Surgery
    {"title": "Pre-Operative Assessment", "system": "General Surgery", "subSystem": "Peri-op", "acuity": "ROUTINE", "priority": "WEEK_5"},
    {"title": "Post-Operative Ileus", "system": "General Surgery", "subSystem": "Post-op", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Anastomotic Leak", "system": "General Surgery", "subSystem": "Post-op", "acuity": "EMERGENCY", "priority": "WEEK_5"},
    {"title": "Surgical Site Infection", "system": "General Surgery", "subSystem": "Post-op", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Inguinal Hernia", "system": "General Surgery", "subSystem": "Hernia", "acuity": "ROUTINE", "priority": "WEEK_5"},
    {"title": "Critical Limb Ischaemia", "system": "Vascular Surgery", "subSystem": "Limb", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Varicose Veins", "system": "Vascular Surgery", "subSystem": "Venous", "acuity": "ROUTINE", "priority": "WEEK_5"},

    # Ortho/trauma
    {"title": "Neck of Femur Fracture", "system": "Orthopaedics & Trauma", "subSystem": "Fracture", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Compartment Syndrome", "system": "Orthopaedics & Trauma", "subSystem": "Limb emergency", "acuity": "EMERGENCY", "priority": "WEEK_5"},
    {"title": "Scaphoid Fracture", "system": "Orthopaedics & Trauma", "subSystem": "Fracture", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Ankle Fracture", "system": "Orthopaedics & Trauma", "subSystem": "Fracture", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Shoulder Dislocation", "system": "Orthopaedics & Trauma", "subSystem": "Dislocation", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "ACL Injury", "system": "Orthopaedics & Trauma", "subSystem": "Soft tissue", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Low Back Pain — Mechanical", "system": "Orthopaedics & Trauma", "subSystem": "Spine", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Disc Herniation", "system": "Orthopaedics & Trauma", "subSystem": "Spine", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Rib Fracture", "system": "Orthopaedics & Trauma", "subSystem": "Trauma", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Flail Chest", "system": "Orthopaedics & Trauma", "subSystem": "Trauma", "acuity": "EMERGENCY", "priority": "WEEK_5"},

    # Paeds
    {"title": "Paediatric Sepsis", "system": "Paediatrics", "subSystem": "Emergency", "acuity": "EMERGENCY", "priority": "WEEK_5"},
    {"title": "Meningococcal Disease", "system": "Paediatrics", "subSystem": "Infection", "acuity": "EMERGENCY", "priority": "WEEK_5"},
    {"title": "Paediatric Anaphylaxis", "system": "Paediatrics", "subSystem": "Emergency", "acuity": "EMERGENCY", "priority": "WEEK_5"},
    {"title": "Bronchiolitis", "system": "Paediatrics", "subSystem": "Respiratory", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Croup", "system": "ENT", "subSystem": "Paediatric airway", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Febrile Convulsion", "system": "Paediatrics", "subSystem": "Seizure", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Febrile Child — Approach", "system": "Paediatrics", "subSystem": "Infection", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Paediatric DKA", "system": "Paediatrics", "subSystem": "Endocrine", "acuity": "EMERGENCY", "priority": "WEEK_5"},
    {"title": "Bronchiolitis — Assessment", "system": "Paediatrics", "subSystem": "Respiratory", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Child Safeguarding", "system": "Paediatrics", "subSystem": "Safeguarding", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Neonatal Jaundice", "system": "Paediatrics", "subSystem": "Neonatal", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Developmental Milestones", "system": "Paediatrics", "subSystem": "Development", "acuity": "ROUTINE", "priority": "WEEK_5"},
    {"title": "Failure to Thrive", "system": "Paediatrics", "subSystem": "Growth", "acuity": "CHRONIC", "priority": "WEEK_5"},

    # Obs
    {"title": "Pre-Eclampsia", "system": "Obstetrics", "subSystem": "Hypertension in pregnancy", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Antepartum Haemorrhage", "system": "Obstetrics", "subSystem": "Obstetric emergency", "acuity": "EMERGENCY", "priority": "WEEK_5"},
    {"title": "Preterm Labour", "system": "Obstetrics", "subSystem": "Labour", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Hyperemesis Gravidarum", "system": "Obstetrics", "subSystem": "Pregnancy complication", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Gestational Diabetes", "system": "Obstetrics", "subSystem": "Pregnancy complication", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "VTE in Pregnancy", "system": "Obstetrics", "subSystem": "Pregnancy complication", "acuity": "URGENT", "priority": "WEEK_5"},

    # Gynae
    {"title": "Ectopic Pregnancy", "system": "Gynaecology", "subSystem": "Early pregnancy", "acuity": "EMERGENCY", "priority": "WEEK_5"},
    {"title": "Miscarriage — Threatened", "system": "Gynaecology", "subSystem": "Early pregnancy", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Miscarriage — Incomplete", "system": "Gynaecology", "subSystem": "Early pregnancy", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "PCOS", "system": "Gynaecology", "subSystem": "Endocrine", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Endometriosis", "system": "Gynaecology", "subSystem": "Chronic pain", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Menorrhagia", "system": "Gynaecology", "subSystem": "Menstrual", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Menopause & HRT", "system": "Gynaecology", "subSystem": "Menopause", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Cervical Cancer", "system": "Gynaecology", "subSystem": "Malignancy", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Ovarian Cancer", "system": "Gynaecology", "subSystem": "Malignancy", "acuity": "CHRONIC", "priority": "WEEK_5"},

    # Psych
    {"title": "Depression — Major", "system": "Psychiatry", "subSystem": "Mood", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Bipolar Affective Disorder", "system": "Psychiatry", "subSystem": "Mood", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Schizophrenia", "system": "Psychiatry", "subSystem": "Psychotic", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Generalised Anxiety Disorder", "system": "Psychiatry", "subSystem": "Anxiety", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Acute Psychosis", "system": "Psychiatry", "subSystem": "Psychotic", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Suicide Risk Assessment", "system": "Psychiatry", "subSystem": "Risk", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Deliberate Self-Harm", "system": "Psychiatry", "subSystem": "Risk", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Alcohol Withdrawal", "system": "Psychiatry", "subSystem": "Substance", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Delirium Tremens", "system": "Psychiatry", "subSystem": "Substance", "acuity": "EMERGENCY", "priority": "WEEK_5"},
    {"title": "Opioid Use Disorder", "system": "Psychiatry", "subSystem": "Substance", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Eating Disorders", "system": "Psychiatry", "subSystem": "Eating", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Mental Health Act — Emergency Detention", "system": "Psychiatry", "subSystem": "Legal", "acuity": "URGENT", "priority": "WEEK_5"},

    # Derm
    {"title": "Atopic Eczema", "system": "Dermatology", "subSystem": "Inflammatory", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Psoriasis", "system": "Dermatology", "subSystem": "Inflammatory", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Cellulitis — Lower limb", "system": "Dermatology", "subSystem": "Skin infection", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Impetigo", "system": "Dermatology", "subSystem": "Skin infection", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Shingles (Herpes Zoster)", "system": "Dermatology", "subSystem": "Viral", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Melanoma", "system": "Dermatology", "subSystem": "Malignancy", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Basal Cell Carcinoma", "system": "Dermatology", "subSystem": "Malignancy", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Leg Ulcer — Venous vs Arterial", "system": "Dermatology", "subSystem": "Ulcer", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Urticaria — Acute", "system": "Dermatology", "subSystem": "Allergic", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Pemphigus Vulgaris", "system": "Dermatology", "subSystem": "Blistering", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Bullous Pemphigoid", "system": "Dermatology", "subSystem": "Blistering", "acuity": "CHRONIC", "priority": "WEEK_5"},

    # ENT
    {"title": "Epistaxis", "system": "ENT", "subSystem": "Nasal", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Epiglottitis", "system": "ENT", "subSystem": "Airway emergency", "acuity": "EMERGENCY", "priority": "WEEK_5"},
    {"title": "Quinsy (Peritonsillar Abscess)", "system": "ENT", "subSystem": "Throat", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Otitis Media", "system": "ENT", "subSystem": "Ear", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Otitis Externa", "system": "ENT", "subSystem": "Ear", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Stridor — Assessment", "system": "ENT", "subSystem": "Airway emergency", "acuity": "EMERGENCY", "priority": "WEEK_5"},

    # Ophthalmology
    {"title": "Red Eye — Approach", "system": "Ophthalmology", "subSystem": "Approach", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Acute Angle-Closure Glaucoma", "system": "Ophthalmology", "subSystem": "Emergency", "acuity": "EMERGENCY", "priority": "WEEK_5"},
    {"title": "Orbital Cellulitis", "system": "Ophthalmology", "subSystem": "Infection", "acuity": "EMERGENCY", "priority": "WEEK_5"},
    {"title": "Retinal Detachment", "system": "Ophthalmology", "subSystem": "Retina", "acuity": "EMERGENCY", "priority": "WEEK_5"},
    {"title": "Central Retinal Artery Occlusion", "system": "Ophthalmology", "subSystem": "Retina", "acuity": "EMERGENCY", "priority": "WEEK_5"},
    {"title": "Corneal Abrasion", "system": "Ophthalmology", "subSystem": "Cornea", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Chemical Eye Injury", "system": "Ophthalmology", "subSystem": "Emergency", "acuity": "EMERGENCY", "priority": "WEEK_5"},

    # Geriatrics
    {"title": "Comprehensive Geriatric Assessment", "system": "Geriatrics", "subSystem": "Overview", "acuity": "ROUTINE", "priority": "WEEK_5"},
    {"title": "Falls — Older Adult", "system": "Geriatrics", "subSystem": "Falls", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "Polypharmacy", "system": "Geriatrics", "subSystem": "Pharmacy", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "Frailty", "system": "Geriatrics", "subSystem": "Syndromes", "acuity": "CHRONIC", "priority": "WEEK_5"},

    # Palliative
    {"title": "Cancer Pain — Palliative", "system": "Palliative Care", "subSystem": "Symptom", "acuity": "CHRONIC", "priority": "WEEK_5"},
    {"title": "End-of-Life Care — Last Days", "system": "Palliative Care", "subSystem": "End-of-life", "acuity": "URGENT", "priority": "WEEK_5"},
    {"title": "SPIKES — Breaking Bad News", "system": "Palliative Care", "subSystem": "Communication", "acuity": "ROUTINE", "priority": "WEEK_5"},

    # ===========================================================
    # ONGOING — Procedural skills, ward essentials, pharmacy
    # ===========================================================
    # FY1 survival / professional
    {"title": "Death Verification & Certification", "system": "Professional", "subSystem": "FY1 essential", "acuity": "ROUTINE", "priority": "ONGOING"},
    {"title": "Consent & Capacity (Mental Capacity Act)", "system": "Professional", "subSystem": "Legal", "acuity": "ROUTINE", "priority": "ONGOING"},
    {"title": "Gillick Competence", "system": "Professional", "subSystem": "Legal", "acuity": "ROUTINE", "priority": "ONGOING"},
    {"title": "Adult Safeguarding", "system": "Professional", "subSystem": "Safeguarding", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "Child Safeguarding — Recognition", "system": "Professional", "subSystem": "Safeguarding", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "Needlestick Injury & BBV Exposure", "system": "Professional", "subSystem": "Occupational", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "Handover — SBAR", "system": "Professional", "subSystem": "Communication", "acuity": "ROUTINE", "priority": "ONGOING"},
    {"title": "Breaking Bad News — Practical", "system": "Professional", "subSystem": "Communication", "acuity": "ROUTINE", "priority": "ONGOING"},
    {"title": "Dealing with the Difficult Patient", "system": "Professional", "subSystem": "Communication", "acuity": "ROUTINE", "priority": "ONGOING"},
    {"title": "Patient Refusing Treatment", "system": "Professional", "subSystem": "Legal", "acuity": "URGENT", "priority": "ONGOING"},

    # Procedural skills
    {"title": "IV Cannulation", "system": "Clinical Skills", "subSystem": "Procedure", "acuity": "ROUTINE", "priority": "ONGOING"},
    {"title": "Venepuncture", "system": "Clinical Skills", "subSystem": "Procedure", "acuity": "ROUTINE", "priority": "ONGOING"},
    {"title": "Arterial Blood Gas Sampling", "system": "Clinical Skills", "subSystem": "Procedure", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "Blood Cultures — Taking", "system": "Clinical Skills", "subSystem": "Procedure", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "Male Urinary Catheterisation", "system": "Clinical Skills", "subSystem": "Procedure", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "Female Urinary Catheterisation", "system": "Clinical Skills", "subSystem": "Procedure", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "Nasogastric Tube Insertion", "system": "Clinical Skills", "subSystem": "Procedure", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "Ascitic Tap (Paracentesis)", "system": "Clinical Skills", "subSystem": "Procedure", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "Pleural Tap & Chest Drain", "system": "Clinical Skills", "subSystem": "Procedure", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "Lumbar Puncture", "system": "Clinical Skills", "subSystem": "Procedure", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "Joint Aspiration", "system": "Clinical Skills", "subSystem": "Procedure", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "Suturing — Basic", "system": "Clinical Skills", "subSystem": "Procedure", "acuity": "ROUTINE", "priority": "ONGOING"},
    {"title": "ECG — Performing", "system": "Clinical Skills", "subSystem": "Procedure", "acuity": "ROUTINE", "priority": "ONGOING"},
    {"title": "Blood Transfusion — Administration", "system": "Clinical Skills", "subSystem": "Procedure", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "Intramuscular Injection", "system": "Clinical Skills", "subSystem": "Procedure", "acuity": "ROUTINE", "priority": "ONGOING"},
    {"title": "Subcutaneous Injection", "system": "Clinical Skills", "subSystem": "Procedure", "acuity": "ROUTINE", "priority": "ONGOING"},
    {"title": "Setting Up an IV Infusion", "system": "Clinical Skills", "subSystem": "Procedure", "acuity": "ROUTINE", "priority": "ONGOING"},
    {"title": "Defibrillation — Manual", "system": "Clinical Skills", "subSystem": "Resuscitation", "acuity": "EMERGENCY", "priority": "ONGOING"},

    # Interpretation
    {"title": "ECG — Approach (Rate/Rhythm/Axis)", "system": "Interpretation Skills", "subSystem": "ECG", "acuity": "ROUTINE", "priority": "ONGOING"},
    {"title": "ECG — Acute MI Patterns", "system": "Interpretation Skills", "subSystem": "ECG", "acuity": "EMERGENCY", "priority": "ONGOING"},
    {"title": "ECG — Arrhythmias", "system": "Interpretation Skills", "subSystem": "ECG", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "ECG — Conduction Blocks", "system": "Interpretation Skills", "subSystem": "ECG", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "ECG — Hyperkalaemia Patterns", "system": "Interpretation Skills", "subSystem": "ECG", "acuity": "EMERGENCY", "priority": "ONGOING"},
    {"title": "ABG Interpretation", "system": "Interpretation Skills", "subSystem": "ABG", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "CXR — Approach", "system": "Interpretation Skills", "subSystem": "Imaging", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "CT Head — Basic Interpretation", "system": "Interpretation Skills", "subSystem": "Imaging", "acuity": "URGENT", "priority": "ONGOING"},

    # High-yield drug monographs
    {"title": "Warfarin — Initiation & Reversal", "system": "Clinical Pharmacology", "subSystem": "Drug monograph", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "DOACs — Overview", "system": "Clinical Pharmacology", "subSystem": "Drug monograph", "acuity": "CHRONIC", "priority": "ONGOING"},
    {"title": "Insulin — Types & Regimens", "system": "Clinical Pharmacology", "subSystem": "Drug monograph", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "Opioids — Conversion & Equianalgesia", "system": "Clinical Pharmacology", "subSystem": "Drug monograph", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "Gentamicin — Dosing & Monitoring", "system": "Clinical Pharmacology", "subSystem": "Drug monograph", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "Vancomycin — Dosing & Monitoring", "system": "Clinical Pharmacology", "subSystem": "Drug monograph", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "Corticosteroids — Equivalence & Weaning", "system": "Clinical Pharmacology", "subSystem": "Drug monograph", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "Antibiotic Stewardship", "system": "Clinical Pharmacology", "subSystem": "Principle", "acuity": "ROUTINE", "priority": "ONGOING"},
    {"title": "Prescribing in Renal Impairment", "system": "Clinical Pharmacology", "subSystem": "Principle", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "Prescribing in Pregnancy", "system": "Clinical Pharmacology", "subSystem": "Principle", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "Common Drug Interactions", "system": "Clinical Pharmacology", "subSystem": "Principle", "acuity": "ROUTINE", "priority": "ONGOING"},

    # Fluids / nutrition
    {"title": "IV Fluid Prescribing — Maintenance", "system": "Fluids & Nutrition", "subSystem": "Fluids", "acuity": "ROUTINE", "priority": "ONGOING"},
    {"title": "IV Fluid Prescribing — Resuscitation", "system": "Fluids & Nutrition", "subSystem": "Fluids", "acuity": "EMERGENCY", "priority": "ONGOING"},
    {"title": "Refeeding Syndrome", "system": "Fluids & Nutrition", "subSystem": "Nutrition", "acuity": "EMERGENCY", "priority": "ONGOING"},
    {"title": "Parenteral Nutrition", "system": "Fluids & Nutrition", "subSystem": "Nutrition", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "MUST Score — Malnutrition", "system": "Fluids & Nutrition", "subSystem": "Nutrition", "acuity": "ROUTINE", "priority": "ONGOING"},

    # ICU / anaesthetics
    {"title": "Escalation of Care — Decision", "system": "Critical Care / ICU", "subSystem": "Decision", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "Ventilation — Basics for FY1", "system": "Critical Care / ICU", "subSystem": "Ventilation", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "Vasopressors & Inotropes — Overview", "system": "Critical Care / ICU", "subSystem": "Circulatory support", "acuity": "EMERGENCY", "priority": "ONGOING"},
    {"title": "Sepsis — ICU Management", "system": "Critical Care / ICU", "subSystem": "Infection", "acuity": "EMERGENCY", "priority": "ONGOING"},

    # Oncologic emergencies
    {"title": "SVC Obstruction", "system": "Oncologic Emergencies", "subSystem": "Emergency", "acuity": "EMERGENCY", "priority": "ONGOING"},
    {"title": "Malignant Spinal Cord Compression", "system": "Oncologic Emergencies", "subSystem": "Emergency", "acuity": "EMERGENCY", "priority": "ONGOING"},
    {"title": "Tumour Lysis Syndrome", "system": "Oncologic Emergencies", "subSystem": "Emergency", "acuity": "EMERGENCY", "priority": "ONGOING"},
    {"title": "Hypercalcaemia of Malignancy", "system": "Oncologic Emergencies", "subSystem": "Emergency", "acuity": "EMERGENCY", "priority": "ONGOING"},

    # Public health / misc
    {"title": "Notifiable Diseases & Reporting", "system": "Public Health", "subSystem": "Reporting", "acuity": "URGENT", "priority": "ONGOING"},
    {"title": "Adult Vaccination Schedule", "system": "Public Health", "subSystem": "Prevention", "acuity": "ROUTINE", "priority": "ONGOING"},
    {"title": "Travel Medicine — Pre-Travel", "system": "Public Health", "subSystem": "Prevention", "acuity": "ROUTINE", "priority": "ONGOING"},
]


def main():
    # Sanity: detect duplicate titles
    seen = set()
    dupes = []
    for t in TOPICS:
        if t["title"] in seen:
            dupes.append(t["title"])
        seen.add(t["title"])
    if dupes:
        print(f"WARNING: {len(dupes)} duplicate topics:")
        for d in dupes:
            print(f"  - {d}")

    # Group counts
    by_system = {}
    by_priority = {}
    by_acuity = {}
    for t in TOPICS:
        by_system[t["system"]] = by_system.get(t["system"], 0) + 1
        by_priority[t["priority"]] = by_priority.get(t["priority"], 0) + 1
        by_acuity[t["acuity"]] = by_acuity.get(t["acuity"], 0) + 1

    print(f"\nTotal topics: {len(TOPICS)}")
    print(f"\nBy priority:")
    for p, c in sorted(by_priority.items()):
        print(f"  {p}: {c}")
    print(f"\nBy acuity:")
    for a, c in sorted(by_acuity.items()):
        print(f"  {a}: {c}")
    print(f"\nBy system ({len(by_system)} systems):")
    for s, c in sorted(by_system.items(), key=lambda x: -x[1]):
        print(f"  {s}: {c}")

    # Save
    out_path = Path(__file__).parent.parent.resolve() / "data" / "master-topics.json"
    out_path.write_text(
        json.dumps({"version": 2, "count": len(TOPICS), "topics": TOPICS}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nSaved -> {out_path}")

    # Cost projection
    avg_tokens = 3500  # ward + study combined estimate per topic
    total_tokens = len(TOPICS) * avg_tokens
    cost_per_million_input = 0.14
    cost_per_million_output = 0.28
    avg_input = 600  # prompt
    avg_output_ward = 1500
    avg_output_study = 3500
    total_input = len(TOPICS) * 2 * avg_input  # both modes per topic
    total_output = len(TOPICS) * (avg_output_ward + avg_output_study)
    cost = (total_input * cost_per_million_input / 1_000_000) + (total_output * cost_per_million_output / 1_000_000)
    print(f"\nCost projection (ward + study for all topics):")
    print(f"  Input tokens: {total_input:,}")
    print(f"  Output tokens: {total_output:,}")
    print(f"  Estimated cost: ${cost:.2f}")


if __name__ == "__main__":
    main()
