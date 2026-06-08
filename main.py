from scraper import fetch_all
from filter import filter_items
from digest import send_digest


def main():
    print("=== Research Digest Agent ===")
    print("Step 1: Fetching sources...")
    items = fetch_all(days_back=1)

    if not items:
        print("No items fetched. Sending empty digest.")
        send_digest([])
        return

    print(f"\nStep 2: Filtering {len(items)} items with Claude...")
    filtered = filter_items(items)

    print(f"\nStep 3: Sending digest ({len(filtered)} items)...")
    send_digest(filtered)

    print("\nDone.")


if __name__ == "__main__":
    main()
