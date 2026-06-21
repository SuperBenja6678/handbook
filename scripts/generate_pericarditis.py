"""
Generate pericarditis clinical reference entry via DeepSeek v4-flash API.
Saves the result as both markdown and structured JSON.
"""

import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

DEEPSEEK_API_KEY = "sk-07e1ff9fcdde4d72a4bcec8c6919f9d9"
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-v4-flash"

PROMPT_TEMPLATE = """You are a senior clinical tutor writing a structured reference entry for a junior doctor (FY1/PRHO level) who is actively seeing patients on the ward. They may have knowledge gaps from medical school and need PATTERN RECOGNITION plus ACTIONABLE knowledge — not exam trivia, not exhaustive pathophysiology.

Generate a structured clinical reference entry for: [TOPIC]

Output STRICTLY in this Markdown structure. Use bullets, not prose. Be dense, scannable, and ward-orientated. Aim for 600-900 words total.

## [Topic Name]
**One-liner:** <=25 words — what it is, who gets it, why it matters.

### Presentation
- Cardinal symptoms (the 3-5 things you'll actually see)
- Key exam findings
- Red flags that change urgency

### Differential Diagnosis
- Most likely -> less likely, with 1-line differentiators

### Investigations
- **Bedside:** what to do in the first hour
- **Bloods:** panels + key markers
- **Imaging:** first-line, second-line
- **Special tests:** if relevant
- Diagnostic criteria / scoring system (name + key thresholds)

### Management
- **Immediate (first hour / ED):**
- **Ward (first 24-72h):**
- **Long-term / outpatient:**

### Drugs & Doses
- First-line agents — name + dose + route + duration
- Common alternatives
- Key contraindications / interactions

### Complications
- **Acute:**
- **Chronic:**

### Prognosis
- 1-2 lines on mortality / recovery / chronicity

### Pearls & Pitfalls
- 3-5 high-yield clinical pearls
- Common mistakes juniors make

### Escalation Criteria
- When to call senior / ICU / crash team
- Specific thresholds (NEWS2, lactate, GCS, etc.)
"""

TOPIC = "Pericarditis"


def call_deepseek(prompt: str, max_retries: int = 3) -> dict:
    """Call DeepSeek API with retry logic."""
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a senior clinical tutor. Follow the structure exactly."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "stream": False,
        "max_tokens": 4000,
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
            with urlopen(req, timeout=120) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw)
                return data
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
    """Parse the markdown response into a structured dict keyed by section."""
    sections = {}
    current_section = None
    current_buf = []

    # Use first ## as the topic header (skip it, we already have title)
    # Then walk through ### sub-headings
    for line in md.splitlines():
        h3 = re.match(r"^###\s+(.+?)\s*$", line)
        if h3:
            if current_section:
                sections[current_section] = "\n".join(current_buf).strip()
            current_section = h3.group(1).strip()
            current_buf = []
        else:
            if current_section is None:
                continue  # skip lines before first section
            current_buf.append(line)

    if current_section:
        sections[current_section] = "\n".join(current_buf).strip()

    # Pull out the one-liner from the top of the markdown if present
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
    print(f"Generating clinical reference for: {TOPIC}")
    prompt = PROMPT_TEMPLATE.replace("[TOPIC]", TOPIC)

    try:
        response = call_deepseek(prompt)
    except Exception as e:
        print(f"FATAL: {e}", file=sys.stderr)
        sys.exit(1)

    if "choices" not in response or not response["choices"]:
        print(f"ERROR: unexpected response shape: {json.dumps(response)[:500]}", file=sys.stderr)
        sys.exit(1)

    content = response["choices"][0]["message"]["content"]
    usage = response.get("usage", {})

    print(f"\n  tokens used: prompt={usage.get('prompt_tokens')}, "
          f"completion={usage.get('completion_tokens')}, "
          f"total={usage.get('total_tokens')}")
    print(f"  response length: {len(content)} chars")

    structured = parse_markdown_to_structured(content, TOPIC)
    structured["metadata"] = {
        "model": MODEL,
        "tokensUsed": usage,
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    out_dir = Path("/home/z/my-project/data")
    out_dir.mkdir(parents=True, exist_ok=True)

    md_path = out_dir / "pericarditis.md"
    md_path.write_text(content, encoding="utf-8")
    print(f"  saved markdown -> {md_path}")

    json_path = out_dir / "pericarditis.json"
    json_path.write_text(json.dumps(structured, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  saved json     -> {json_path}")

    print(f"\nSections parsed: {list(structured['sections'].keys())}")
    print("DONE.")


if __name__ == "__main__":
    main()
