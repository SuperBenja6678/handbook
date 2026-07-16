"""
Sync generated question sets into the runtime data folder the app serves.

Background: the app fetches its data at runtime from `public/data/` (see
sync_new_topics.py for the same pattern used for topic entries). The question
generator (generate_questions.py) writes to the top-level `data/questions/`
folder, so freshly generated quizzes never reach the app until copied into
`public/data/questions/` AND indexed in a manifest the app can check.

This script:
  * Copies every data/questions/<slug>.json into public/data/questions/<slug>.json.
  * Writes public/data/questions-manifest.json: a list of {slug, topic, system,
    subSystem, acuity, count} for every topic that HAS a question set — the
    main app uses this to decide whether to show the Quiz mode for a topic,
    without fetching every question file up front.

Always a full mirror (not add-only): question files are fully regenerated
artifacts, not hand-edited, so there's nothing to preserve by diffing.

Usage:
  python scripts/sync_questions.py
"""

import json
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SRC_QUESTIONS = PROJECT_ROOT / "data" / "questions"
PUB_QUESTIONS = PROJECT_ROOT / "public" / "data" / "questions"
PUB_MANIFEST = PROJECT_ROOT / "public" / "data" / "questions-manifest.json"


def main() -> int:
    if not SRC_QUESTIONS.exists():
        print(f"ERROR: source dir not found: {SRC_QUESTIONS}")
        return 1

    files = sorted(SRC_QUESTIONS.glob("*.json"))
    if not files:
        print("No question files found — nothing to sync.")
        return 0

    PUB_QUESTIONS.mkdir(parents=True, exist_ok=True)

    manifest = []
    copied = 0
    problems = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            problems.append(f"{f.name}: cannot read ({e})")
            continue

        shutil.copy2(f, PUB_QUESTIONS / f.name)
        copied += 1
        manifest.append({
            "slug": data["slug"],
            "topic": data["topic"],
            "system": data["system"],
            "subSystem": data.get("subSystem"),
            "acuity": data.get("acuity"),
            "count": data["count"],
        })

    manifest.sort(key=lambda m: (m["system"], m["topic"]))
    PUB_MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Copied {copied} question file(s) -> {PUB_QUESTIONS}")
    print(f"Manifest written ({len(manifest)} topics) -> {PUB_MANIFEST}")
    if problems:
        print(f"\n!! {len(problems)} problem file(s):")
        for p in problems:
            print(f"   - {p}")

    by_system: dict[str, int] = {}
    for m in manifest:
        by_system[m["system"]] = by_system.get(m["system"], 0) + 1
    print("\nQuiz coverage by system:")
    for sys_name in sorted(by_system):
        print(f"   {by_system[sys_name]:>3}  {sys_name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
