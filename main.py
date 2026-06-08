import json
import os
from datetime import datetime, timezone, timedelta
from scraper import fetch_all
from filter import filter_items
from digest import send_digest

SEEN_LINKS_FILE = "seen_links.json"
MAX_SEEN_AGE_DAYS = 30  # forget links older than 30 days to keep file small


def load_seen_links():
    if not os.path.exists(SEEN_LINKS_FILE):
        return {}
    with open(SEEN_LINKS_FILE, "r") as f:
        data = json.load(f)
    # support both old list format and new dict format
    if isinstance(data, list):
        return {link: "2000-01-01" for link in data}
    return data


def save_seen_links(seen: dict):
    # prune links older than MAX_SEEN_AGE_DAYS
    cutoff = (datetime.now(timezone.utc) - timedelta(days=MAX_SEEN_AGE_DAYS)).strftime("%Y-%m-%d")
    pruned = {link: date for link, date in seen.items() if date >= cutoff}
    with open(SEEN_LINKS_FILE, "w") as f:
        json.dump(pruned, f, indent=2)
    print(f"Saved {len(pruned)} seen links ({len(seen) - len(pruned)} pruned).")


def deduplicate(items, seen):
    fresh = [item for item in items if item.get("link") not in seen]
    dupes = len(items) - len(fresh)
    if dupes:
        print(f"  Skipped {dupes} already-seen items.")
    return fresh


def main():
    print("=== Research Digest Agent ===")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    seen = load_seen_links()
    print(f"Loaded {len(seen)} previously seen links.")

    filtered = []
    for days_back in [1, 3, 7, 14]:
        print(f"\nFetching sources (days_back={days_back})...")
        items = fetch_all(days_back=days_back)
        print(f"  Raw items fetched: {len(items)}")

        fresh_items = deduplicate(items, seen)
        print(f"  Fresh items after dedup: {len(fresh_items)}")

        if not fresh_items:
            continue

        print(f"Filtering {len(fresh_items)} items with Claude...")
        filtered = filter_items(fresh_items)

        if len(filtered) >= 3:
            print(f"  Got {len(filtered)} relevant items. Done.")
            break
        else:
            print(f"  Only {len(filtered)} relevant items, widening window...")

    if not filtered:
        print("\nFallback: fetching last 30 days...")
        items = fetch_all(days_back=30)
        fresh_items = deduplicate(items, seen)
        filtered = filter_items(fresh_items) if fresh_items else []
        if not filtered:
            print("Nothing new in 30 days. Sending empty digest.")

    # mark sent links as seen
    for item in filtered:
        link = item.get("link")
        if link:
            seen[link] = today

    save_seen_links(seen)

    print(f"\nSending digest ({len(filtered)} items)...")
    send_digest(filtered)
    print("Done.")


if __name__ == "__main__":
    main()