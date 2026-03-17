import json
from pathlib import Path
from datetime import datetime


def main():
    root = Path(".")
    preview_path = root / "data" / "source_preview.json"
    latest_path = root / "data" / "latest.json"
    archive_path = root / "data" / "archive.json"

    preview = json.loads(preview_path.read_text(encoding="utf-8"))
    articles_in = preview.get("articles", [])

    if not articles_in:
        raise ValueError("source_preview.json has no articles")

    today_key = datetime.now().strftime("%Y-%m-%d")
    today_label = datetime.now().strftime("%B %d, %Y")
    dated_path = root / "data" / f"{today_key}.json"

    first_article = articles_in[0]

    edition = {
        "label": today_label,
        "date_key": today_key,
        "lead_title": first_article.get("headline", "Lead story"),
        "lead_summary": first_article.get("summary", ""),
        "stats": {
            "platforms": len({a.get("platform", "") for a in articles_in}),
            "updates": len(articles_in),
            "highUrgency": min(3, len(articles_in)),
            "sources": len(articles_in),
        },
        "vp_tells": [
            "Translate platform updates into operator guidance quickly so teams know what actually changes workflow, buying, and reporting.",
            "Separate real product shifts from marketing language and focus only on what changes performance decisions.",
            "Keep source fidelity high: the headline, image, and link should always point to the same underlying platform story.",
            "Use the daily brief as a management tool so teams know what to test, pause, or reframe."
        ],
        "trend_scores": [
            {"name": "AI-led buying", "score": 90},
            {"name": "Measurement changes", "score": 86},
            {"name": "Creative importance", "score": 88},
            {"name": "Commerce integration", "score": 77},
            {"name": "UI / workflow change", "score": 64}
        ],
        "feeds": [
            {"platform": "Meta", "title": "Meta Business News", "url": "https://www.facebook.com/business/news", "note": "Official source hub"},
            {"platform": "TikTok", "title": "TikTok Business Blog", "url": "https://ads.tiktok.com/business/en/blog", "note": "Official source hub"},
            {"platform": "LinkedIn", "title": "LinkedIn Marketing Blog", "url": "https://www.linkedin.com/business/marketing/blog", "note": "Official source hub"},
            {"platform": "Pinterest", "title": "Pinterest Business Blog", "url": "https://business.pinterest.com/blog/", "note": "Official source hub"},
            {"platform": "Reddit", "title": "Reddit for Business Blog", "url": "https://www.business.reddit.com/blog", "note": "Official source hub"},
            {"platform": "Snapchat", "title": "Snap for Business Blog", "url": "https://forbusiness.snapchat.com/blog", "note": "Official source hub"},
            {"platform": "X", "title": "X Business Blog", "url": "https://business.x.com/en/blog", "note": "Official source hub"},
            {"platform": "YouTube / Google Ads", "title": "Google Ads & Commerce Blog", "url": "https://blog.google/products/ads-commerce/", "note": "Official source hub"}
        ],
        "articles": []
    }

    for i, item in enumerate(articles_in):
        section = "Lead story" if i < 2 else "Briefing"
        edition["articles"].append({
            "platform": item.get("platform", "Unknown"),
            "section": section,
            "headline": item.get("headline", "Untitled source"),
            "summary": item.get("summary", ""),
            "impact": f"{item.get('platform', 'This platform')} has a live source update worth reviewing for operators and planners.",
            "action": f"Review the latest {item.get('platform', 'platform')} source update and decide whether it changes workflow, reporting, or testing priorities.",
            "url": item.get("url", ""),
            "image": item.get("image", "")
        })

    latest_path.write_text(json.dumps(edition, indent=2), encoding="utf-8")
    dated_path.write_text(json.dumps(edition, indent=2), encoding="utf-8")

    # rebuild archive.json with latest first, then dated files
    archive = [{
        "date_key": today_key,
        "label": today_label,
        "file": "latest.json"
    }]

    seen = {today_key}
    for path in sorted((root / "data").glob("*.json"), reverse=True):
        name = path.name
        if name in ("latest.json", "archive.json", "source_urls.json", "source_preview.json"):
            continue

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        date_key = data.get("date_key")
        label = data.get("label")
        if not date_key or not label or date_key in seen:
            continue

        seen.add(date_key)
        archive.append({
            "date_key": date_key,
            "label": label,
            "file": name
        })

    archive_path.write_text(json.dumps(archive, indent=2), encoding="utf-8")

    print(f"Wrote {latest_path}")
    print(f"Wrote {dated_path}")
    print(f"Wrote {archive_path}")


if __name__ == "__main__":
    main()
