'use client';

/*
 * Shared interactive MCQ quiz UI: angle filter, shuffled deck, scoring,
 * answer reveal + explanation, results screen. Takes an already-loaded
 * question list — callers (TopicQuiz, SystemQuizView) handle fetching.
 */

import { useEffect, useMemo, useState } from 'react';
import { Check, X, RotateCcw, ChevronRight, Trophy } from 'lucide-react';
import type { QuizQuestion } from '@/lib/types';

const ANGLE_LABELS: Record<string, string> = {
  recognise: 'Recognise',
  diagnose: 'Diagnose',
  treat: 'Treat',
  next_step: 'Next step',
  red_flag: 'Red flag',
};

const ANGLE_ORDER = ['recognise', 'diagnose', 'treat', 'next_step', 'red_flag'];

const DIFFICULTY_STYLE: Record<string, string> = {
  easy: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  medium: 'bg-amber-100 text-amber-800 border-amber-200',
  hard: 'bg-red-100 text-red-800 border-red-200',
};

const LETTERS = ['A', 'B', 'C', 'D', 'E'];

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export default function QuizRunner({ questions }: { questions: QuizQuestion[] }) {
  const [angle, setAngle] = useState<string>('all');
  const [deck, setDeck] = useState<QuizQuestion[]>([]);
  const [idx, setIdx] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [score, setScore] = useState(0);
  const [finished, setFinished] = useState(false);

  // A deck spanning >1 topic (system-wide practice) reveals which topic a
  // question was about only AFTER answering — showing it beforehand would
  // give away "recognise the diagnosis" questions for free.
  const multiTopic = useMemo(() => new Set(questions.map((q) => q.topic)).size > 1, [questions]);

  const angleCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    questions.forEach((q) => {
      counts[q.angle] = (counts[q.angle] ?? 0) + 1;
    });
    return counts;
  }, [questions]);

  function buildDeck(source: QuizQuestion[]) {
    setDeck(shuffle(source));
    setIdx(0);
    setSelected(null);
    setScore(0);
    setFinished(false);
  }

  // Reset the angle filter whenever the question pool itself changes (new topic/system).
  useEffect(() => {
    setAngle('all');
  }, [questions]);

  // Rebuild the shuffled deck whenever the pool or the angle filter changes.
  useEffect(() => {
    const filtered = angle === 'all' ? questions : questions.filter((q) => q.angle === angle);
    buildDeck(filtered);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [questions, angle]);

  const current = deck[idx];

  function answer(i: number) {
    if (selected !== null || !current) return;
    setSelected(i);
    if (i === current.answerIndex) setScore((s) => s + 1);
  }

  function next() {
    if (idx + 1 >= deck.length) {
      setFinished(true);
      return;
    }
    setIdx(idx + 1);
    setSelected(null);
  }

  return (
    <div>
      {/* Angle filter */}
      <div className="mb-5 flex flex-wrap gap-2">
        <AngleChip active={angle === 'all'} onClick={() => setAngle('all')}>
          All ({questions.length})
        </AngleChip>
        {ANGLE_ORDER.filter((a) => angleCounts[a]).map((a) => (
          <AngleChip key={a} active={angle === a} onClick={() => setAngle(a)}>
            {ANGLE_LABELS[a]} ({angleCounts[a]})
          </AngleChip>
        ))}
      </div>

      {finished ? (
        <ResultCard score={score} total={deck.length} onRestart={() => buildDeck(deck)} />
      ) : current ? (
        <div className="max-w-2xl">
          {/* Progress */}
          <div className="mb-3 flex items-center justify-between text-sm text-slate-500">
            <span>
              Question {idx + 1} of {deck.length}
            </span>
            <span>
              Score: <span className="font-semibold text-slate-900">{score}</span>
            </span>
          </div>
          <div className="mb-6 h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
            <div
              className="h-full rounded-full bg-slate-900 transition-all"
              style={{ width: `${((idx + (selected !== null ? 1 : 0)) / deck.length) * 100}%` }}
            />
          </div>

          {/* Card */}
          <div className="rounded-lg border border-slate-200 bg-white p-5 sm:p-6">
            <div className="mb-4 flex items-center gap-2 flex-wrap">
              <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-0.5 text-xs font-medium text-slate-600">
                {ANGLE_LABELS[current.angle] ?? current.angle}
              </span>
              <span
                className={`rounded-md border px-2 py-0.5 text-xs font-medium capitalize ${
                  DIFFICULTY_STYLE[current.difficulty] ?? 'bg-slate-100 text-slate-700 border-slate-200'
                }`}
              >
                {current.difficulty}
              </span>
              {multiTopic && selected !== null && (
                <span className="rounded-md border border-slate-200 bg-white px-2 py-0.5 text-xs font-medium text-slate-500">
                  {current.topic}
                </span>
              )}
            </div>

            <p className="text-[15px] leading-relaxed text-slate-900">{current.stem}</p>

            {/* Options */}
            <div className="mt-5 space-y-2.5">
              {current.options.map((opt, i) => {
                const isCorrect = i === current.answerIndex;
                const isSelected = i === selected;
                const answered = selected !== null;

                let cls = 'border-slate-200 bg-white hover:border-slate-400 hover:shadow-sm';
                if (answered && isCorrect) cls = 'border-emerald-300 bg-emerald-50';
                else if (answered && isSelected) cls = 'border-red-300 bg-red-50';
                else if (answered) cls = 'border-slate-200 bg-white opacity-50';

                return (
                  <button
                    key={i}
                    onClick={() => answer(i)}
                    disabled={answered}
                    className={`flex w-full items-start gap-3 rounded-lg border px-4 py-3 text-left text-sm transition-all ${cls} ${
                      answered ? 'cursor-default' : 'cursor-pointer'
                    }`}
                  >
                    <span
                      className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border text-xs font-semibold ${
                        answered && isCorrect
                          ? 'border-emerald-500 bg-emerald-500 text-white'
                          : answered && isSelected
                          ? 'border-red-500 bg-red-500 text-white'
                          : 'border-slate-300 text-slate-500'
                      }`}
                    >
                      {answered && isCorrect ? (
                        <Check className="h-3 w-3" />
                      ) : answered && isSelected ? (
                        <X className="h-3 w-3" />
                      ) : (
                        LETTERS[i]
                      )}
                    </span>
                    <span className="text-slate-900">{opt}</span>
                  </button>
                );
              })}
            </div>

            {/* Explanation */}
            {selected !== null && (
              <div className="mt-5 rounded-lg bg-slate-50 border border-slate-100 p-4">
                <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">
                  {selected === current.answerIndex ? 'Correct' : 'Explanation'}
                </p>
                <p className="text-sm leading-relaxed text-slate-700">{current.explanation}</p>
              </div>
            )}
          </div>

          {/* Next */}
          {selected !== null && (
            <div className="mt-4 flex justify-end">
              <button
                onClick={next}
                className="inline-flex items-center gap-1.5 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90"
              >
                {idx + 1 >= deck.length ? 'Finish' : 'Next'}
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>
      ) : (
        <p className="text-sm text-slate-400">No questions in this filter.</p>
      )}
    </div>
  );
}

function AngleChip({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
        active
          ? 'border-slate-900 bg-slate-900 text-white'
          : 'border-slate-200 bg-white text-slate-500 hover:bg-slate-50'
      }`}
    >
      {children}
    </button>
  );
}

function ResultCard({
  score,
  total,
  onRestart,
}: {
  score: number;
  total: number;
  onRestart: () => void;
}) {
  const pct = total ? Math.round((score / total) * 100) : 0;
  return (
    <div className="max-w-md rounded-lg border border-slate-200 bg-white p-8 text-center">
      <Trophy className="mx-auto h-10 w-10 text-amber-500" />
      <p className="mt-3 text-3xl font-bold text-slate-900">
        {score} / {total}
      </p>
      <p className="mt-1 text-slate-500">{pct}% correct</p>
      <button
        onClick={onRestart}
        className="mt-6 inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50"
      >
        <RotateCcw className="h-4 w-4" /> Restart
      </button>
    </div>
  );
}
