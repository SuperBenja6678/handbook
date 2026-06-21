"""
Generate pericarditis STUDY-MODE entry via DeepSeek v4-flash.
Attempts to replicate the depth/structure of the DeepSeek-pro multi-turn chat
output (which used the original exam-tutor prompt) but in a single API call.
"""

import json
import re
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

DEEPSEEK_API_KEY = "sk-07e1ff9fcdde4d72a4bcec8c6919f9d9"
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-v4-flash"

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

TOPIC = "Pericarditis"


def call_deepseek(prompt: str, max_retries: int = 3) -> dict:
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a senior clinical tutor. Follow the structure exactly. Use markdown."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.4,
        "stream": False,
        "max_tokens": 6000,
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


def parse_markdown_to_structured(md: str, title: str) -> dict:
    """Parse markdown into sections keyed by their ### heading."""
    sections = {}
    current_section = None
    current_buf = []

    for line in md.splitlines():
        h3 = re.match(r"^###\s+(.+?)\s*$", line)
        if h3:
            if current_section:
                sections[current_section] = "\n".join(current_buf).strip()
            current_section = h3.group(1).strip()
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
        "system": "Cardiovascular",
        "subSystem": "Pericardial disease",
        "acuity": "URGENT",
        "oneLiner": one_liner,
        "sections": sections,
        "rawMarkdown": md,
    }


def main():
    print(f"Generating STUDY-MODE entry for: {TOPIC}")
    prompt = STUDY_PROMPT.replace("[TOPIC]", TOPIC)
    try:
        response = call_deepseek(prompt)
    except Exception as e:
        print(f"FATAL: {e}", file=sys.stderr)
        sys.exit(1)

    if "choices" not in response or not response["choices"]:
        print(f"ERROR: unexpected response: {json.dumps(response)[:500]}", file=sys.stderr)
        sys.exit(1)

    content = response["choices"][0]["message"]["content"]
    usage = response.get("usage", {})

    print(f"\n  tokens used: prompt={usage.get('prompt_tokens')}, "
          f"completion={usage.get('completion_tokens')}, "
          f"total={usage.get('total_tokens')}")
    print(f"  response length: {len(content)} chars")
    print(f"  word count (approx): {len(content.split())}")

    structured = parse_markdown_to_structured(content, TOPIC)
    structured["metadata"] = {
        "model": MODEL,
        "mode": "STUDY",
        "tokensUsed": usage,
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    out_dir = Path("/home/z/my-project/data")
    out_dir.mkdir(parents=True, exist_ok=True)

    md_path = out_dir / "pericarditis_study.md"
    md_path.write_text(content, encoding="utf-8")
    print(f"  saved markdown -> {md_path}")

    json_path = out_dir / "pericarditis_study.json"
    json_path.write_text(json.dumps(structured, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  saved json     -> {json_path}")

    print(f"\nSections parsed ({len(structured['sections'])}):")
    for name in structured['sections']:
        print(f"  - {name}")

    print("DONE.")


if __name__ == "__main__":
    main()
