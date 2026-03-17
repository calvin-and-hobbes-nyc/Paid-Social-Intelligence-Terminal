import json
import re
from html import unescape
from pathlib import Path
from urllib.parse import urljoin

import requests


HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PaidSocialIntelBot/1.0; +https://github.com/)"
}


def extract_meta(html: str, base_url: str) -> dict:
    def find_meta(prop_names):
        for name in prop_names:
            patterns = [
                rf'<meta[^>]+property=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']+)["\']',
                rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']{re.escape(name)}["\']',
                rf'<meta[^>]+name=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']+)["\']',
                rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']{re.escape(name)}["\']',
            ]
            for pattern in patterns:
                m = re.search(pattern, html, flags=re.I)
                if m:
                    return unescape(m.group(1).strip())
        return None

    title = find_meta(["og:title", "twitter:title"])
    if not title:
        m = re.search(r"<title>(.*?)</title>", html, flags=re.I | re.S)
        title = unescape(m.group(1).strip()) if m else "Untitled source"

    description = find_meta(["og:description", "twitter:description", "description"]) or ""
    image = find_meta(["og:image", "twitter:image"]) or ""

    if image:
        image = urljoin(base_url, image)

    return {
        "title": title,
        "description": description,
        "image": image,
    }


def fetch_source(url: str) -> dict:
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    html = response.text
    return extract_meta(html, url)


def main():
    repo_root = Path(".")
    source_file = repo_root / "data" / "source_urls.json"
    out_file = repo_root / "data" / "source_preview.json"

    payload = json.loads(source_file.read_text(encoding="utf-8"))
    results = []

    for item in payload["sources"]:
        url = item["url"]
        try:
            meta = fetch_source(url)
            results.append({
                "platform": item["platform"],
                "section": item["section"],
                "url": url,
                "headline": meta["title"],
                "summary": meta["description"],
                "image": meta["image"],
                "status": "ok"
            })
            print(f"Fetched: {url}")
        except Exception as e:
            results.append({
                "platform": item["platform"],
                "section": item["section"],
                "url": url,
                "headline": "",
                "summary": "",
                "image": "",
                "status": f"error: {e}"
            })
            print(f"Failed: {url} -> {e}")

    out_file.write_text(json.dumps({"articles": results}, indent=2), encoding="utf-8")
    print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()
