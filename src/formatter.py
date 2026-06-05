from datetime import datetime, timezone, timedelta

CATEGORY_EMOJIS = {
    "Macro Economy": "\U0001f4c8",
    "Corporate": "\U0001f3ed",
    "Markets": "\U0001f4ca",
    "Global Markets": "\U0001f30d",
    "Geopolitical": "\U0001f6e1\ufe0f",
    "Policy & Regulation": "\U0001f4dc",
    "AI & Technology": "\U0001f916",
}

CATEGORY_ORDER = [
    "Geopolitical",
    "AI & Technology",
    "Macro Economy",
    "Policy & Regulation",
    "Corporate",
    "Global Markets",
    "Markets",
]

IST = timezone(timedelta(hours=5, minutes=30))


def fmt_ticker_list(companies):
    if not companies:
        return ""
    sectors = set()
    sub_sectors = set()
    symbols = []
    for c in companies:
        symbols.append(c["symbol"])
        if c.get("sector"):
            sectors.add(c["sector"])
        if c.get("sub_sector"):
            sub_sectors.add(c["sub_sector"])
    parts = []
    if symbols:
        parts.append("NSE: " + ", ".join(symbols[:8]))
    if sub_sectors:
        parts.append("Sector: " + ", ".join(sorted(sub_sectors)[:3]))
    return " | ".join(parts)


def format_message(articles, date_str=None):
    if not date_str:
        date_str = datetime.now(IST).strftime("%d %b %Y")

    lines = [f"\U0001f4f0 *Indian Market Brief \u2014 8 AM | {date_str}*"]
    lines.append("")
    lines.append("\u2501" * 35)

    grouped = {}
    rest = []
    for art in articles:
        cat = art.get("category", "Markets")
        if cat in CATEGORY_ORDER:
            grouped.setdefault(cat, []).append(art)
        else:
            rest.append(art)
    if rest:
        grouped["Markets"] = rest

    sorted_cats = [c for c in CATEGORY_ORDER if c in grouped]
    other_cats = [c for c in grouped if c not in CATEGORY_ORDER]
    sorted_cats.extend(other_cats)

    for cat in sorted_cats:
        cat_articles = grouped[cat]
        emoji = CATEGORY_EMOJIS.get(cat, "\U0001f4f0")
        lines.append(f"\n{emoji} *{cat.upper()}*")
        lines.append("")
        for i, art in enumerate(cat_articles[:8], 1):
            title = art.get("title", "Untitled")
            url = art.get("url", "")
            score = art.get("rank_score", 0)
            companies = art.get("mentioned_companies", [])
            summary = art.get("summary", "") or ""
            if len(summary) > 200:
                summary = summary[:197] + "..."

            lines.append(f"{'=' * 40}")
            lines.append(f"*{title}*")
            lines.append(f"\u2b50 Importance: {int(score)}/10")
            if summary:
                lines.append(f"_{summary}_")
            ticker_line = fmt_ticker_list(companies)
            if ticker_line:
                lines.append(ticker_line)
            if url:
                lines.append(f"\U0001f517 [Read more]({url})")
            lines.append("")

    if len(articles) == 0:
        lines.append("No news articles found today.")

    lines.append("\u2501" * 35)
    lines.append(f"_Delivered by Indian Market News Bot_")
    return "\n".join(lines)
