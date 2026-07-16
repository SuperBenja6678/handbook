"""
Generate pattern-recognition MCQs for a topic, grounded in that topic's existing
STUDY + WARD entry JSON (so answers never contradict the handbook).

Each topic produces questions across 5 clinical ANGLES:
  recognise   - single most likely diagnosis (distractors = the real mimics)
  diagnose    - best investigation / interpret a result / never-miss test
  treat       - first-line management (incl. "what is contraindicated")
  next_step   - immediate next action under time pressure
  red_flag    - the finding that mandates escalation / the killer to exclude

Usage:
  python scripts/generate_questions.py --slug ulcerative-colitis
  python scripts/generate_questions.py --slug ulcerative-colitis --per-angle 5

Reads DEEPSEEK_API_KEY from the environment or from .env (gitignored).
Writes data/questions/<slug>.json and prints a readable digest.
"""

import argparse
import json
import os
import random
import re
import sys
import time
import uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# Windows consoles default to cp1252 and crash when printing ≥, °, – etc. Force UTF-8.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-v4-flash"
VALID_DIFFICULTY = {"easy", "medium", "hard"}


def load_dotenv():
    """Minimal .env loader (KEY=VALUE). Real env vars win over .env."""
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        os.environ.setdefault(key.strip(), val.strip())


load_dotenv()
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
if not DEEPSEEK_API_KEY:
    print("ERROR: Set DEEPSEEK_API_KEY (environment or .env).", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

MCQ_SYSTEM = (
    "You are an expert medical MCQ author for UK foundation-year doctors. "
    "You write single-best-answer questions that build pattern recognition. "
    "You output ONLY valid JSON — no markdown, no commentary."
)

MCQ_PROMPT = """Write [N] single-best-answer (SBA) questions for a UK foundation-year doctor (FY1/FY2), UKMLA / MRCP style, on:

TOPIC: [TOPIC_TITLE] — [SYSTEM]

QUESTION TYPE — [ANGLE_LABEL]:
[ANGLE_INSTRUCTION]
[REFERENCE_BLOCK]
Rules:
- UK practice only (NICE / BNF; UK drug names, units, spellings). The drug CLASS matters more than the exact dose — name the class or a typical dose, but never invent a precise dose you are unsure of.
- Stay strictly inside the QUESTION TYPE above. Do not drift into other types (a diagnosis question must not ask about treatment; a red-flag question must not ask "what do you do").
- SCENARIO SPREAD: across your [N] questions, deliberately vary the clinical situation — e.g. first presentation, mild-to-moderate disease, acute/severe emergency, a specific complication, and a special population or the maintenance/remission setting. Do NOT write more than one question on the same scenario or complication.
- Each stem is a concise, realistic clinical vignette. Then EXACTLY 5 options. Exactly ONE single best answer.
- Distractors must be plausible NEAR-MISSES: the genuine differentials, mimics, or tempting-but-wrong choices for THIS condition. Never use random, unrelated options.
- OPTIONS MUST BE PARALLEL: all five options are single, discrete answers of comparable scope, form, and length. Never make the correct answer a bundle of several actions while distractors are single actions — if several actions are needed, pick the SINGLE most important one and phrase every option as a single action.
- Avoid clinical equipoise: if two options are equally defensible under UK guidelines (a genuine shared decision), do NOT force a single best answer — write a different question.
- Do NOT write basic-science, mechanism, or "which cytokine / which receptor" trivia. Everything clinical.
- Each explanation must NAME the discriminating feature — why the correct answer beats the most tempting distractor (1-3 sentences).
- Vary difficulty; include at least one harder discriminator or atypical presentation.
- The position of the correct option does not matter — it will be shuffled afterwards. Do not bias toward any particular letter.

Output ONLY this JSON shape (no code fences, no text before or after):
{"questions":[{"stem":"...","options":["opt0","opt1","opt2","opt3","opt4"],"answerIndex":0,"explanation":"...","difficulty":"medium"}]}
"""

ANGLES = {
    "recognise": {
        "label": "Recognise the diagnosis",
        "instruction": (
            "Present a clinical vignette and ask ONLY 'what is the single most likely diagnosis?'. "
            "The five options are this condition plus its closest mimics / differentials. "
            "Do NOT ask about investigations or management. Include at least one atypical or easily-missed presentation."
        ),
    },
    "diagnose": {
        "label": "Diagnose / investigate",
        "instruction": (
            "Ask ONLY about establishing the diagnosis: the single most appropriate investigation to confirm it, "
            "the best NEXT test, the correct INTERPRETATION of a result, or a diagnostic criterion / threshold. "
            "Options are competing investigations or interpretations. Do NOT ask about treatment or escalation. "
            "Use the reference's 'never-miss' test at most ONCE."
        ),
    },
    "treat": {
        "label": "Treat / manage",
        "instruction": (
            "Assume the diagnosis is known. Ask ONLY about definitive therapy: the single most appropriate first-line "
            "treatment for the described disease state, or which drug / therapy is CONTRAINDICATED. Options are competing "
            "treatments (drugs or therapies). Do NOT ask 'what is the immediate next action' — focus on the correct "
            "therapy and why. Use the correct UK drugs and doses from the reference."
        ),
    },
    "next_step": {
        "label": "Next step",
        "instruction": (
            "Give an evolving ward / ED scenario and ask for the SINGLE most appropriate IMMEDIATE next action — which "
            "may be to investigate, treat, resuscitate, reassess, or escalate. The answer must be ONE discrete action, "
            "not a bundle. This is about PRIORITISATION: what to do first among competing reasonable actions. Vary the "
            "scenarios — do not make every question about the same deteriorating patient."
        ),
    },
    "red_flag": {
        "label": "Red flag / can't-miss",
        "instruction": (
            "Focus on RECOGNISING danger, not acting on it. Ask which single FINDING / FEATURE marks this as an "
            "emergency or crosses an escalation threshold, OR which life-threatening complication / mimic the picture "
            "represents. The correct ANSWER must be a clinical finding, a threshold, or a diagnosis to exclude — NOT a "
            "management action. Draw on the reference's 'Killers First', complications, and escalation criteria."
        ),
    },
}


# ---------------------------------------------------------------------------
# DeepSeek call
# ---------------------------------------------------------------------------

def call_deepseek(prompt, *, max_tokens=8000, temperature=0.4, max_retries=3):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": MCQ_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "stream": False,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    }
    req = Request(
        DEEPSEEK_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            with urlopen(req, timeout=180) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            last_error = f"HTTP {e.code}: {body[:200]}"
        except (URLError, Exception) as e:  # noqa: BLE001
            last_error = str(e)
        if attempt < max_retries:
            time.sleep(2 ** attempt)
    raise RuntimeError(f"DeepSeek call failed after {max_retries} attempts: {last_error}")


def extract_json(text):
    """Pull a JSON object out of the model response, tolerating stray fences/prose."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]
    return json.loads(text, strict=False)


# ---------------------------------------------------------------------------
# Grounding + generation
# ---------------------------------------------------------------------------

def load_entry(slug, mode):
    path = PROJECT_ROOT / "data" / "entries" / f"{slug}.{mode}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build_reference(study, ward):
    parts = []
    if study and study.get("rawMarkdown"):
        parts.append("# STUDY NOTES\n" + study["rawMarkdown"])
    if ward and ward.get("rawMarkdown"):
        parts.append("# WARD NOTES\n" + ward["rawMarkdown"])
    return "\n\n".join(parts)


def validate_question(q):
    """Basic structural sanity checks; returns (ok, reason)."""
    if not isinstance(q, dict):
        return False, "not an object"
    opts = q.get("options")
    if not isinstance(opts, list) or len(opts) != 5:
        return False, "options must be a list of 5"
    idx = q.get("answerIndex")
    if not isinstance(idx, int) or not (0 <= idx <= 4):
        return False, "answerIndex out of range"
    if not q.get("stem") or not q.get("explanation"):
        return False, "missing stem/explanation"
    return True, ""


def _norm_text(s):
    return re.sub(r"[^a-z0-9 ]", " ", s.lower())


def dedupe(questions, ans_thresh=0.80, stem_thresh=0.55):
    """Drop near-duplicate questions across the whole set.

    A question is a duplicate when its correct-answer text is highly similar to a
    kept question's (high bar) AND its stem is moderately similar (moderate bar).
    This keeps 'same scenario, different question type' but removes the same
    question reworded. First occurrence (earliest angle) is kept.
    """
    import difflib

    kept, dropped = [], []
    for q in questions:
        ans = _norm_text(q["options"][q["answerIndex"]])
        stem = _norm_text(q["stem"])
        is_dup = False
        for k in kept:
            k_ans = _norm_text(k["options"][k["answerIndex"]])
            if (difflib.SequenceMatcher(None, ans, k_ans).ratio() >= ans_thresh
                    and difflib.SequenceMatcher(None, stem, _norm_text(k["stem"])).ratio() >= stem_thresh):
                is_dup = True
                break
        (kept if not is_dup else dropped).append(q)
    return kept, dropped


def generate_angle(angle_key, reference, meta, per_angle):
    angle = ANGLES[angle_key]
    if reference:
        ref_block = (
            "\nREFERENCE MATERIAL (from the doctor's own handbook — treat as the source of truth; "
            "where your knowledge differs, follow it):\n--- BEGIN REFERENCE ---\n"
            + reference
            + "\n--- END REFERENCE ---\n"
        )
    else:
        ref_block = ""
    prompt = (
        MCQ_PROMPT.replace("[N]", str(per_angle))
        .replace("[TOPIC_TITLE]", meta["title"])
        .replace("[SYSTEM]", meta["system"])
        .replace("[ANGLE_LABEL]", angle["label"])
        .replace("[ANGLE_INSTRUCTION]", angle["instruction"])
        .replace("[REFERENCE_BLOCK]", ref_block)
    )
    data, total_tokens, last_err = None, 0, None
    for _ in range(3):  # retry on unparseable / truncated JSON
        resp = call_deepseek(prompt)
        total_tokens += resp.get("usage", {}).get("total_tokens", 0)
        try:
            data = extract_json(resp["choices"][0]["message"]["content"])
            break
        except (json.JSONDecodeError, ValueError) as e:
            last_err = e
    if data is None:
        raise RuntimeError(f"unparseable JSON after retries: {last_err}")

    questions = []
    for q in data.get("questions", []):
        ok, reason = validate_question(q)
        if not ok:
            print(f"  [warn] dropped {angle_key} question: {reason}", file=sys.stderr)
            continue
        # Shuffle options in code so the model's positional bias (it favours A/B) can't leak through.
        options = [str(o).strip() for o in q["options"]]
        correct = options[q["answerIndex"]]
        random.shuffle(options)
        difficulty = str(q.get("difficulty", "medium")).strip().lower()
        if difficulty not in VALID_DIFFICULTY:
            difficulty = "medium"
        questions.append({
            "id": uuid.uuid4().hex[:12],
            "topic": meta["title"],
            "slug": meta["slug"],
            "system": meta["system"],
            "subSystem": meta.get("subSystem"),
            "acuity": meta.get("acuity"),
            "angle": angle_key,
            "stem": q["stem"].strip(),
            "options": options,
            "answerIndex": options.index(correct),
            "explanation": q["explanation"].strip(),
            "difficulty": difficulty,
        })
    return angle_key, questions, total_tokens


def digest(questions):
    letters = "ABCDE"
    by_angle = {}
    for q in questions:
        by_angle.setdefault(q["angle"], []).append(q)
    for angle_key in ANGLES:
        qs = by_angle.get(angle_key, [])
        print(f"\n{'='*70}\n{ANGLES[angle_key]['label'].upper()}  ({len(qs)} questions)\n{'='*70}")
        for i, q in enumerate(qs, 1):
            print(f"\n[{i}] ({q['difficulty']}) {q['stem']}")
            for j, opt in enumerate(q["options"]):
                mark = " <-- correct" if j == q["answerIndex"] else ""
                print(f"    {letters[j]}. {opt}{mark}")
            print(f"    Explanation: {q['explanation']}")


def load_manifest():
    p = PROJECT_ROOT / "public" / "data" / "manifest.json"
    if not p.exists():
        print(f"ERROR: manifest not found at {p}", file=sys.stderr)
        sys.exit(1)
    return json.loads(p.read_text(encoding="utf-8"))


def generate_topic(meta, reference, per_angle, out_dir):
    """Generate every angle for one topic, dedupe, and save <slug>.json.

    Returns {n, tokens, failures, questions}. Angle failures are tolerated so one
    bad angle does not lose the whole topic.
    """
    all_questions = []
    total_tokens = 0
    failures = []
    with ThreadPoolExecutor(max_workers=len(ANGLES)) as pool:
        futures = {pool.submit(generate_angle, key, reference, meta, per_angle): key for key in ANGLES}
        for f in as_completed(futures):
            key = futures[f]
            try:
                _angle, questions, tokens = f.result()
                total_tokens += tokens
                all_questions.extend(questions)
            except Exception:  # noqa: BLE001
                failures.append(key)

    order = {k: i for i, k in enumerate(ANGLES)}
    all_questions.sort(key=lambda q: order[q["angle"]])
    all_questions, _dropped = dedupe(all_questions)

    (out_dir / f"{meta['slug']}.json").write_text(
        json.dumps({
            "topic": meta["title"],
            "slug": meta["slug"],
            "system": meta["system"],
            "subSystem": meta.get("subSystem"),
            "acuity": meta.get("acuity"),
            "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "model": MODEL,
            "grounded": bool(reference),
            "count": len(all_questions),
            "questions": all_questions,
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return {"n": len(all_questions), "tokens": total_tokens, "failures": failures, "questions": all_questions}


def main():
    parser = argparse.ArgumentParser(description="Generate pattern-recognition MCQs for a topic or a whole system.")
    parser.add_argument("--slug", help="Single topic slug, e.g. ulcerative-colitis")
    parser.add_argument("--system", help="Every topic in this system (from the manifest), e.g. Gastroenterology")
    parser.add_argument("--all", action="store_true", help="Every topic across all systems (minus exclusions below)")
    parser.add_argument("--exclude-system", help="Comma-separated system names to skip entirely (only with --all)")
    parser.add_argument("--exclude-slug-file", help="Path to a JSON array of topic slugs to skip")
    parser.add_argument("--per-angle", type=int, default=5, help="Questions per angle (default 5)")
    parser.add_argument("--ground", action="store_true", help="Feed the handbook entry as grounding (default: off)")
    parser.add_argument("--workers", type=int, default=6, help="Topics generated in parallel in batch mode (default 6)")
    parser.add_argument("--no-skip", action="store_true", help="Regenerate even if a question file already exists")
    args = parser.parse_args()

    if not args.slug and not args.system and not args.all:
        parser.error("provide --slug, --system, or --all")

    out_dir = PROJECT_ROOT / "data" / "questions"
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---- Single topic (meta from the entry; keeps the readable digest) ----
    if args.slug:
        study = load_entry(args.slug, "study")
        ward = load_entry(args.slug, "ward")
        if not study and not ward:
            print(f"ERROR: no entry JSON found for slug '{args.slug}'", file=sys.stderr)
            sys.exit(1)
        base = study or ward
        meta = {
            "title": base["title"], "slug": args.slug, "system": base["system"],
            "subSystem": base.get("subSystem"), "acuity": base.get("acuity"),
        }
        reference = build_reference(study, ward) if args.ground else None
        print(f"Topic: {meta['title']} ({meta['system']}) — {'grounded' if reference else 'ungrounded'}\n")
        start = time.time()
        result = generate_topic(meta, reference, args.per_angle, out_dir)
        print(f"\nGenerated {result['n']} questions in {time.time()-start:.1f}s ({result['tokens']:,} tokens).")
        digest(result["questions"])
        return

    # ---- Batch mode: --system or --all (meta from the manifest, so slugs match what the app fetches) ----
    manifest = load_manifest()

    exclude_systems = {s.strip() for s in (args.exclude_system or "").split(",") if s.strip()}
    exclude_slugs: set = set()
    if args.exclude_slug_file:
        exclude_slugs = set(json.loads(Path(args.exclude_slug_file).read_text(encoding="utf-8")))

    if args.all:
        topics = [t for t in manifest if t.get("system") not in exclude_systems]
        label = "ALL systems"
    else:
        if args.system in exclude_systems:
            print(f"ERROR: --system '{args.system}' is also in --exclude-system", file=sys.stderr)
            sys.exit(1)
        topics = [t for t in manifest if t.get("system") == args.system]
        label = args.system
    topics = [t for t in topics if t["slug"] not in exclude_slugs]

    if not topics:
        systems = sorted({t.get("system", "") for t in manifest})
        print(f"ERROR: no topics selected for '{label}'.\nAvailable systems:\n  " + "\n  ".join(systems), file=sys.stderr)
        sys.exit(1)

    jobs, skipped = [], 0
    for t in topics:
        if not args.no_skip and (out_dir / f"{t['slug']}.json").exists():
            skipped += 1
            continue
        jobs.append({
            "title": t["title"], "slug": t["slug"], "system": t["system"],
            "subSystem": t.get("subSystem"), "acuity": t.get("acuity"),
        })

    excl_note = f", {len(exclude_slugs)} slug(s) + {len(exclude_systems)} system(s) excluded" if (exclude_slugs or exclude_systems) else ""
    print(f"Scope: {label} — {len(topics)} topics selected ({skipped} already done, {len(jobs)} to generate{excl_note})")
    print(f"Mode: {'grounded' if args.ground else 'ungrounded'} | {args.per_angle}/angle | up to {args.workers} topics in parallel\n")
    if not jobs:
        print("Nothing to generate.")
        return

    def run(meta):
        reference = None
        if args.ground:
            reference = build_reference(load_entry(meta["slug"], "study"), load_entry(meta["slug"], "ward"))
        return meta, generate_topic(meta, reference, args.per_angle, out_dir)

    start = time.time()
    total_q = total_tok = done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(run, m): m for m in jobs}
        for f in as_completed(futs):
            m = futs[f]
            done += 1
            try:
                meta, result = f.result()
                total_q += result["n"]
                total_tok += result["tokens"]
                warn = f"  [!] failed angles: {result['failures']}" if result["failures"] else ""
                print(f"[{done}/{len(jobs)}] {meta['title'][:42]:<42} -> {result['n']:>2} Q ({result['tokens']:>6,} tok){warn}")
            except Exception as e:  # noqa: BLE001
                print(f"[{done}/{len(jobs)}] {m['title'][:42]:<42} -> FAILED: {e}", file=sys.stderr)

    print(f"\nDONE. {total_q} questions across {len(jobs)} topics in {time.time()-start:.1f}s ({total_tok:,} tokens).")
    print(f"Saved -> {out_dir}")


if __name__ == "__main__":
    main()
