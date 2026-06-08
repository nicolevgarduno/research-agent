import os
import json
import requests

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

SYSTEM_PROMPT = """You are a research assistant for a post-master's AI security researcher 
at Los Alamos National Laboratory working on the Advanced Systems for Cyber Security team.

Their core research interests are:
- Physical attacks on computer vision systems (CV), especially cameras and object detection models
- Acoustic/vibration-based attacks on sensors and CV pipelines (their published focus)
- Adversarial machine learning: adversarial examples, evasion attacks, robustness
- YOLO and real-time object detection vulnerabilities
- AI security broadly: model stealing, poisoning, backdoor attacks
- DOE and national lab priorities in AI/ML security
- Autonomous systems security (drones, vehicles)
- Sensor fusion attacks

You will receive a list of items (papers, articles, publications). 
Return ONLY a JSON array of the top 3-5 most relevant items.
Each object must have these exact keys: title, source, link, authors, date, summary, reason.
"reason" is a paragraph with 3-5 sentences explaining why this is relevant to their research.
Return ONLY the JSON array — no preamble, no markdown, no backticks."""


def filter_items(items):
    if not items:
        print("No items to filter.")
        return []

    items_text = json.dumps([
        {
            "title": item["title"],
            "source": item["source"],
            "link": item["link"],
            "authors": item["authors"],
            "date": item["date"],
            "summary": item["summary"],
        }
        for item in items
    ], indent=2)

    user_message = f"Here are today's items. Return the top 3-5 most relevant:\n\n{items_text}"

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 2000,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": user_message}],
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        raw = data["content"][0]["text"].strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        filtered = json.loads(raw)
        print(f"Claude selected {len(filtered)} items.")
        return filtered
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}\nRaw response: {raw}")
        return []
    except Exception as e:
        print(f"Claude API error: {e}")
        return []


if __name__ == "__main__":
    sample = [
        {
            "source": "arXiv",
            "title": "Acoustic Attack on Camera Stabilization Systems",
            "summary": "We demonstrate that acoustic signals can disrupt MEMS gyroscopes in cameras.",
            "link": "https://arxiv.org/abs/0000.00000",
            "authors": "Jane Doe",
            "date": "2025-01-01",
        }
    ]
    result = filter_items(sample)
    print(json.dumps(result, indent=2))
