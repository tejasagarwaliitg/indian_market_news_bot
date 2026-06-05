import json
import os
from datetime import datetime, timezone, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


KEYWORD_CFG = None
SOURCE_AUTH = None


def get_keywords():
    global KEYWORD_CFG
    if KEYWORD_CFG is None:
        KEYWORD_CFG = load_json("importance_keywords.json")
    return KEYWORD_CFG


def get_source_authority():
    global SOURCE_AUTH
    if SOURCE_AUTH is None:
        SOURCE_AUTH = load_json("source_authority.json")
    return SOURCE_AUTH


def score_article(article, company_count):
    now = datetime.now(timezone.utc)
    pub = article.get("published", now)
    hours_ago = (now - pub).total_seconds() / 3600 if pub else 24

    recency = 10 if hours_ago <= 6 else (7 if hours_ago <= 12 else (5 if hours_ago <= 24 else (3 if hours_ago <= 48 else 1)))

    domain = article.get("source_domain", "")
    source_auth = get_source_authority()
    source_score = source_auth.get(domain, source_auth.get("default", 5))

    title = (article.get("title", "") or "") + " " + (article.get("summary", "") or "")
    title_lower = title.lower()

    kw_cfg = get_keywords()
    max_kw_score = 0
    for cfg in kw_cfg.values():
        kw_score = 0
        for kw in cfg["keywords"]:
            if kw.lower() in title_lower:
                kw_score = max(kw_score, cfg["weight"])
        max_kw_score = max(max_kw_score, kw_score)
    if max_kw_score == 0:
        max_kw_score = 2

    company_score = min(company_count * 1.5, 10)

    total = (recency * 0.25) + (source_score * 0.25) + (max_kw_score * 0.35) + (company_score * 0.15)
    return round(total, 1), max_kw_score


def get_article_category(article):
    title = (article.get("title", "") or "") + " " + (article.get("summary", "") or "")
    title_lower = title.lower()
    kw_cfg = get_keywords()
    best_cat = "Markets"
    best_weight = 0
    for cfg in kw_cfg.values():
        for kw in cfg["keywords"]:
            if kw.lower() in title_lower and cfg["weight"] > best_weight:
                best_weight = cfg["weight"]
                best_cat = cfg["category"]
                break
    return best_cat


def rank_articles(articles, company_map):
    scored = []
    for art in articles:
        mentioned = company_map.get(art.get("url", ""), [])
        score, max_kw = score_article(art, len(mentioned))
        category = get_article_category(art)
        scored.append({
            **art,
            "rank_score": score,
            "mentioned_companies": mentioned,
            "category": category,
        })
    scored.sort(key=lambda x: x["rank_score"], reverse=True)
    print(f"Ranked articles, top score: {scored[0]['rank_score'] if scored else 'N/A'}")
    return scored[:25]
