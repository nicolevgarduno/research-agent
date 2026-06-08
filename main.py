from scraper import fetch_all
from filter import filter_items
from digest import send_digest


def main():
    print("=== Research Digest Agent ===")

    filtered = []
    for days_back in [1, 3, 7, 14]:
        print(f"Step 1: Fetching sources (days_back={days_back})...")
        items = fetch_all(days_back=days_back)
        print(f"  Total raw items: {len(items)}")

        if not items:
            continue

        print(f"Step 2: Filtering {len(items)} items with Claude...")
        filtered = filter_items(items)

        if len(filtered) >= 3:
            print(f"  Got {len(filtered)} items. Done.")
            break
        else:
            print(f"  Only {len(filtered)} items found, widening window...")

    if not filtered:
        print("No relevant items found after all windows. Sending fallback.")
        items = fetch_all(days_back=30)
        filtered = filter_items(items) or items[:3]

    print(f"Step 3: Sending digest ({len(filtered)} items)...")
    send_digest(filtered)
    print("Done.")


if __name__ == "__main__":
    main()