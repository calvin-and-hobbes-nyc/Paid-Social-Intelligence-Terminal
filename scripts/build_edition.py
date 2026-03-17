import json
from pathlib import Path


def main():
    root = Path(".")
    preview_path = root / "data" / "source_preview.json"
    latest_path = root / "data" / "latest.json"

    preview = json.loads(preview_path.read_text(encoding="utf-8"))
    articles_in = preview.get("articles", [])

    if not articles_in:
        raise ValueError("source_preview.json has no articles")

    first_article = articles_in[0]
    second_article = articles_in[1] if len(articles_in) > 1 else articles_in[0]

    edition = {
        "label": "March 17, 2026",
        "date_key": "2026-03-17",
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
    print(f"Wrote {latest_path}")


if __name__ == "__main__":
    main()
