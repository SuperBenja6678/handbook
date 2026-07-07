"""
Sync newly-generated topic entries into the runtime data folder the app serves.

Background: the app fetches its data at runtime from `public/data/`:
  - public/data/manifest.json         (the topic index / sidebar list)
  - public/data/entries/<slug>.ward.json + <slug>.study.json  (content)

The generation pipeline (batch_generate.py) writes new topics to the top-level
`data/entries/` folder instead, so freshly generated topics never reach the app
until they are copied into `public/data/entries/` AND added to the manifest.

This script performs an ADD-ONLY sync:
  * It scans `data/entries/` for paired <slug>.ward.json + <slug>.study.json files.
  * A topic is "new" if its title is NOT already present in the live manifest.
  * New topics are copied into `public/data/entries/` and appended to manifest.json.
  * Existing (already-live) topics and their content are left completely untouched.

The slug used everywhere is the FILE NAME (what the app fetches), guaranteeing the
manifest slug always matches a real file on disk.

Usage:
  python scripts/sync_new_topics.py            # dry run (prints what it would do)
  python scripts/sync_new_topics.py --apply    # actually copy files + write manifest
"""

import argparse
import json
import shutil
import sys
import unicodedata
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SRC_ENTRIES = PROJECT_ROOT / "data" / "entries"
PUB_DATA = PROJECT_ROOT / "public" / "data"
PUB_ENTRIES = PUB_DATA / "entries"
MANIFEST = PUB_DATA / "manifest.json"


def norm_title(s: str) -> str:
    """Normalise a title for duplicate detection: NFC, lowercase, collapse whitespace."""
    s = unicodedata.normalize("NFC", s)
    return " ".join(s.strip().lower().split())


def main() -> int:
    ap = argparse.ArgumentParser(description="Add newly-generated topics to public/data.")
    ap.add_argument("--apply", action="store_true", help="Write changes (default is dry run).")
    args = ap.parse_args()

    if not SRC_ENTRIES.exists():
        print(f"ERROR: source entries dir not found: {SRC_ENTRIES}")
        return 1
    if not MANIFEST.exists():
        print(f"ERROR: live manifest not found: {MANIFEST}")
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    live_titles = {norm_title(m["title"]) for m in manifest}
    live_slugs = {m["slug"] for m in manifest}
    print(f"Live manifest: {len(manifest)} topics")

    # Find paired ward+study files in the source folder.
    ward = {f.name[: -len(".ward.json")] for f in SRC_ENTRIES.glob("*.ward.json")}
    study = {f.name[: -len(".study.json")] for f in SRC_ENTRIES.glob("*.study.json")}
    paired = sorted(ward & study)
    print(f"Source data/entries: {len(paired)} paired topics")

    to_add = []          # list of (slug, meta-dict)
    skipped_live = 0     # title already live
    seen_new = set()     # dedupe within the new set by normalised title
    problems = []        # metadata / read issues

    for slug in paired:
        ward_path = SRC_ENTRIES / f"{slug}.ward.json"
        try:
            data = json.loads(ward_path.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            problems.append(f"{slug}: cannot read ward.json ({e})")
            continue

        title = data.get("title")
        if not title:
            problems.append(f"{slug}: ward.json missing 'title'")
            continue

        nt = norm_title(title)
        if nt in live_titles or slug in live_slugs:
            skipped_live += 1
            continue
        if nt in seen_new:
            # Two source files map to the same title (e.g. em-dash vs stripped
            # regeneration of a topic that isn't live). Keep the first, skip the rest.
            continue
        seen_new.add(nt)

        acuity = data.get("acuity", "")
        meta = {
            "slug": slug,  # filename slug == what the app fetches
            "title": title,
            "system": data.get("system", "Uncategorised"),
            "subSystem": data.get("subSystem", ""),
            "acuity": acuity,
            "highYield": acuity in ("EMERGENCY", "URGENT"),
        }
        to_add.append((slug, meta))

    print(f"\nAlready live (skipped): {skipped_live}")
    print(f"New topics to add:      {len(to_add)}")
    if problems:
        print(f"\n!! {len(problems)} problem file(s):")
        for p in problems[:30]:
            print(f"   - {p}")

    # Show a sample of what will be added, grouped by system.
    by_system: dict[str, int] = {}
    for _slug, meta in to_add:
        by_system[meta["system"]] = by_system.get(meta["system"], 0) + 1
    print("\nNew topics by system:")
    for sys_name in sorted(by_system):
        print(f"   {by_system[sys_name]:>3}  {sys_name}")

    print("\nSample (first 15):")
    for slug, meta in to_add[:15]:
        print(f"   [{meta['acuity']:<9}] {meta['title']}  ->  {slug}")

    if not args.apply:
        print("\n(dry run — no files written. Re-run with --apply to make changes.)")
        return 0

    # --- Apply ---
    PUB_ENTRIES.mkdir(parents=True, exist_ok=True)
    copied = 0
    for slug, _meta in to_add:
        for ext in ("ward", "study"):
            src = SRC_ENTRIES / f"{slug}.{ext}.json"
            dst = PUB_ENTRIES / f"{slug}.{ext}.json"
            shutil.copy2(src, dst)
            copied += 1

    manifest.extend(meta for _slug, meta in to_add)
    MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"\nAPPLIED: copied {copied} files into {PUB_ENTRIES}")
    print(f"         manifest now lists {len(manifest)} topics -> {MANIFEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
