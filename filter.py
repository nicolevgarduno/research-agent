import os
import json
import requests

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# Describe what YOU care about here — this is the only thing that makes the
# digest "yours." Set it via the RESEARCH_INTERESTS environment variable
# (a GitHub secret in production; an exported env var for local testing).
# It can be as short as a couple of keywords or as long as a paragraph.
RESEARCH_INTERESTS = os.environ.get(
    "RESEARCH_INTERESTS",
    "Set RESEARCH_INTERESTS to describe what you want this digest to surface "
    "(e.g. 'adversarial machine learning, computer vision security, robotics').",
)

SYSTEM_PROMPT_TEMPLATE = """You are a research assistant helping someone filter a daily list of \
papers and articles down to only what's genuinely relevant to them.

Their research interests are:
{interests}

You will receive a list of items (papers, articles, publications).
Return ONLY a JSON array of the top 3-5 most relevant items.
Each object must have these exact keys: title, source, link, authors, date, summary, reason.
"reason" is a paragraph with 3-5 sentences explaining why this is relevant to their research.
Return ONLY the JSON array — no preamble, no markdown, no backticks."""

SYSTEM_PROMPT = SYSTEM_PROMPT_TEMPLATE.format(interests=RESEARCH_INTERESTS)


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
            "title": "Sample Paper Title",
            "summary": "A sample summary for testing the filter end-to-end.",
            "link": "https://arxiv.org/abs/0000.00000",
            "authors": "Jane Doe",
            "date": "2025-01-01",
        }
    ]
    result = filter_items(sample)
    print(json.dumps(result, indent=2))
