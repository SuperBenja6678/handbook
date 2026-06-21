"""
Re-parse existing entry JSON files that have section-count issues.
Re-extracts sections from rawMarkdown using the updated parser (which handles
both ## and ### headings).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generate_entry import parse_markdown_to_structured


def main():
    entries_dir = Path(__file__).parent.parent.resolve() / "data" / "entries"
    fixed = 0
    skipped = 0
    issues = []

    for f in sorted(entries_dir.glob("*.json")):
        if f.name.startswith("_"):
            continue

        data = json.loads(f.read_text(encoding="utf-8"))
        n_sections = len(data.get("sections", {}))
        md = data.get("rawMarkdown", "")

        # Determine if it's a ward or study file
        is_study = ".study." in f.name
        expected_min = 10 if is_study else 9

        if n_sections >= expected_min:
            skipped += 1
            continue

        # Re-parse using the updated parser
        title = data["title"]
        system = data["system"]
        sub_system = data.get("subSystem", "")
        acuity = data["acuity"]
        mode = data.get("metadata", {}).get("mode", "STUDY" if is_study else "WARD")

        new_struct = parse_markdown_to_structured(md, title, system, sub_system, acuity, mode)
        new_n = len(new_struct["sections"])

        if new_n > n_sections:
            # Preserve original metadata (tokens, timestamps)
            new_struct["metadata"] = data["metadata"]
            f.write_text(json.dumps(new_struct, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"FIXED {f.name}: {n_sections} -> {new_n} sections")
            fixed += 1
        else:
            issues.append((f.name, n_sections, new_n))
            print(f"STILL BAD {f.name}: {n_sections} -> {new_n} sections")

    print()
    print(f"Total: {fixed} fixed, {skipped} already OK, {len(issues)} still problematic")
    if issues:
        print("\nStill problematic:")
        for name, old, new in issues:
            print(f"  {name}: {old} -> {new}")


if __name__ == "__main__":
    main()
