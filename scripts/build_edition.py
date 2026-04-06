import json
from pathlib import Path
from datetime import datetime


DEFAULT_IMAGES = {
    "Meta": "https://static.xx.fbcdn.net/mci_ab/public/cms/?ab_b=e&ab_page=CMS&ab_entry=797459857892055&version=1773680588&transcode_extension=webp",
    "TikTok": "https://lf-tt4b.tiktokcdn.com/obj/i18nblog/tt4b_cms/en-US/tipdilz7wysq-63reVQqHHHiOCcKFWtVWbC.png",
    "LinkedIn": "https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=1200&q=80",
    "Pinterest": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1200&q=80",
    "Reddit": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1200&q=80",
    "Snapchat": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?auto=format&fit=crop&w=1200&q=80",
    "X": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=1200&q=80",
    "YouTube / Google Ads": "https://images.unsplash.com/photo-1611162618071-b39a2ec055fb?auto=format&fit=crop&w=1200&q=80",
    "default": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1200&q=80",
}


FEEDS = [
    {"platform": "Meta", "title": "Meta Business News", "url": "https://www.facebook.com/business/news", "note": "Official source hub"},
    {"platform": "TikTok", "title": "TikTok Business Blog", "url": "https://ads.tiktok.com/business/en/blog", "note": "Official source hub"},
    {"platform": "LinkedIn", "title": "LinkedIn Marketing Blog", "url": "https://www.linkedin.com/business/marketing/blog", "note": "Official source hub"},
    {"platform": "Pinterest", "title": "Pinterest Business Blog", "url": "https://business.pinterest.com/blog/", "note": "Official source hub"},
    {"platform": "Reddit", "title": "Reddit Inc. Blog", "url": "https://www.redditinc.com/blog", "note": "Official source hub"},
    {"platform": "Snapchat", "title": "Snap for Business Blog", "url": "https://forbusiness.snapchat.com/blog", "note": "Official source hub"},
    {"platform": "X", "title": "X Business Blog", "url": "https://business.x.com/en/blog", "note": "Official source hub"},
    {"platform": "YouTube / Google Ads", "title": "Google Ads & Commerce Blog", "url": "https://blog.google/products/ads-commerce/", "note": "Official source hub"},
]


def safe_image(platform: str, image: str) -> str:
    if not image or not image.strip():
        return DEFAULT_IMAGES.get(platform, DEFAULT_IMAGES["default"])

    image = image.strip()
    if image.startswith("data:image"):
        return DEFAULT_IMAGES.get(platform, DEFAULT_IMAGES["default"])

    return image


def status_ok(item: dict) -> bool:
    status = (item.get("status") or "").lower()
    return status == "ok"


def normalize_articles(raw_articles: list[dict]) -> list[dict]:
    cleaned = []
    seen = set()

    for item in raw_articles:
        if not status_ok(item):
            continue

        platform = item.get("platform", "Unknown").strip() or "Unknown"
        url = (item.get("url") or "").strip()
        headline = (item.get("headline") or "").strip()
        summary = (item.get("summary") or "").strip()
        section = (item.get("section") or "Briefing").strip() or "Briefing"
        image = safe_image(platform, item.get("image", ""))

        if not headline and not summary:
            continue

        key = f"{url}|{headline}".lower()
        if key in seen:
            continue
        seen.add(key)

        cleaned.append({
            "platform": platform,
            "section": section,
            "headline": headline or f"{platform} update",
            "summary": summary,
            "impact": f"{platform} has a live source update worth reviewing for operators and planners.",
            "action": f"Review the latest {platform} source update and decide whether it changes workflow, reporting, or testing priorities.",
            "url": url,
            "image": image,
        })

    return cleaned


def build_vp_tells(articles: list[dict]) -> list[str]:
    platforms = sorted({a.get("platform", "") for a in articles if a.get("platform")})

    base = [
        "Translate platform updates into operator guidance quickly so teams know what actually changes workflow, buying, and reporting.",
        "Separate real product shifts from marketing language and focus only on what changes performance decisions.",
        "Keep source fidelity high: the headline, image, and link should always point to the same underlying platform story.",
        "Use the daily brief as a management tool so teams know what to test, pause, or reframe.",
    ]

    if len(platforms) >= 5:
        base[3] = "Use this broader cross-platform readout to identify where automation, creator workflows, and measurement expectations are converging."

    return base


def build_trend_scores(articles: list[dict]) -> list[dict]:
    platforms = {a.get("platform", "") for a in articles}
    platform_count = len(platforms)
    article_count = len(articles)

    ai_score = min(95, 70 + platform_count * 3)
    measurement_score = min(95, 68 + article_count * 2)
    creative_score = min(95, 72 + platform_count * 2)
    commerce_score = min(95, 60 + platform_count * 2)
    workflow_score = min(95, 58 + article_count * 2)

    return [
        {"name": "AI-led buying", "score": ai_score},
        {"name": "Measurement changes", "score": measurement_score},
        {"name": "Creative importance", "score": creative_score},
        {"name": "Commerce integration", "score": commerce_score},
        {"name": "UI / workflow change", "score": workflow_score},
    ]


def choose_lead_article(articles: list[dict]) -> dict:
    if not articles:
        return {}

    non_tiktok = [a for a in articles if a.get("platform") != "TikTok"]
    if non_tiktok:
        return non_tiktok[0]

    return articles[0]


def build_lead_title(articles: list[dict]) -> str:
    if not articles:
        return "Daily platform intelligence briefing"

    lead = choose_lead_article(articles)
    return lead.get("headline", "Daily platform intelligence briefing")


def build_lead_summary(articles: list[dict]) -> str:
    if not articles:
        return ""

    lead = choose_lead_article(articles)
    summary = (lead.get("summary") or "").strip()
    if summary:
        return summary

    return "Key platform developments worth reviewing across paid social planning, buying, and measurement."


def main():
    root = Path(".")
    preview_path = root / "data" / "source_preview.json"
    latest_path = root / "data" / "latest.json"
    archive_path = root / "data" / "archive.json"

    preview = json.loads(preview_path.read_text(encoding="utf-8"))
    raw_articles = preview.get("articles", [])
    articles_in = normalize_articles(raw_articles)

    if not articles_in:
        raise ValueError("source_preview.json has no usable articles")

    today_key = datetime.now().strftime("%Y-%m-%d")
    today_label = datetime.now().strftime("%B %d, %Y")
    dated_path = root / "data" / f"{today_key}.json"

    edition_articles = []
    for i, item in enumerate(articles_in):
        section = "Lead story" if i < 2 else "Briefing"
        edition_articles.append({
            "platform": item["platform"],
            "section": section,
            "headline": item["headline"],
            "summary": item["summary"],
            "impact": item["impact"],
            "action": item["action"],
            "url": item["url"],
            "image": item["image"],
            "date": today_key
        })

    edition = {
        "label": today_label,
        "date_key": today_key,
        "lead_title": build_lead_title(edition_articles),
        "lead_summary": build_lead_summary(edition_articles),
        "stats": {
            "platforms": len({a.get("platform", "") for a in edition_articles}),
            "updates": len(edition_articles),
            "highUrgency": min(3, len(edition_articles)),
            "sources": len(edition_articles),
        },
        "vp_tells": build_vp_tells(edition_articles),
        "trend_scores": build_trend_scores(edition_articles),
        "feeds": FEEDS,
        "articles": edition_articles,
    }

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

    print("No-AI editorial layer ran successfully.")
    print(f"Wrote {latest_path}")
    print(f"Wrote {dated_path}")
    print(f"Wrote {archive_path}")


if __name__ == "__main__":
    main()
