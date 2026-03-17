import json
from pathlib import Path
from datetime import datetime


DEFAULT_IMAGES = {
    "Meta": "https://static.xx.fbcdn.net/mci_ab/public/cms/?ab_b=e&ab_page=CMS&ab_entry=797459857892055&version=1773680588&transcode_extension=webp",
    "TikTok": "https://lf-tt4b.tiktokcdn.com/obj/i18nblog/tt4b_cms/en-US/tipdilz7wysq-63reVQqHHHiOCcKFWtVWbC.png",
    "LinkedIn": "https://media.licdn.com/dms/image/v2/D4D08AQHvd0T61n0CdQ/croft-frontend-shrinkToFit1024/0/1631557065472",
    "Pinterest": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1200&q=80",
    "Reddit": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1200&q=80",
    "Snapchat": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?auto=format&fit=crop&w=1200&q=80",
    "X": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=1200&q=80",
    "YouTube / Google Ads": "https://images.unsplash.com/photo-1611162618071-b39a2ec055fb?auto=format&fit=crop&w=1200&q=80",
    "default": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1200&q=80",
}


def safe_image(platform: str, image: str) -> str:
    if not image or not image.strip():
        return DEFAULT_IMAGES.get(platform, DEFAULT_IMAGES["default"])

    image = image.strip()

    if image.startswith("data:image"):
        return DEFAULT_IMAGES.get(platform, DEFAULT_IMAGES["default"])

    return image


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
        platform = item.get("platform", "Unknown")
        image = safe_image(platform, item.get("image", ""))

        section = "Lead story" if i < 2 else "Briefing"
        edition["articles"].append({
            "platform": platform,
            "section": section,
            "headline": item.get("headline", "Untitled source"),
            "summary": item.get("summary", ""),
            "impact": f"{platform} has a live source update worth reviewing for operators and planners.",
            "action": f"Review the latest {platform} source update and decide whether it changes workflow, reporting, or testing priorities.",
            "url": item.get("url", ""),
            "image": image
        })

    latest_path.write_text(json.dumps(edition, indent=2), encoding="utf-8")
    dated_path.write_text(json.dumps(edition, indent=2), encoding="utf-8")

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
