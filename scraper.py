import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

ARXIV_QUERIES = [
    "adversarial attack computer vision",
    "acoustic attack camera sensor",
    "object detection adversarial",
    "physical attack deep learning",
    "AI security robustness",
]

OSTI_KEYWORDS = [
    "adversarial machine learning",
    "AI cybersecurity",
    "computer vision security",
    "deep learning robustness",
]

ARS_TECHNICA_RSS = "https://feeds.arstechnica.com/arstechnica/technology-lab"


def fetch_arxiv(days_back=1):
    results = []
    since = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y%m%d")
    for query in ARXIV_QUERIES:
        url = (
            "https://export.arxiv.org/api/query"
            f"?search_query=all:{requests.utils.quote(query)}"
            f"&sortBy=submittedDate&sortOrder=descending&max_results=10"
        )
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            root = ET.fromstring(resp.text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            for entry in root.findall("atom:entry", ns):
                published = entry.find("atom:published", ns).text[:10].replace("-", "")
                if published < since:
                    continue
                title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
                summary = entry.find("atom:summary", ns).text.strip().replace("\n", " ")[:300]
                link = entry.find("atom:id", ns).text.strip()
                authors = [
                    a.find("atom:name", ns).text
                    for a in entry.findall("atom:author", ns)
                ][:3]
                results.append({
                    "source": "arXiv",
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "authors": ", ".join(authors),
                    "date": entry.find("atom:published", ns).text[:10],
                })
        except Exception as e:
            print(f"arXiv error for query '{query}': {e}")
    seen = set()
    unique = []
    for r in results:
        if r["link"] not in seen:
            seen.add(r["link"])
            unique.append(r)
    return unique


def fetch_osti(days_back=1):
    results = []
    since = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%d")
    for keyword in OSTI_KEYWORDS:
        url = (
            "https://www.osti.gov/api/v1/records"
            f"?q={requests.utils.quote(keyword)}"
            f"&page=0&size=5&sort=publication_date+desc"
        )
        try:
            resp = requests.get(url, timeout=15, headers={"Accept": "application/json"})
            resp.raise_for_status()
            data = resp.json()
            for item in data.get("hits", {}).get("hits", []):
                src = item.get("_source", {})
                pub_date = src.get("publication_date", "")[:10]
                if pub_date < since:
                    continue
                results.append({
                    "source": "OSTI.gov",
                    "title": src.get("title", "No title"),
                    "summary": src.get("description", "No description available.")[:300],
                    "link": f"https://www.osti.gov/biblio/{src.get('osti_id', '')}",
                    "authors": src.get("authors", [{}])[0].get("name", "Unknown") if src.get("authors") else "Unknown",
                    "date": pub_date,
                })
        except Exception as e:
            print(f"OSTI error for keyword '{keyword}': {e}")
    seen = set()
    unique = []
    for r in results:
        if r["link"] not in seen:
            seen.add(r["link"])
            unique.append(r)
    return unique


def fetch_ars_technica(days_back=1):
    results = []
    since = datetime.now(timezone.utc) - timedelta(days=days_back)
    try:
        resp = requests.get(ARS_TECHNICA_RSS, timeout=15)
        resp.raise_for_status()
        root = ET.fromstring(resp.text)
        for item in root.findall(".//item"):
            pub_str = item.findtext("pubDate", "")
            try:
                from email.utils import parsedate_to_datetime
                pub_dt = parsedate_to_datetime(pub_str)
                if pub_dt.tzinfo is None:
                    pub_dt = pub_dt.replace(tzinfo=timezone.utc)
                if pub_dt < since:
                    continue
            except Exception:
                pass
            title = item.findtext("title", "No title").strip()
            desc = item.findtext("description", "")
            if desc:
                import re
                desc = re.sub(r"<[^>]+>", "", desc).strip()[:300]
            link = item.findtext("link", "")
            results.append({
                "source": "Ars Technica",
                "title": title,
                "summary": desc,
                "link": link,
                "authors": "Ars Technica",
                "date": pub_str[:16] if pub_str else "",
            })
    except Exception as e:
        print(f"Ars Technica RSS error: {e}")
    return results


def fetch_all(days_back=1):
    print("Fetching arXiv...")
    arxiv = fetch_arxiv(days_back)
    print(f"  {len(arxiv)} papers found")

    print("Fetching OSTI.gov...")
    osti = fetch_osti(days_back)
    print(f"  {len(osti)} publications found")

    print("Fetching Ars Technica...")
    ars = fetch_ars_technica(days_back)
    print(f"  {len(ars)} articles found")

    all_items = arxiv + osti + ars
    print(f"Total items before filtering: {len(all_items)}")
    return all_items


if __name__ == "__main__":
    items = fetch_all()
    for item in items[:5]:
        print(f"\n[{item['source']}] {item['title']}")
