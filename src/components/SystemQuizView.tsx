'use client';

/*
 * "Practice all" quiz for an entire system: merges every topic's question
 * set within that system into one shuffled pool. Entry point lives on
 * SystemDashboard (see page.tsx).
 */

import { useEffect, useRef, useState } from 'react';
import { ChevronRight, Loader2, HelpCircle } from 'lucide-react';
import type { QuestionSet, QuizManifestEntry, QuizQuestion } from '@/lib/types';
import QuizRunner from '@/components/QuizRunner';

export default function SystemQuizView({ system, onBack }: { system: string; onBack: () => void }) {
  const [questions, setQuestions] = useState<QuizQuestion[] | null>(null);
  const [topicCount, setTopicCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const cacheRef = useRef<Map<string, { questions: QuizQuestion[]; topicCount: number }>>(new Map());

  useEffect(() => {
    setError(null);

    const cached = cacheRef.current.get(system);
    if (cached) {
      setQuestions(cached.questions);
      setTopicCount(cached.topicCount);
      setLoading(false);
      return;
    }

    setLoading(true);
    setQuestions(null);
    let cancelled = false;

    fetch('/data/questions-manifest.json')
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((manifest: QuizManifestEntry[]) => {
        const slugs = manifest.filter((m) => m.system === system).map((m) => m.slug);
        if (slugs.length === 0) throw new Error(`No quiz topics found for ${system}`);
        return Promise.all(
          slugs.map((slug) =>
            fetch(`/data/questions/${slug}.json`).then((r) => {
              if (!r.ok) throw new Error(`HTTP ${r.status} for ${slug}`);
              return r.json() as Promise<QuestionSet>;
            })
          )
        );
      })
      .then((sets) => {
        if (cancelled) return;
        const merged = sets.flatMap((s) => s.questions);
        cacheRef.current.set(system, { questions: merged, topicCount: sets.length });
        setQuestions(merged);
        setTopicCount(sets.length);
        setLoading(false);
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err.message);
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [system]);

  return (
    <div className="flex-1 max-w-[900px] mx-auto w-full px-4 sm:px-6 py-6 sm:py-8">
      <button
        onClick={onBack}
        className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-900 mb-6 transition-colors"
      >
        <ChevronRight className="w-4 h-4 rotate-180" />
        {system}
      </button>

      <h1 className="text-xl sm:text-2xl font-bold text-slate-900 mb-1">{system} — Practice All</h1>
      <p className="text-sm text-slate-500 mb-6">
        {loading ? 'Loading…' : `${questions?.length ?? 0} questions shuffled across ${topicCount} topics`}
      </p>

      {loading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
          <span className="ml-2 text-sm text-slate-500">Loading questions&hellip;</span>
        </div>
      ) : error || !questions ? (
        <div className="flex items-center justify-center py-16">
          <div className="text-center max-w-sm">
            <HelpCircle className="w-8 h-8 text-slate-300 mx-auto mb-3" />
            <p className="text-sm font-medium text-slate-600">Couldn&rsquo;t load quiz</p>
            <p className="mt-1 text-xs text-slate-400">{error}</p>
          </div>
        </div>
      ) : (
        <QuizRunner questions={questions} />
      )}
    </div>
  );
}
