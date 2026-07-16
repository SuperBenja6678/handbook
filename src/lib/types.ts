// Type definitions for the clinical reference data model

export type Acuity = 'EMERGENCY' | 'URGENT' | 'ROUTINE' | 'CHRONIC';
export type TopicStatus = 'PENDING' | 'GENERATED' | 'REVIEWED' | 'MASTERED';
export type EntryMode = 'WARD' | 'STUDY' | 'QUIZ';

// MCQ pattern-recognition angle — see scripts/generate_questions.py
export type QuizAngle = 'recognise' | 'diagnose' | 'treat' | 'next_step' | 'red_flag';
export type QuizDifficulty = 'easy' | 'medium' | 'hard';

export interface QuizQuestion {
  id: string;
  topic: string;
  slug: string;
  system: string;
  subSystem?: string;
  acuity?: Acuity;
  angle: QuizAngle;
  stem: string;
  options: string[];
  answerIndex: number;
  explanation: string;
  difficulty: QuizDifficulty;
}

export interface QuestionSet {
  topic: string;
  slug: string;
  system: string;
  subSystem?: string;
  acuity?: Acuity;
  generatedAt: string;
  model: string;
  grounded: boolean;
  count: number;
  questions: QuizQuestion[];
}

// Entry in public/data/questions-manifest.json — lets the app know which
// topics have a quiz available without fetching every question file.
export interface QuizManifestEntry {
  slug: string;
  topic: string;
  system: string;
  subSystem?: string;
  acuity?: Acuity;
  count: number;
}

export interface ClinicalEntry {
  title: string;
  slug: string;
  system: string;
  subSystem?: string;
  acuity: Acuity;
  oneLiner: string;
  sections: Record<string, string>;
  rawMarkdown: string;
  metadata?: {
    model: string;
    mode?: EntryMode;
    tokensUsed?: Record<string, number>;
    generatedAt?: string;
  };
}

export interface QuickRef {
  id: string;
  title: string;
  category: string;
  content: string;
  pinned?: boolean;
}

// Section display config — order, icon, accent color
export interface SectionMeta {
  name: string;        // exact section key as it appears in `sections`
  iconName: string;    // Lucide icon name
  accent: string;      // Tailwind text class for heading
  bgClass?: string;    // Optional card background
  borderClass?: string;// Optional card border
}

// WARD MODE sections — upgraded v2 prompt with Killers First, Safety Netting,
// split Pearls/Pitfalls, etc. (12 sections total)
export const WARD_SECTION_META: SectionMeta[] = [
  { name: 'Killers First — What Will Kill Them In The First Hour?',
    iconName: 'Skull',
    accent: 'text-red-700',   bgClass: 'bg-red-50/40',   borderClass: 'border-red-300' },
  { name: 'Presentation',          iconName: 'Stethoscope',     accent: 'text-slate-700' },
  { name: 'Differential Diagnosis',iconName: 'GitBranch',       accent: 'text-slate-700' },
  { name: 'Investigations',        iconName: 'Microscope',      accent: 'text-slate-700' },
  { name: 'Management',            iconName: 'ClipboardList',   accent: 'text-slate-700' },
  { name: 'Drugs & Doses',         iconName: 'Pill',            accent: 'text-slate-700' },
  { name: 'Complications',         iconName: 'AlertTriangle',   accent: 'text-amber-700' },
  { name: 'Prognosis',             iconName: 'Activity',        accent: 'text-slate-700' },
  { name: 'Pearls (positive actions)',
    iconName: 'Lightbulb',
    accent: 'text-emerald-700', bgClass: 'bg-emerald-50/30', borderClass: 'border-emerald-200' },
  { name: 'Pitfalls (Errors To Avoid)',
    iconName: 'AlertOctagon',
    accent: 'text-amber-700',  bgClass: 'bg-amber-50/30',  borderClass: 'border-amber-200' },
  { name: 'Safety Netting (If Patient Goes Home)',
    iconName: 'ShieldAlert',
    accent: 'text-teal-700',   bgClass: 'bg-teal-50/30',   borderClass: 'border-teal-200' },
  { name: 'Escalation Criteria',   iconName: 'Siren',
    accent: 'text-red-700',   bgClass: 'bg-red-50/30',   borderClass: 'border-red-200' },
];

// STUDY MODE sections — the deep-teaching structure
export const STUDY_SECTION_META: SectionMeta[] = [
  { name: "1. Pattern Recognition — The Patient You'll See",
    iconName: 'Eye',                accent: 'text-slate-700' },
  { name: '2. What Is This? (Definition & Why It Matters)',
    iconName: 'BookOpen',           accent: 'text-slate-700' },
  { name: '3. Pathophysiology — The "Why" Behind The Findings',
    iconName: 'Brain',              accent: 'text-slate-700' },
  { name: '4. Causes / Triggers (organised in bins)',
    iconName: 'Tags',               accent: 'text-slate-700' },
  { name: '5. Investigations — What, Why, What It Means',
    iconName: 'Microscope',         accent: 'text-slate-700' },
  { name: '6. Management — Approach & Reasoning',
    iconName: 'ClipboardList',      accent: 'text-slate-700' },
  { name: '7. Differential Diagnosis — Comparison Table',
    iconName: 'GitBranch',          accent: 'text-slate-700' },
  { name: '8. Complications — What If You Miss It?',
    iconName: 'AlertTriangle',
    accent: 'text-amber-700', bgClass: 'bg-amber-50/30', borderClass: 'border-amber-200' },
  { name: '9. High-Yield Mnemonics & Pearls',
    iconName: 'Lightbulb',
    accent: 'text-amber-700', bgClass: 'bg-amber-50/30', borderClass: 'border-amber-200' },
  { name: '10. Escalation Criteria',
    iconName: 'Siren',
    accent: 'text-red-700',   bgClass: 'bg-red-50/30',   borderClass: 'border-red-200' },
];

export const ACUITY_META: Record<Acuity, { label: string; className: string }> = {
  EMERGENCY: { label: 'EMERGENCY',  className: 'bg-red-100 text-red-800 border-red-200' },
  URGENT:    { label: 'URGENT',     className: 'bg-amber-100 text-amber-800 border-amber-200' },
  ROUTINE:   { label: 'ROUTINE',    className: 'bg-slate-100 text-slate-700 border-slate-200' },
  CHRONIC:   { label: 'CHRONIC',    className: 'bg-teal-100 text-teal-800 border-teal-200' },
};

/**
 * Normalize a section name for fuzzy matching against `sections` keys.
 * DeepSeek occasionally returns curly quotes / extra spaces; we don't want
 * to break rendering over minor punctuation drift.
 */
export function normalizeSectionName(s: string): string {
  return s
    .toLowerCase()
    .replace(/[\u201c\u201d\u2018\u2019]/g, '"') // curly quotes -> straight
    .replace(/[\u2013\u2014]/g, '-')             // en/em dash -> hyphen
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * Look up a section's content from `sections` by normalized name match.
 */
export function findSectionContent(
  sections: Record<string, string>,
  metaName: string
): string | undefined {
  const target = normalizeSectionName(metaName);
  // Direct match first
  if (sections[metaName]) return sections[metaName];
  // Normalized match
  for (const key of Object.keys(sections)) {
    if (normalizeSectionName(key) === target) return sections[key];
  }
  return undefined;
}
