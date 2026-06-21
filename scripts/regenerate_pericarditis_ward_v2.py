"""
Regenerate the pericarditis ward-mode entry with the upgraded v2 prompt
(same prompt as the UC v2 regeneration). Backs up the old version.
"""

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generate_entry import call_deepseek, parse_markdown_to_structured, attach_tokens
from regenerate_uc_ward_v2 import WARD_PROMPT_V2

TOPIC = "Pericarditis"
SYSTEM = "Cardiovascular"
SUB_SYSTEM = "Pericardial disease"
ACUITY = "URGENT"


def main():
    old_path = Path("/home/z/my-project/data/entries/pericarditis.ward.json")
    compare_dir = Path("/home/z/my-project/data/compare")
    compare_dir.mkdir(parents=True, exist_ok=True)

    if old_path.exists():
        shutil.copy(old_path, compare_dir / "pericarditis.ward.v1.json")
        print(f"Backed up old version -> {compare_dir / 'pericarditis.ward.v1.json'}")

    print(f"\n=== WARD MODE v2 (upgraded prompt): {TOPIC} ===")
    prompt = WARD_PROMPT_V2.replace("[TOPIC]", TOPIC)
    resp = call_deepseek(prompt, max_tokens=4500)
    content = resp["choices"][0]["message"]["content"]
    usage = resp.get("usage", {})
    print(f"  tokens: {usage.get('total_tokens')}, words: ~{len(content.split())}")

    structured = parse_markdown_to_structured(content, TOPIC, SYSTEM, SUB_SYSTEM, ACUITY, "WARD")
    attach_tokens(structured, resp)

    old_path.write_text(json.dumps(structured, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  saved -> {old_path}")

    (compare_dir / "pericarditis.ward.v2.json").write_text(
        json.dumps(structured, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"\nSections ({len(structured['sections'])}):")
    for k in structured['sections']:
        print(f"  - {k}")

    print("\nDONE.")


if __name__ == "__main__":
    main()
