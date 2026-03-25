import json
import os
from pathlib import Path
from datetime import datetime

from openai import OpenAI


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


def safe_image(platform: str, image: str) -> str:
    if not image or not image.strip():
        return DEFAULT_IMAGES.get(platform, DEFAULT_IMAGES["default"])

    image = image.strip()
    if image.startswith("data:image"):
        return DEFAULT_IMAGES.get(platform, DEFAULT_IMAGES["default"])

    return image


def call_editorial_model(articles_in: list[dict]) -> dict:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing")

    client = OpenAI(api_key=api_key)

    compact_articles = []
    for item in articles_in:
        compact_articles.append({
            "platform": item.get("platform", ""),
            "headline": item.get("headline", ""),
            "summary": item.get("summary", ""),
            "url": item.get("url", ""),
            "section": item.get("section", ""),
        })

    prompt = f"""
You are writing a paid social intelligence briefing for senior media operators and VP-level leaders.

Take the source metadata below and turn it into an editorial briefing.
Be concise, strategic, and specific.
Do not sound generic or promotional.
Focus on what changes workflow, buying, reporting, or cross-functional coordination.

Return STRICT JSON only with this exact structure:
{{
  "lead_title": "string",
  "lead_summary": "string",
  "vp_tells": ["string", "string", "string", "string"],
  "trend_scores": [
    {{"name": "AI-led buying", "score": 0}},
    {{"name": "Measurement changes", "score": 0}},
    {{"name": "Creative importance", "score": 0}},
    {{"name": "Commerce integration", "score": 0}},
    {{"name": "UI / workflow change", "score": 0}}
  ],
  "articles": [
    {{
      "platform": "string",
      "headline": "rewritten editorial headline",
      "summary": "rewritten editorial summary",
      "impact": "why this matters operationally",
      "action": "clear recommended action"
    }}
  ]
}}

Rules:
- Keep exactly 4 vp_tells.
- Keep exactly 5 trend_scores with the same names shown above.
- Return one article object per source article in the same order.
- The lead_title should sound like a real daily publication headline, not like a scraped blog post title.
- The lead_summary should synthesize the overall theme across the sources.
- Use plain language, but sound sharp and credible.
- No markdown.
- No explanation outside JSON.

Source metadata:
{json.dumps(compact_articles, indent=2)}
"""

    response = client.responses.create(
        model="gpt-5",
        input=prompt,
    )

    text = response.output_text.strip()
    return json.loads(text)


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

    editorial = call_editorial_model(articles_in)

    edition = {
        "label": today_label,
        "date_key": today_key,
        "lead_title": editorial.get("lead_title", articles_in[0].get("headline", "Lead story")),
        "lead_summary": editorial.get("lead_summary", articles_in[0].get("summary", "")),
        "stats": {
            "platforms": len({a.get("platform", "") for a in articles_in}),
            "updates": len(articles_in),
            "highUrgency": min(3, len(articles_in)),
            "sources": len(articles_in),
        },
        "vp_tells": editorial.get("vp_tells", [
            "Translate platform updates into operator guidance quickly so teams know what actually changes workflow, buying, and reporting.",
            "Separate real product shifts from marketing language and focus only on what changes performance decisions.",
            "Keep source fidelity high: the headline, image, and link should always point to the same underlying platform story.",
            "Use the daily brief as a management tool so teams know what to test, pause, or reframe."
        ]),
        "trend_scores": editorial.get("trend_scores", [
            {"name": "AI-led buying", "score": 90},
            {"name": "Measurement changes", "score": 86},
            {"name": "Creative importance", "score": 88},
            {"name": "Commerce integration", "score": 77},
            {"name": "UI / workflow change", "score": 64}
        ]),
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

    editorial_articles = editorial.get("articles", [])

    for i, item in enumerate(articles_in):
        platform = item.get("platform", "Unknown")
        image = safe_image(platform, item.get("image", ""))
        ai_item = editorial_articles[i] if i < len(editorial_articles) else {}

        section = "Lead story" if i < 2 else "Briefing"

        edition["articles"].append({
            "platform": platform,
            "section": section,
            "headline": ai_item.get("headline", item.get("headline", "Untitled source")),
            "summary": ai_item.get("summary", item.get("summary", "")),
            "impact": ai_item.get("impact", f"{platform} has a live source update worth reviewing for operators and planners."),
            "action": ai_item.get("action", f"Review the latest {platform} source update and decide whether it changes workflow, reporting, or testing priorities."),
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

    print("AI editorial layer ran successfully.")
    print(f"Wrote {latest_path}")
    print(f"Wrote {dated_path}")
    print(f"Wrote {archive_path}")


if __name__ == "__main__":
    main()
