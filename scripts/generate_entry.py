"""
Batch-generate ward + study entries for a single topic via DeepSeek v4-flash.
Saves both modes to /home/z/my-project/data/entries/<slug>.{ward,study}.json

Usage: python3 generate_entry.py "Topic Name" "System" "SubSystem" "ACUITY"
Example: python3 generate_entry.py "Ulcerative Colitis" "Gastroenterology" "IBD" "CHRONIC"
"""

import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
if not DEEPSEEK_API_KEY:
    print("ERROR: Set DEEPSEEK_API_KEY environment variable.", file=sys.stderr)
    sys.exit(1)
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-v4-flash"

WARD_PROMPT = """You are a senior clinical tutor writing a structured reference entry for a junior doctor (FY1/PRHO level) who is actively seeing patients on the ward. They may have knowledge gaps from medical school and need PATTERN RECOGNITION plus ACTIONABLE knowledge — not exam trivia, not exhaustive pathophysiology.

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

STUDY_PROMPT = """You are a senior clinical tutor running a one-shot deep-teaching session for a junior doctor (FY1/PRHO level) who is building a personal knowledge bank. They may have knowledge gaps from medical school. They want CONCEPTUAL UNDERSTANDING plus PATTERN RECOGNITION — not exam trivia, not just bullet-point dosing.

Generate a structured STUDY-MODE entry for: [TOPIC]

Output STRICTLY in this Markdown structure. Mix prose with bullets where each works best. Be engaging but dense. Aim for 1800-2500 words total. Use tables where they aid comparison. Use mnemonics where useful.

## [Topic Name]
**One-liner:** <=25 words — what it is, who gets it, why it matters.

### 1. Pattern Recognition — The Patient You'll See
- Describe a classic vignette (3-5 sentences) showing how this presents on the ward / in a stem
- Dissect the vignette: bullet-list each pattern clue and what it tells you
- Atypical presentations: 2-3 brief variants that may trick you

### 2. What Is This? (Definition & Why It Matters)
- Plain-language definition (2-3 sentences)
- Why this topic matters clinically — frequency, stakes, common pitfalls

### 3. Pathophysiology — The "Why" Behind The Findings
- Tell the story of how the disease develops
- Explain WHY each key clinical sign happens (mechanism -> sign)
- Connect pathophys to the pattern recognition cues above

### 4. Causes / Triggers (organised in bins)
- Group causes by category (idiopathic, infectious, autoimmune, etc.)
- For each cause: 1-line "stem clue" that points to it
- Highlight the most common cause

### 5. Investigations — What, Why, What It Means
- Diagnostic criteria / scoring system (name + key thresholds)
- For each test: WHAT it shows, WHY you order it, HOW to interpret
- Pattern-recognition: what single finding confirms / rules out

### 6. Management — Approach & Reasoning
- Immediate (first hour): what + why
- Ward (24-72h): what + why
- Long-term: what + why
- Include drug doses inline (name + dose + route + duration)
- Highlight what NOT to do (common pitfalls)

### 7. Differential Diagnosis — Comparison Table
Build a markdown table comparing the topic to its top 3-4 mimics:

| Feature | [Topic] | [Mimic 1] | [Mimic 2] | [Mimic 3] |
|---------|---------|-----------|-----------|-----------|
| Pain    | ...     | ...       | ...       | ...       |
| Exam    | ...     | ...       | ...       | ...       |
| ECG     | ...     | ...       | ...       | ...       |
| Labs    | ...     | ...       | ...       | ...       |
| Key diff| ...     | ...       | ...       | ...       |

### 8. Complications — What If You Miss It?
- For each major complication: how it presents, key signs, what to do
- Include late-presentation patterns (the stems that test "what happens if untreated")

### 9. High-Yield Mnemonics & Pearls
- 2-3 mnemonics if applicable (with what each letter means)
- 5-7 high-yield clinical pearls (pattern-recognition cues)
- Common exam / ward mistakes to avoid

### 10. Escalation Criteria
- When to call senior / ICU / crash team
- Specific thresholds (NEWS2, lactate, GCS, etc.)

Keep it clinically accurate. Avoid padding. Every sentence should teach something.
"""


def call_deepseek(prompt: str, max_tokens: int = 6000, max_retries: int = 3) -> dict:
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a senior clinical tutor. Follow the structure exactly. Use markdown."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.35,
        "stream": False,
        "max_tokens": max_tokens,
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
            print(f"  [attempt {attempt}/{max_retries}] calling DeepSeek {MODEL}...")
            with urlopen(req, timeout=180) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        except HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            print(f"  HTTP {e.code}: {body[:300]}")
            last_error = f"HTTP {e.code}: {body[:200]}"
        except URLError as e:
            print(f"  URL error: {e}")
            last_error = str(e)
        except Exception as e:
            print(f"  Error: {e}")
            last_error = str(e)
        if attempt < max_retries:
            wait = 2 ** attempt
            print(f"  retrying in {wait}s...")
            time.sleep(wait)
    raise RuntimeError(f"DeepSeek call failed after {max_retries} attempts: {last_error}")


def parse_markdown_to_structured(md: str, title: str, system: str, sub_system: str, acuity: str, mode: str) -> dict:
    """Parse markdown into sections keyed by heading.

    Accepts both ### (preferred) and ## (fallback) headings for section names.
    DeepSeek occasionally uses ## instead of ### — we handle both gracefully.
    Skips the very first ## title heading (which is the topic name, not a section).
    """
    sections = {}
    current_section = None
    current_buf = []
    first_h2_seen = False

    for line in md.splitlines():
        # Try ### first (preferred)
        h3 = re.match(r"^###\s+(.+?)\s*$", line)
        h2 = re.match(r"^##\s+(.+?)\s*$", line)

        if h3:
            if current_section:
                sections[current_section] = "\n".join(current_buf).strip()
            current_section = h3.group(1).strip()
            current_buf = []
        elif h2:
            # Skip the first ## (it's the topic title)
            if not first_h2_seen:
                first_h2_seen = True
                # If this h2 looks like the title, skip it
                if h2.group(1).strip().lower() == title.lower():
                    continue
                # Otherwise treat as a section
                if current_section:
                    sections[current_section] = "\n".join(current_buf).strip()
                current_section = h2.group(1).strip()
                current_buf = []
            else:
                if current_section:
                    sections[current_section] = "\n".join(current_buf).strip()
                current_section = h2.group(1).strip()
                current_buf = []
        else:
            if current_section is None:
                continue
            current_buf.append(line)

    if current_section:
        sections[current_section] = "\n".join(current_buf).strip()

    one_liner = ""
    m = re.search(r"\*\*One-liner:\*\*\s*(.+)", md)
    if m:
        one_liner = m.group(1).strip()

    return {
        "title": title,
        "slug": title.lower().replace(" ", "-"),
        "system": system,
        "subSystem": sub_system,
        "acuity": acuity,
        "oneLiner": one_liner,
        "sections": sections,
        "rawMarkdown": md,
        "metadata": {
            "model": MODEL,
            "mode": mode,
            "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
    }


def attach_tokens(structured: dict, response: dict) -> None:
    usage = response.get("usage", {})
    structured["metadata"]["tokensUsed"] = usage


def main():
    if len(sys.argv) < 5:
        print("Usage: python3 generate_entry.py \"Topic Name\" \"System\" \"SubSystem\" \"ACUITY\"")
        print("ACUITY must be one of: EMERGENCY, URGENT, ROUTINE, CHRONIC")
        sys.exit(1)
    title = sys.argv[1]
    system = sys.argv[2]
    sub_system = sys.argv[3]
    acuity = sys.argv[4].upper()
    if acuity not in ("EMERGENCY", "URGENT", "ROUTINE", "CHRONIC"):
        print(f"ERROR: invalid acuity '{acuity}'", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(__file__).parent.parent.resolve() / "data" / "entries"
    out_dir.mkdir(parents=True, exist_ok=True)

    slug = title.lower().replace(" ", "-")

    # Ward mode
    print(f"\n=== WARD MODE: {title} ===")
    prompt = WARD_PROMPT.replace("[TOPIC]", title)
    resp = call_deepseek(prompt, max_tokens=4500)
    content = resp["choices"][0]["message"]["content"]
    usage = resp.get("usage", {})
    print(f"  tokens: {usage.get('total_tokens')}, words: ~{len(content.split())}")
    structured = parse_markdown_to_structured(content, title, system, sub_system, acuity, "WARD")
    attach_tokens(structured, resp)
    ward_path = out_dir / f"{slug}.ward.json"
    ward_path.write_text(json.dumps(structured, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  saved -> {ward_path}")
    print(f"  sections ({len(structured['sections'])}): {list(structured['sections'].keys())}")

    # Brief pause between calls
    time.sleep(1)

    # Study mode
    print(f"\n=== STUDY MODE: {title} ===")
    prompt = STUDY_PROMPT.replace("[TOPIC]", title)
    resp = call_deepseek(prompt, max_tokens=6000)
    content = resp["choices"][0]["message"]["content"]
    usage = resp.get("usage", {})
    print(f"  tokens: {usage.get('total_tokens')}, words: ~{len(content.split())}")
    structured = parse_markdown_to_structured(content, title, system, sub_system, acuity, "STUDY")
    attach_tokens(structured, resp)
    study_path = out_dir / f"{slug}.study.json"
    study_path.write_text(json.dumps(structured, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  saved -> {study_path}")
    print(f"  sections ({len(structured['sections'])}): {list(structured['sections'].keys())}")

    print("\nDONE.")


if __name__ == "__main__":
    main()
