'use client';

import { useMemo, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Stethoscope,
  GitBranch,
  Microscope,
  ClipboardList,
  Pill,
  AlertTriangle,
  Activity,
  Lightbulb,
  Siren,
  Eye,
  BookOpen,
  Brain,
  Tags,
  Search,
  Heart,
  FileText,
  Bookmark,
  ChevronRight,
  Tag,
  StickyNote,
  Clock,
  Zap,
  GraduationCap,
  Hospital,
  Skull,
  AlertOctagon,
  ShieldAlert,
  Menu,
  X,
} from 'lucide-react';

import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';

import { TOPIC_BUNDLES, TOPICS_BY_SYSTEM, SYSTEMS_ORDERED } from '@/data/manifest';
import {
  ACUITY_META,
  WARD_SECTION_META,
  STUDY_SECTION_META,
  findSectionContent,
  type ClinicalEntry,
  type EntryMode,
  type SectionMeta,
  type Acuity,
} from '@/lib/types';

const ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  Stethoscope,
  GitBranch,
  Microscope,
  ClipboardList,
  Pill,
  AlertTriangle,
  Activity,
  Lightbulb,
  Siren,
  Eye,
  BookOpen,
  Brain,
  Tags,
  Skull,
  AlertOctagon,
  ShieldAlert,
};

interface TopicListItem {
  slug: string;
  title: string;
  system: string;
  subSystem: string;
  acuity: Acuity;
  highYield: boolean;
}

export default function Home() {
  const [query, setQuery] = useState('');
  const [notesByTopic, setNotesByTopic] = useState<Record<string, string>>({});
  const [bookmarks, setBookmarks] = useState<Record<string, boolean>>({});
  const [mode, setMode] = useState<EntryMode>('WARD');
  const [activeSlug, setActiveSlug] = useState<string | null>(null);
  const [selectedSystem, setSelectedSystem] = useState<string | null>(null);

  // Mobile sheet state
  const [topicsSheetOpen, setTopicsSheetOpen] = useState(false);
  const [notesSheetOpen, setNotesSheetOpen] = useState(false);

  const bundle = activeSlug ? TOPIC_BUNDLES[activeSlug] : null;
  const entry: ClinicalEntry | null = bundle
    ? (mode === 'WARD' ? bundle.ward : bundle.study)
    : null;
  const sectionMeta: SectionMeta[] = mode === 'WARD' ? WARD_SECTION_META : STUDY_SECTION_META;

  const filteredGroups = useMemo(() => {
    if (!query.trim()) {
      return SYSTEMS_ORDERED.map((sys) => ({
        system: sys,
        topics: TOPICS_BY_SYSTEM[sys] as TopicListItem[],
      }));
    }
    const q = query.toLowerCase();
    return SYSTEMS_ORDERED
      .map((sys) => ({
        system: sys,
        topics: (TOPICS_BY_SYSTEM[sys] as TopicListItem[]).filter(
          (t) =>
            t.title.toLowerCase().includes(q) ||
            t.system.toLowerCase().includes(q) ||
            t.subSystem.toLowerCase().includes(q)
        ),
      }))
      .filter((g) => g.topics.length > 0);
  }, [query]);

  const totalTopics = Object.keys(TOPIC_BUNDLES).length;
  const totalSystems = SYSTEMS_ORDERED.length;
  const notes = activeSlug ? (notesByTopic[activeSlug] || '') : '';
  const bookmarked = activeSlug ? !!bookmarks[activeSlug] : false;

  const handleSelectTopic = (slug: string) => {
    setActiveSlug(slug);
    setSelectedSystem(null);
    setQuery('');
    setTopicsSheetOpen(false);
  };

  const handleSelectSystem = (system: string) => {
    setSelectedSystem(system);
    setActiveSlug(null);
    setQuery('');
  };

  const handleLogoClick = () => {
    setActiveSlug(null);
    setSelectedSystem(null);
  };

  const handleNotesChange = (val: string) => {
    setNotesByTopic((prev) => ({ ...prev, [activeSlug]: val }));
  };

  const handleBookmark = () => {
    setBookmarks((prev) => ({ ...prev, [activeSlug]: !prev[activeSlug] }));
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
      <Header
        query={query}
        setQuery={setQuery}
        totalTopics={totalTopics}
        onOpenTopics={() => setTopicsSheetOpen(true)}
        onOpenNotes={() => setNotesSheetOpen(true)}
        onLogoClick={handleLogoClick}
        isHome={!activeSlug && !selectedSystem}
      />

      {!activeSlug && !selectedSystem ? (
        <Dashboard
          totalTopics={totalTopics}
          totalSystems={totalSystems}
          filteredGroups={filteredGroups}
          query={query}
          onSelectSystem={handleSelectSystem}
          bookmarks={bookmarks}
        />
      ) : !activeSlug && selectedSystem ? (
        <SystemDashboard
          system={selectedSystem}
          topics={(TOPICS_BY_SYSTEM[selectedSystem] || []) as TopicListItem[]}
          bookmarks={bookmarks}
          onSelectTopic={handleSelectTopic}
          onBack={() => setSelectedSystem(null)}
        />
      ) : (
        <div className="flex-1 max-w-[1600px] mx-auto w-full px-3 sm:px-6 py-4 grid grid-cols-1 lg:grid-cols-[260px_1fr_320px] gap-4">
          {/* LEFT SIDEBAR (desktop only) */}
          <aside className="hidden lg:block bg-white rounded-lg border border-slate-200 p-3 h-[calc(100vh-140px)] overflow-hidden flex flex-col">
            <TopicBrowser
              filteredGroups={filteredGroups}
              query={query}
              activeSlug={activeSlug}
              bookmarks={bookmarks}
              onSelectTopic={handleSelectTopic}
              totalTopics={totalTopics}
            />
          </aside>

          {/* CENTER — Entry viewer */}
          <main className="bg-white rounded-lg border border-slate-200 overflow-hidden flex flex-col min-h-[60vh] lg:min-h-0">
            <EntryHeader
              entry={entry!}
              mode={mode}
              setMode={setMode}
              bookmarked={bookmarked}
              setBookmarked={handleBookmark}
            />
            <div className="flex-1 overflow-y-auto custom-scroll px-4 sm:px-8 py-5 sm:py-6">
              <EntryBody entry={entry!} sectionMeta={sectionMeta} />
            </div>
          </main>

          {/* RIGHT SIDEBAR (desktop only) */}
          <aside className="hidden lg:block bg-white rounded-lg border border-slate-200 p-3 h-[calc(100vh-140px)] overflow-hidden flex flex-col">
            <NotesPanel
              entry={entry!}
              notes={notes}
              onNotesChange={handleNotesChange}
              mode={mode}
            />
          </aside>
        </div>
      )}

      {/* MOBILE TOPICS SHEET */}
      <Sheet open={topicsSheetOpen} onOpenChange={setTopicsSheetOpen}>
        <SheetContent side="left" className="w-[85vw] max-w-sm p-0 bg-white">
          <SheetHeader className="px-4 py-3 border-b border-slate-100 flex-row items-center justify-between space-y-0">
            <SheetTitle className="text-sm font-semibold text-slate-700 flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-slate-500" />
              Topics by System
            </SheetTitle>
            <span className="text-[10px] text-slate-400 font-medium">
              {totalTopics} {totalTopics === 1 ? 'topic' : 'topics'}
            </span>
          </SheetHeader>
          <div className="flex-1 overflow-y-auto custom-scroll h-[calc(100vh-100px)]">
            <TopicBrowser
              filteredGroups={filteredGroups}
              query={query}
              activeSlug={activeSlug}
              bookmarks={bookmarks}
              onSelectTopic={handleSelectTopic}
              totalTopics={totalTopics}
            />
          </div>
        </SheetContent>
      </Sheet>

      {/* MOBILE NOTES SHEET */}
      <Sheet open={notesSheetOpen} onOpenChange={setNotesSheetOpen}>
        <SheetContent side="right" className="w-[90vw] max-w-md p-0 bg-white">
          <SheetHeader className="px-4 py-3 border-b border-slate-100 flex-row items-center justify-between space-y-0">
            <SheetTitle className="text-sm font-semibold text-slate-700 flex items-center gap-2">
              <StickyNote className="w-4 h-4 text-slate-500" />
              My Notes
            </SheetTitle>
            <span className="text-[10px] text-slate-400 truncate max-w-[150px]">
              {entry ? `· ${entry.title}` : ''}
            </span>
          </SheetHeader>
          <div className="p-4 h-[calc(100vh-100px)] overflow-y-auto custom-scroll">
            {entry && (
              <NotesPanel
                entry={entry}
                notes={notes}
                onNotesChange={handleNotesChange}
                mode={mode}
                fillHeight
              />
            )}
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* DASHBOARD — home page when no topic is selected                      */
/* ------------------------------------------------------------------ */

function Dashboard({
  totalTopics,
  totalSystems,
  filteredGroups,
  query,
  onSelectSystem,
  bookmarks,
}: {
  totalTopics: number;
  totalSystems: number;
  filteredGroups: { system: string; topics: TopicListItem[] }[];
  query: string;
  onSelectSystem: (system: string) => void;
  bookmarks: Record<string, boolean>;
}) {
  const HIGH_YIELD_COUNT = Object.values(TOPICS_BY_SYSTEM)
    .flat()
    .filter((t) => t.highYield).length;

  return (
    <div className="flex-1 max-w-[1100px] mx-auto w-full px-4 sm:px-6 py-6 sm:py-10">
      {/* Hero */}
      <div className="text-center mb-8 sm:mb-12">
        <div className="inline-flex items-center justify-center w-14 h-14 sm:w-16 sm:h-16 rounded-xl bg-slate-900 text-white mb-5 shadow-lg shadow-slate-200">
          <Heart className="w-7 h-7 sm:w-8 sm:h-8 fill-white" />
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 mb-2">
          Clinical Handbook
        </h1>
        <p className="text-sm sm:text-base text-slate-500 max-w-lg mx-auto leading-relaxed">
          The 20% of medicine that covers 80% of ward work. Built by a junior doctor, for junior doctors.
        </p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-3 sm:gap-4 mb-8">
        <div className="bg-white rounded-lg border border-slate-200 p-4 text-center">
          <div className="text-2xl sm:text-3xl font-bold text-slate-900">{totalTopics}</div>
          <div className="text-[11px] sm:text-xs text-slate-500 mt-0.5">Topics</div>
        </div>
        <div className="bg-white rounded-lg border border-slate-200 p-4 text-center">
          <div className="text-2xl sm:text-3xl font-bold text-slate-900">{totalSystems}</div>
          <div className="text-[11px] sm:text-xs text-slate-500 mt-0.5">Systems</div>
        </div>
        <div className="bg-white rounded-lg border border-slate-200 p-4 text-center">
          <div className="text-2xl sm:text-3xl font-bold text-amber-600">{HIGH_YIELD_COUNT}</div>
          <div className="text-[11px] sm:text-xs text-slate-500 mt-0.5">High-Yield</div>
        </div>
      </div>

      {/* Systems grid */}
      <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4">
        Browse by System
      </h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2 sm:gap-3">
        {(query ? filteredGroups : SYSTEMS_ORDERED.map((sys) => ({
          system: sys,
          topics: TOPICS_BY_SYSTEM[sys] as TopicListItem[],
        }))).map((group) => (
          <button
            key={group.system}
            onClick={() => onSelectSystem(group.system)}
            className="bg-white rounded-lg border border-slate-200 p-3 sm:p-4 text-left hover:border-slate-400 hover:shadow-sm transition-all group"
          >
            <div className="text-xs sm:text-sm font-semibold text-slate-800 group-hover:text-slate-900 leading-tight mb-1">
              {group.system}
            </div>
            <div className="text-[10px] sm:text-[11px] text-slate-400">
              {group.topics.length} {group.topics.length === 1 ? 'topic' : 'topics'}
            </div>
          </button>
        ))}
        {query && filteredGroups.length === 0 && (
          <div className="col-span-full text-center py-10 text-sm text-slate-400">
            No systems match &ldquo;{query}&rdquo;
          </div>
        )}
      </div>

      {/* Footer hint */}
      <p className="text-center text-[11px] text-slate-400 mt-10">
        Select a system to browse topics, or search above.
      </p>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* SYSTEM DASHBOARD — shows topics within a selected system             */
/* ------------------------------------------------------------------ */

function SystemDashboard({
  system,
  topics,
  bookmarks,
  onSelectTopic,
  onBack,
}: {
  system: string;
  topics: TopicListItem[];
  bookmarks: Record<string, boolean>;
  onSelectTopic: (slug: string) => void;
  onBack: () => void;
}) {
  return (
    <div className="flex-1 max-w-[900px] mx-auto w-full px-4 sm:px-6 py-6 sm:py-8">
      {/* Back + title */}
      <button
        onClick={onBack}
        className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-900 mb-6 transition-colors"
      >
        <ChevronRight className="w-4 h-4 rotate-180" />
        All Systems
      </button>
      <h1 className="text-xl sm:text-2xl font-bold text-slate-900 mb-1">{system}</h1>
      <p className="text-sm text-slate-500 mb-6">
        {topics.length} {topics.length === 1 ? 'topic' : 'topics'}
      </p>

      {/* Topic list */}
      <div className="space-y-2">
        {topics.map((t) => {
          const isBookmarked = !!bookmarks[t.slug];
          return (
            <button
              key={t.slug}
              onClick={() => onSelectTopic(t.slug)}
              className="w-full text-left bg-white rounded-lg border border-slate-200 p-4 hover:border-slate-400 hover:shadow-sm transition-all flex items-center gap-4 group"
            >
              <div className="flex-1 min-w-0">
                <div className="text-sm font-semibold text-slate-800 group-hover:text-slate-900 flex items-center gap-2">
                  <span className="truncate">{t.title}</span>
                  {isBookmarked && (
                    <Bookmark className="w-3.5 h-3.5 flex-shrink-0 fill-amber-500 text-amber-500" />
                  )}
                </div>
                {t.subSystem && (
                  <div className="text-[11px] text-slate-400 mt-0.5">{t.subSystem}</div>
                )}
              </div>
              <div className="flex items-center gap-1.5 flex-shrink-0">
                <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium border ${ACUITY_META[t.acuity].className}`}>
                  {t.acuity}
                </span>
                {t.highYield && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded font-medium bg-amber-50 text-amber-700 border border-amber-200 flex items-center gap-0.5">
                    <Zap className="w-2.5 h-2.5" /> HY
                  </span>
                )}
                <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-slate-500" />
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* TOPIC BROWSER (shared between desktop sidebar + mobile sheet)       */
/* ------------------------------------------------------------------ */

function TopicBrowser({
  filteredGroups,
  query,
  activeSlug,
  bookmarks,
  onSelectTopic,
  totalTopics,
}: {
  filteredGroups: { system: string; topics: TopicListItem[] }[];
  query: string;
  activeSlug: string;
  bookmarks: Record<string, boolean>;
  onSelectTopic: (slug: string) => void;
  totalTopics: number;
}) {
  return (
    <>
      <div className="flex items-center gap-2 px-1 pb-3 border-b border-slate-100 lg:flex">
        <BookOpen className="w-4 h-4 text-slate-500" />
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          Topics by System
        </span>
        <span className="ml-auto text-[10px] text-slate-400 font-medium">
          {totalTopics} {totalTopics === 1 ? 'topic' : 'topics'}
        </span>
      </div>

      <div className="flex-1 overflow-y-auto mt-2 -mx-1 px-1 custom-scroll">
        {filteredGroups.map((group) => (
          <div key={group.system} className="mb-3">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 px-2 py-1.5">
              {group.system}
            </div>
            <ul className="space-y-0.5">
              {group.topics.map((t) => {
                const isActive = t.slug === activeSlug;
                const isBookmarked = !!bookmarks[t.slug];
                return (
                  <li key={t.slug}>
                    <button
                      onClick={() => onSelectTopic(t.slug)}
                      className={`w-full text-left px-2 py-1.5 rounded-md group flex items-start gap-2 transition-colors ${
                        isActive
                          ? 'bg-slate-900 text-white'
                          : 'hover:bg-slate-100 text-slate-900'
                      }`}
                    >
                      <ChevronRight
                        className={`w-3.5 h-3.5 mt-0.5 flex-shrink-0 ${
                          isActive ? 'text-slate-300' : 'text-slate-400 group-hover:text-slate-600'
                        }`}
                      />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium leading-tight flex items-center gap-1.5">
                          <span className="truncate">{t.title}</span>
                          {isBookmarked && (
                            <Bookmark
                              className={`w-3 h-3 flex-shrink-0 fill-current ${
                                isActive ? 'text-amber-300' : 'text-amber-500'
                              }`}
                            />
                          )}
                        </div>
                        <div className="flex items-center gap-1.5 mt-1 flex-wrap">
                          <span
                            className={`text-[10px] px-1.5 py-0.5 rounded font-medium border ${
                              isActive
                                ? 'bg-white/15 text-white border-white/20'
                                : ACUITY_META[t.acuity].className
                            }`}
                          >
                            {t.acuity}
                          </span>
                          {t.highYield && (
                            <span
                              className={`text-[10px] px-1.5 py-0.5 rounded font-medium flex items-center gap-0.5 border ${
                                isActive
                                  ? 'bg-white/15 text-white border-white/20'
                                  : 'bg-amber-50 text-amber-700 border-amber-200'
                              }`}
                            >
                              <Zap className="w-2.5 h-2.5" /> HY
                            </span>
                          )}
                          {t.subSystem && (
                            <span
                              className={`text-[10px] truncate ${
                                isActive ? 'text-slate-300' : 'text-slate-400'
                              }`}
                            >
                              · {t.subSystem}
                            </span>
                          )}
                        </div>
                      </div>
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
        {filteredGroups.length === 0 && (
          <div className="text-xs text-slate-400 px-2 py-6 text-center">
            No topics found for &ldquo;{query}&rdquo;
          </div>
        )}
      </div>

    </>
  );
}

/* ------------------------------------------------------------------ */
/* NOTES PANEL (shared between desktop sidebar + mobile sheet)         */
/* ------------------------------------------------------------------ */

function NotesPanel({
  entry,
  notes,
  onNotesChange,
  mode,
  fillHeight = false,
}: {
  entry: ClinicalEntry;
  notes: string;
  onNotesChange: (v: string) => void;
  mode: EntryMode;
  fillHeight?: boolean;
}) {
  return (
    <div className={`flex flex-col ${fillHeight ? 'h-full' : 'h-full'}`}>
      <div className="flex items-center gap-2 px-1 pb-3 border-b border-slate-100">
        <StickyNote className="w-4 h-4 text-slate-500" />
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          My Notes
        </span>
        <span className="ml-auto text-[10px] text-slate-400 truncate max-w-[120px]">
          · {entry.title}
        </span>
      </div>

      <textarea
        value={notes}
        onChange={(e) => onNotesChange(e.target.value)}
        placeholder={`Add your own annotations for ${entry.title}…\n\n(e.g. saw a case on ward 7, treated with X, responded well)`}
        className="flex-1 mt-2 w-full resize-none rounded-md border border-slate-200 p-2 text-xs font-mono text-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-300 placeholder:text-slate-400 min-h-[200px]"
      />

    </div>
  );
}

/* ------------------------------------------------------------------ */
/* HEADER — with mobile menu + notes buttons                          */
/* ------------------------------------------------------------------ */

function Header({
  query,
  setQuery,
  totalTopics,
  onOpenTopics,
  onOpenNotes,
  onLogoClick,
  isHome,
}: {
  query: string;
  setQuery: (v: string) => void;
  totalTopics: number;
  onOpenTopics: () => void;
  onOpenNotes: () => void;
  onLogoClick: () => void;
  isHome: boolean;
}) {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
      <div className="max-w-[1600px] mx-auto px-3 sm:px-6 py-3 flex items-center gap-2 sm:gap-4">
        {/* Mobile menu button */}
        <button
          onClick={onOpenTopics}
          className="lg:hidden p-2 -ml-1 rounded-md text-slate-600 hover:bg-slate-100 flex-shrink-0"
          aria-label="Open topics menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <button
          onClick={onLogoClick}
          className="flex items-center gap-2 flex-shrink-0 hover:opacity-80 transition-opacity rounded-md -ml-1 px-1 py-0.5"
          aria-label="Go to home page"
        >
          <div className="w-8 h-8 rounded-md bg-slate-900 text-white flex items-center justify-center">
            <Heart className="w-4 h-4 fill-white" />
          </div>
          <div className="hidden sm:block text-left">
            <div className="text-sm font-semibold text-slate-900 leading-tight">Clinical Handbook</div>
            <div className="text-[10px] text-slate-500 leading-tight">Personal medical reference</div>
          </div>
        </button>

        <div className="flex-1 max-w-xl relative min-w-0">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search topics…"
            className="w-full pl-9 pr-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-300 focus:bg-white placeholder:text-slate-400"
          />
        </div>

        {/* Mobile notes button */}
        <button
          onClick={onOpenNotes}
          className="lg:hidden p-2 rounded-md text-slate-600 hover:bg-slate-100 flex-shrink-0"
          aria-label="Open notes"
        >
          <StickyNote className="w-5 h-5" />
        </button>

      </div>
    </header>
  );
}

/* ------------------------------------------------------------------ */
/* ENTRY HEADER                                                        */
/* ------------------------------------------------------------------ */

function EntryHeader({
  entry,
  mode,
  setMode,
  bookmarked,
  setBookmarked,
}: {
  entry: ClinicalEntry;
  mode: EntryMode;
  setMode: (m: EntryMode) => void;
  bookmarked: boolean;
  setBookmarked: () => void;
}) {
  const acuity = ACUITY_META[entry.acuity];
  return (
    <div className="border-b border-slate-200 bg-gradient-to-b from-slate-50 to-white px-4 sm:px-8 py-4 sm:py-5">
      <div className="flex items-center gap-2 text-[11px] text-slate-500 mb-2 flex-wrap">
        <span className="font-medium uppercase tracking-wider">{entry.system}</span>
        {entry.subSystem && (
          <>
            <ChevronRight className="w-3 h-3" />
            <span>{entry.subSystem}</span>
          </>
        )}
      </div>
      <div className="flex items-start justify-between gap-3 sm:gap-4 flex-wrap">
        <div className="flex-1 min-w-0">
          <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-slate-900 leading-tight">
            {entry.title}
          </h1>
          <p className="mt-2 text-sm text-slate-600 leading-relaxed">
            {entry.oneLiner}
          </p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <span className={`text-[11px] px-2.5 py-1 rounded-md border font-semibold ${acuity.className}`}>
            {acuity.label}
          </span>
          <button
            onClick={setBookmarked}
            className={`p-2 rounded-md border transition-colors ${
              bookmarked
                ? 'bg-amber-50 border-amber-300 text-amber-600'
                : 'bg-white border-slate-200 text-slate-400 hover:text-slate-600 hover:bg-slate-50'
            }`}
            aria-label={bookmarked ? 'Remove bookmark' : 'Bookmark this topic'}
          >
            <Bookmark className={`w-4 h-4 ${bookmarked ? 'fill-amber-500' : ''}`} />
          </button>
        </div>
      </div>

      <div className="mt-4 flex items-center gap-2">
        <ModeToggle mode={mode} setMode={setMode} />
      </div>
    </div>
  );
}

function ModeToggle({ mode, setMode }: { mode: EntryMode; setMode: (m: EntryMode) => void }) {
  return (
    <div className="inline-flex p-0.5 rounded-md bg-slate-100 border border-slate-200 text-xs font-medium w-full sm:w-auto">
      <button
        onClick={() => setMode('WARD')}
        className={`flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-sm transition-colors flex-1 sm:flex-initial ${
          mode === 'WARD'
            ? 'bg-white text-slate-900 shadow-sm'
            : 'text-slate-500 hover:text-slate-700'
        }`}
      >
        <Hospital className="w-3.5 h-3.5" />
        <span>Ward</span>
        <span className="hidden sm:inline text-[10px] text-slate-400 font-normal">· scannable</span>
      </button>
      <button
        onClick={() => setMode('STUDY')}
        className={`flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-sm transition-colors flex-1 sm:flex-initial ${
          mode === 'STUDY'
            ? 'bg-white text-slate-900 shadow-sm'
            : 'text-slate-500 hover:text-slate-700'
        }`}
      >
        <GraduationCap className="w-3.5 h-3.5" />
        <span>Study</span>
        <span className="hidden sm:inline text-[10px] text-slate-400 font-normal">· deep</span>
      </button>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* ENTRY BODY                                                          */
/* ------------------------------------------------------------------ */

function EntryBody({
  entry,
  sectionMeta,
}: {
  entry: ClinicalEntry;
  sectionMeta: SectionMeta[];
}) {
  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      {sectionMeta.map((meta) => {
        const content = findSectionContent(entry.sections, meta.name);
        if (!content) return null;
        const Icon = ICONS[meta.iconName] || Stethoscope;
        const cardBorder = meta.borderClass || 'border-slate-200';
        const cardBg = meta.bgClass || 'bg-white';
        return (
          <section
            key={meta.name}
            className={`rounded-lg border p-4 sm:p-5 ${cardBorder} ${cardBg}`}
          >
            <div className="flex items-center gap-2 mb-3">
              <Icon className={`w-4 h-4 ${meta.accent}`} />
              <h2 className={`text-sm font-semibold uppercase tracking-wider ${meta.accent}`}>
                {meta.name}
              </h2>
            </div>
            <div className="prose-clinical">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
            </div>
          </section>
        );
      })}

      <div className="pt-4 border-t border-slate-100 text-center">
        <p className="text-[11px] text-slate-400">
          {entry.metadata?.mode === 'STUDY' ? 'Study mode' : 'Ward mode'} · Generated by {entry.metadata?.model} ·{' '}
          {entry.metadata?.tokensUsed?.total_tokens.toLocaleString()} tokens ·{' '}
          {entry.metadata?.generatedAt?.slice(0, 10)}
        </p>
        <p className="text-[11px] text-slate-400 mt-1">
          Always verify dosing and protocols against local guidelines. AI-generated content may contain errors.
        </p>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* MISC                                                                */
/* ------------------------------------------------------------------ */

