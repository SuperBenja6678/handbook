"""
Batch-generate ward + study entries for a set of topics from the master list.

Usage:
  python scripts/batch_generate.py --priority WEEK_1
  python scripts/batch_generate.py --priority WEEK_1 --limit 10
  python scripts/batch_generate.py --system Cardiovascular
  python scripts/batch_generate.py --slug acute-pancreatitis
  python scripts/batch_generate.py --all  # generate ALL remaining topics across all priorities

Parallel by default (--parallel 20). DeepSeek v4-flash concurrency limit is 2500,
so we can push this much higher if needed. Ward + study calls for the same topic
also run in parallel.

Estimated time with --parallel 20: ~2-3 minutes per 20 topics.
"""

import argparse
import json
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generate_entry import (
    call_deepseek,
    parse_markdown_to_structured,
    attach_tokens,
    WARD_PROMPT,
    STUDY_PROMPT,
)


PROJECT_ROOT = Path(__file__).parent.parent.resolve()
_print_lock = threading.Lock()

def sanitize_slug(title):
    """Convert a title to a safe filename slug. Handles Windows-illegal characters."""
    import re
    slug = title.lower()
    # Replace anything that's not alphanumeric, space, or hyphen with a hyphen
    # This handles Windows-illegal chars, Unicode dashes, parens, slashes, etc.
    slug = re.sub(r'[^a-z0-9\s-]', '-', slug)
    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)
    # Collapse multiple hyphens
    slug = re.sub(r'-+', '-', slug)
    # Strip leading/trailing hyphens
    slug = slug.strip('-')
    return slug

def safe_print(*args, **kwargs):
    with _print_lock:
        print(*args, **kwargs)


def load_master_topics():
    p = PROJECT_ROOT / "data" / "master-topics.json"
    if not p.exists():
        print(f"ERROR: master-topics.json not found at {p}", file=sys.stderr)
        sys.exit(1)
    return json.loads(p.read_text(encoding="utf-8"))["topics"]


def select_topics(topics, *, priority=None, system=None, slug=None, limit=None):
    selected = topics
    if priority:
        selected = [t for t in selected if t["priority"] == priority]
    if system:
        selected = [t for t in selected if t["system"] == system]
    if slug:
        selected = [t for t in selected if sanitize_slug(t["title"]) == slug]
    if limit:
        selected = selected[:limit]
    return selected


def already_generated(slug, out_dir):
    """Skip topics where both ward and study JSON already exist."""
    ward = out_dir / f"{slug}.ward.json"
    study = out_dir / f"{slug}.study.json"
    return ward.exists() and study.exists()


def generate_one(topic, out_dir, *, skip_existing=True, max_retries=2, parallel_mode=True):
    """Generate ward + study for one topic. Returns a summary dict.

    When parallel_mode=True, ward and study API calls run concurrently.
    """
    title = topic["title"]
    slug = sanitize_slug(title)
    summary = {
        "title": title,
        "slug": slug,
        "system": topic["system"],
        "acuity": topic["acuity"],
        "priority": topic["priority"],
        "wardTokens": None,
        "studyTokens": None,
        "wardSections": None,
        "studySections": None,
        "status": "pending",
        "error": None,
        "skipped": False,
    }

    if skip_existing and already_generated(slug, out_dir):
        summary["status"] = "skipped"
        summary["skipped"] = True
        return summary

    if parallel_mode:
        # Run ward and study API calls in parallel
        ward_resp = None
        study_resp = None
        ward_err = None
        study_err = None

        def do_ward():
            nonlocal ward_resp, ward_err
            try:
                prompt = WARD_PROMPT.replace("[TOPIC]", title)
                ward_resp = call_deepseek(prompt, max_tokens=4500, max_retries=max_retries)
            except Exception as e:
                ward_err = e

        def do_study():
            nonlocal study_resp, study_err
            try:
                prompt = STUDY_PROMPT.replace("[TOPIC]", title)
                study_resp = call_deepseek(prompt, max_tokens=6000, max_retries=max_retries)
            except Exception as e:
                study_err = e

        with ThreadPoolExecutor(max_workers=2) as pool:
            f_ward = pool.submit(do_ward)
            f_study = pool.submit(do_study)
            f_ward.result()
            f_study.result()

        # Process ward result
        if ward_err:
            summary["status"] = "ward_failed"
            summary["error"] = f"ward: {ward_err}"
            return summary

        try:
            content = ward_resp["choices"][0]["message"]["content"]
            usage = ward_resp.get("usage", {})
            summary["wardTokens"] = usage.get("total_tokens")
            structured = parse_markdown_to_structured(
                content, title, topic["system"], topic["subSystem"], topic["acuity"], "WARD"
            )
            attach_tokens(structured, ward_resp)
            summary["wardSections"] = len(structured["sections"])
            (out_dir / f"{slug}.ward.json").write_text(
                json.dumps(structured, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except Exception as e:
            summary["status"] = "ward_failed"
            summary["error"] = f"ward parse: {e}"
            return summary

        # Process study result
        if study_err:
            summary["status"] = "study_failed"
            summary["error"] = f"study: {study_err}"
            return summary

        try:
            content = study_resp["choices"][0]["message"]["content"]
            usage = study_resp.get("usage", {})
            summary["studyTokens"] = usage.get("total_tokens")
            structured = parse_markdown_to_structured(
                content, title, topic["system"], topic["subSystem"], topic["acuity"], "STUDY"
            )
            attach_tokens(structured, study_resp)
            summary["studySections"] = len(structured["sections"])
            (out_dir / f"{slug}.study.json").write_text(
                json.dumps(structured, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except Exception as e:
            summary["status"] = "study_failed"
            summary["error"] = f"study parse: {e}"
            return summary

        summary["status"] = "ok"
        return summary

    else:
        # Sequential mode (original behaviour)
        # Ward mode
        try:
            prompt = WARD_PROMPT.replace("[TOPIC]", title)
            resp = call_deepseek(prompt, max_tokens=4500, max_retries=max_retries)
            content = resp["choices"][0]["message"]["content"]
            usage = resp.get("usage", {})
            summary["wardTokens"] = usage.get("total_tokens")

            structured = parse_markdown_to_structured(
                content, title, topic["system"], topic["subSystem"], topic["acuity"], "WARD"
            )
            attach_tokens(structured, resp)
            summary["wardSections"] = len(structured["sections"])
            (out_dir / f"{slug}.ward.json").write_text(
                json.dumps(structured, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except Exception as e:
            summary["status"] = "ward_failed"
            summary["error"] = f"ward: {e}"
            return summary

        time.sleep(0.5)

        # Study mode
        try:
            prompt = STUDY_PROMPT.replace("[TOPIC]", title)
            resp = call_deepseek(prompt, max_tokens=6000, max_retries=max_retries)
            content = resp["choices"][0]["message"]["content"]
            usage = resp.get("usage", {})
            summary["studyTokens"] = usage.get("total_tokens")

            structured = parse_markdown_to_structured(
                content, title, topic["system"], topic["subSystem"], topic["acuity"], "STUDY"
            )
            attach_tokens(structured, resp)
            summary["studySections"] = len(structured["sections"])
            (out_dir / f"{slug}.study.json").write_text(
                json.dumps(structured, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except Exception as e:
            summary["status"] = "study_failed"
            summary["error"] = f"study: {e}"
            return summary

        summary["status"] = "ok"
        return summary


def main():
    parser = argparse.ArgumentParser(description="Batch-generate topic entries.")
    parser.add_argument("--priority", help="Filter by priority (WEEK_1, WEEK_2, ..., ONGOING)")
    parser.add_argument("--system", help="Filter by system")
    parser.add_argument("--slug", help="Generate a single topic by slug")
    parser.add_argument("--limit", type=int, help="Max topics to generate")
    parser.add_argument("--no-skip", action="store_true", help="Regenerate even if files exist")
    parser.add_argument("--dry-run", action="store_true", help="List what would be generated, don't call API")
    parser.add_argument("--parallel", "-j", type=int, default=20, help="Number of topics to generate in parallel (default: 20)")
    parser.add_argument("--sequential", action="store_true", help="Disable parallel mode (original sequential behaviour)")
    parser.add_argument("--all", action="store_true", help="Generate ALL remaining topics across all priorities")
    args = parser.parse_args()

    topics = load_master_topics()

    if args.all:
        # Generate all remaining topics across all priorities
        selected = topics
        filter_label = "ALL priorities"
    elif any([args.priority, args.system, args.slug]):
        selected = select_topics(
            topics,
            priority=args.priority,
            system=args.system,
            slug=args.slug,
            limit=args.limit,
        )
        filter_label = args.priority or args.system or args.slug
    else:
        args.priority = "WEEK_1"
        selected = select_topics(topics, priority="WEEK_1", limit=args.limit)
        filter_label = "WEEK_1"
        print("No filter specified — defaulting to WEEK_1 (acute emergencies).\n")

    if not selected:
        print("No topics match the filter.")
        sys.exit(0)

    out_dir = PROJECT_ROOT / "data" / "entries"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Count how many are already done
    already = sum(1 for t in selected if already_generated(sanitize_slug(t["title"]), out_dir))
    remaining = len(selected) - already

    print(f"Filter: {filter_label}")
    print(f"Total: {len(selected)} topics ({already} already done, {remaining} to generate)")
    print()

    if args.dry_run:
        print("DRY RUN — listing topics:")
        for t in selected:
            slug = sanitize_slug(t["title"])
            status = "DONE" if already_generated(slug, out_dir) else "TODO"
            print(f"  [{status:4s}] {t['title']}")
        return

    if remaining == 0:
        print("All topics already generated. Nothing to do.")
        return

    use_parallel = not args.sequential
    parallel_workers = args.parallel if use_parallel else 1

    print(f"Mode: {'parallel (' + str(parallel_workers) + ' workers)' if use_parallel else 'sequential'}")
    print(f"Generating into: {out_dir}")
    print(f"Skip existing: {not args.no_skip}")
    print()

    start = time.time()
    summaries = []
    failed = []
    completed = 0

    if use_parallel:
        # Parallel mode — submit all topics to thread pool
        with ThreadPoolExecutor(max_workers=parallel_workers) as pool:
            future_map = {}
            for topic in selected:
                slug = sanitize_slug(topic["title"])
                if not args.no_skip and already_generated(slug, out_dir):
                    # Already done — add dummy summary immediately
                    summaries.append({
                        "title": topic["title"],
                        "slug": slug,
                        "system": topic["system"],
                        "acuity": topic["acuity"],
                        "priority": topic["priority"],
                        "wardTokens": None, "studyTokens": None,
                        "wardSections": None, "studySections": None,
                        "status": "skipped", "error": None, "skipped": True,
                    })
                    continue
                f = pool.submit(generate_one, topic, out_dir,
                               skip_existing=not args.no_skip, parallel_mode=True)
                future_map[f] = topic

            for f in as_completed(future_map):
                topic = future_map[f]
                completed += 1
                try:
                    summary = f.result()
                except Exception as e:
                    summary = {
                        "title": topic["title"],
                        "slug": sanitize_slug(topic["title"]),
                        "system": topic["system"],
                        "acuity": topic["acuity"],
                        "priority": topic["priority"],
                        "wardTokens": None, "studyTokens": None,
                        "wardSections": None, "studySections": None,
                        "status": "failed", "error": str(e), "skipped": False,
                    }
                summaries.append(summary)

                if summary["status"] == "skipped":
                    safe_print(f"[{completed}/{remaining}] {summary['title']} -> skipped")
                elif summary["status"] == "ok":
                    safe_print(f"[{completed}/{remaining}] {summary['title']} -> OK "
                              f"({summary['wardTokens']}+{summary['studyTokens']} tokens, "
                              f"{summary['wardSections']}+{summary['studySections']} sections)")
                else:
                    safe_print(f"[{completed}/{remaining}] {summary['title']} -> FAILED "
                              f"({summary['status']}: {summary['error']})")
                    failed.append(summary)
    else:
        # Sequential mode (original behaviour)
        for i, topic in enumerate(selected, 1):
            title = topic["title"]
            print(f"[{i}/{len(selected)}] {title}")
            t0 = time.time()

            summary = generate_one(topic, out_dir, skip_existing=not args.no_skip, parallel_mode=False)
            summaries.append(summary)

            if summary["status"] == "skipped":
                print(f"  -> skipped (already exists)")
            elif summary["status"] == "ok":
                print(f"  -> OK ({summary['wardTokens']}+{summary['studyTokens']} tokens, "
                      f"{summary['wardSections']}+{summary['studySections']} sections, "
                      f"{time.time()-t0:.1f}s)")
            else:
                print(f"  -> FAILED ({summary['status']}: {summary['error']})")
                failed.append(summary)

    elapsed = time.time() - start
    succeeded = sum(1 for s in summaries if s["status"] == "ok")
    skipped = sum(1 for s in summaries if s["status"] == "skipped")
    n_failed = sum(1 for s in summaries if s["status"] not in ("ok", "skipped"))
    total_tokens = sum((s["wardTokens"] or 0) + (s["studyTokens"] or 0) for s in summaries)

    # Write batch summary
    summary_path = out_dir / "_batch-summary.json"
    batch_summary = {
        "runAt": datetime.utcnow().isoformat() + "Z",
        "filter": {
            "priority": args.priority,
            "system": args.system,
            "slug": args.slug,
            "limit": args.limit,
            "all": args.all,
        },
        "parallel": use_parallel,
        "workers": parallel_workers,
        "elapsedSeconds": round(elapsed, 1),
        "total": len(selected),
        "succeeded": succeeded,
        "skipped": skipped,
        "failed": n_failed,
        "totalTokens": total_tokens,
        "topics": summaries,
    }
    summary_path.write_text(json.dumps(batch_summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print()
    print("=" * 60)
    print(f"BATCH COMPLETE — {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"  OK:      {succeeded}")
    print(f"  Skipped: {skipped}")
    print(f"  Failed:  {n_failed}")
    print(f"  Tokens:  {total_tokens:,}")
    print(f"  Summary: {summary_path}")
    if succeeded > 0:
        print(f"  Avg per topic: {elapsed/succeeded:.1f}s")

    if failed:
        print("\nFAILED TOPICS:")
        for s in failed:
            print(f"  - {s['title']}: {s['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
