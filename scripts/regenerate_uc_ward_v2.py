"""
Regenerate the UC ward-mode entry with the upgraded prompt that incorporates
all 8 DeepSeek-suggested improvements. Save the OLD version under a comparison
folder so we can A/B test.

Saves:
  data/entries/ulcerative-colitis.ward.json  (NEW — overwritten)
  data/compare/ulcerative-colitis.ward.v1.json  (OLD — backed up)
  data/compare/ulcerative-colitis.ward.v2.json  (NEW — copy for diffing)
"""

import json
import re
import shutil
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(Path(__file__).parent))
from generate_entry import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_API_URL,
    MODEL,
    call_deepseek,
    parse_markdown_to_structured,
    attach_tokens,
)

# ---------------------------------------------------------------------------
# Upgraded ward prompt — incorporates 8 DeepSeek-suggested improvements:
#   1. "Killers first" before presentation
#   2. Splitter question in DDx
#   3. "Never miss" test in investigations
#   4. Default orders in management
#   5. Max safe dose + renal + most dangerous dose error in drugs
#   6. Pearls (positive actions) vs Pitfalls (errors to avoid) — split
#   7. Safety-netting for discharge (new section)
#   8. Source hierarchy guidance (NICE/BTS/BNF, mark uncertain doses)
# ---------------------------------------------------------------------------

WARD_PROMPT_V2 = """You are a senior clinical tutor writing a structured reference entry for a junior doctor (FY1/PRHO level) who is actively seeing patients on the ward. They may have knowledge gaps from medical school and need PATTERN RECOGNITION plus ACTIONABLE knowledge — not exam trivia, not exhaustive pathophysiology.

Generate a structured clinical reference entry for: [TOPIC]

Output STRICTLY in this Markdown structure. Use bullets, not prose. Be dense, scannable, and ward-orientated. Aim for 800-1200 words total.

Source guidance: Prefer UK/Irish practice (NICE, BTS, BNF, SIGN, HSE). Use UK/IE drug names, units, and spellings. NEVER invent a drug dose — if you are uncertain about a specific dose or threshold, write "[check local policy]" instead of guessing.

## [Topic Name]
**One-liner:** <=25 words — what it is, who gets it, why it matters.

### Killers First — What Will Kill Them In The First Hour?
- 1-2 immediately life-threatening mimics or complications you MUST rule out before treating the common
- For each: the single finding that says "this is the killer, not the routine case"
- This primes pattern recognition before the calm bullet points begin.

### Presentation
- Cardinal symptoms (the 3-5 things you'll actually see)
- Key exam findings

### Differential Diagnosis
- Most likely -> less likely, with 1-line differentiators
- **Splitter:** one single clinical feature or bedside test that bifurcates the top two differentials (e.g. "no blood + perianal disease -> Crohn's, not UC")

### Investigations
- **Bedside:** what to do in the first hour
- **Bloods:** panels + key markers
- **Imaging:** first-line, second-line
- **Special tests:** if relevant
- Diagnostic criteria / scoring system (name + key thresholds)
- **Never-miss test:** the ONE investigation whose omission is a serious error (e.g. pregnancy test in abdominal pain, stool culture before steroids in colitis, ECG in syncope, lipase in chest pain)

### Management
- **Immediate (first hour / ED):**
- **Ward (first 24-72h):**
- **Long-term / outpatient:**
- **Default Orders (if admitted):** fluids type + rate, VTE prophylaxis, diet/NBM status, observation frequency. (Skip if not relevant for this topic.)

### Drugs & Doses
- First-line agents — name + dose + route + duration
- Common alternatives
- Key contraindications / interactions
- **Renal/hepatic adjustment:** note any dose changes for renal or hepatic impairment
- **Most dangerous dose error:** the single most common or harmful prescribing mistake with this drug class (e.g. "gentamicin — check levels before second dose", "insulin — never give IV bolus in DKA without K+ check")

### Complications
- **Acute:**
- **Chronic:**

### Prognosis
- 1-2 lines on mortality / recovery / chronicity

### Pearls (positive actions)
- 2-3 specific things you should DO (e.g. "Always check AXR before calling reg in severe UC")

### Pitfalls (Errors To Avoid)
- 2-3 specific things you should NOT do (e.g. "Giving steroids before stool cultures", "Using loperamide in active colitis")

### Safety Netting (If Patient Goes Home)
- **Return if:** 2-3 concrete triggers that mean the patient must come back
- **Follow-up:** who and when

### Escalation Criteria
- When to call senior / ICU / crash team
- Specific thresholds (NEWS2, lactate, GCS, etc.)
"""

TOPIC = "Ulcerative Colitis"
SYSTEM = "Gastroenterology"
SUB_SYSTEM = "IBD"
ACUITY = "CHRONIC"


def main():
    # Back up old version
    old_path = Path("/home/z/my-project/data/entries/ulcerative-colitis.ward.json")
    compare_dir = Path("/home/z/my-project/data/compare")
    compare_dir.mkdir(parents=True, exist_ok=True)

    if old_path.exists():
        shutil.copy(old_path, compare_dir / "ulcerative-colitis.ward.v1.json")
        print(f"Backed up old version -> {compare_dir / 'ulcerative-colitis.ward.v1.json'}")

    print(f"\n=== WARD MODE v2 (upgraded prompt): {TOPIC} ===")
    prompt = WARD_PROMPT_V2.replace("[TOPIC]", TOPIC)
    resp = call_deepseek(prompt, max_tokens=4500)
    content = resp["choices"][0]["message"]["content"]
    usage = resp.get("usage", {})
    print(f"  tokens: {usage.get('total_tokens')}, words: ~{len(content.split())}")

    structured = parse_markdown_to_structured(content, TOPIC, SYSTEM, SUB_SYSTEM, ACUITY, "WARD")
    attach_tokens(structured, resp)

    # Save new version
    old_path.write_text(json.dumps(structured, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  saved -> {old_path}")

    # Also save to compare dir for A/B
    (compare_dir / "ulcerative-colitis.ward.v2.json").write_text(
        json.dumps(structured, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"\nSections ({len(structured['sections'])}):")
    for k in structured['sections']:
        print(f"  - {k}")

    print("\nDONE.")


if __name__ == "__main__":
    main()
