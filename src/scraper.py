import feedparser
import requests
from bs4 import BeautifulSoup
from bs4 import MarkupResemblesLocatorWarning
from datetime import datetime, timezone, timedelta
import re
import time
import warnings
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

HEADERS = {"User-Agent": USER_AGENT}

RSS_FEEDS = [
    {"name": "Moneycontrol Markets", "url": "https://www.moneycontrol.com/rss/marketlinks.xml", "authority": 8},
    {"name": "Economic Times Markets", "url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms", "authority": 8},
    {"name": "Business Standard Markets", "url": "https://www.business-standard.com/rss/markets-101.rss", "authority": 8},
    {"name": "Livemint Money", "url": "https://www.livemint.com/rss/money", "authority": 7},
    {"name": "Google Finance India", "url": "https://news.google.com/rss/search?q=indian+stock+market&hl=en-IN&gl=IN&ceid=IN:en", "authority": 6},
    {"name": "Google News India Economy", "url": "https://news.google.com/rss/search?q=Indian+economy+business&hl=en-IN&gl=IN&ceid=IN:en", "authority": 6},
]

RBI_PR_URL = "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx"


def parse_date(date_str):
    if not date_str:
        return datetime.now(timezone.utc)
    try:
        from dateutil import parser as dateparser
        dt = dateparser.parse(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return datetime.now(timezone.utc)


def scrape_rss(feed_cfg):
    articles = []
    try:
        feed = feedparser.parse(feed_cfg["url"])
        for entry in feed.entries[:40]:
            pub_date = parse_date(entry.get("published", ""))
            summary = entry.get("summary", "") or entry.get("description", "") or ""
            summary = BeautifulSoup(summary, "lxml").get_text(separator=" ", strip=True)
            link = entry.get("link", "")
            articles.append({
                "title": entry.get("title", "").strip(),
                "url": link,
                "source": feed_cfg["name"],
                "source_domain": extract_domain(link),
                "published": pub_date,
                "summary": summary[:500],
                "content": summary[:1000],
            })
        print(f"  RSS {feed_cfg['name']}: {len(articles)} articles")
    except Exception as e:
        print(f"  RSS {feed_cfg['name']} failed: {e}")
    return articles


def extract_domain(url):
    m = re.search(r"https?://([^/]+)", url or "")
    return m.group(1) if m else ""


def scrape_rbi():
    articles = []
    try:
        resp = requests.get(RBI_PR_URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        links = soup.select("a[href*='PressRelease']") or soup.select("a[href*='pressrelease']")
        for a in links[:30]:
            href = a.get("href", "")
            if not href.startswith("http"):
                href = "https://www.rbi.org.in" + href
            title = a.get_text(strip=True)
            if title and len(title) > 10:
                articles.append({
                    "title": title,
                    "url": href,
                    "source": "RBI Press Release",
                    "source_domain": "rbi.org.in",
                    "published": datetime.now(timezone.utc),
                    "summary": title,
                    "content": title,
                })
        print(f"  RBI: {len(articles)} releases")
    except Exception as e:
        print(f"  RBI scrape failed: {e}")
    return articles


def scrape_nse():
    articles = []
    try:
        sess = requests.Session()
        sess.headers.update(HEADERS)
        sess.get("https://www.nseindia.com", headers=HEADERS, timeout=10)
        resp = sess.get("https://www.nseindia.com/api/latest-announcements", headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            for item in data[:30] if isinstance(data, list) else data.get("data", [])[:30]:
                title = item.get("heading", "") or item.get("title", "") or item.get("desc", "")
                articles.append({
                    "title": title,
                    "url": item.get("url", "") or f"https://www.nseindia.com/announcements/{item.get('id','')}",
                    "source": "NSE Announcements",
                    "source_domain": "nseindia.com",
                    "published": datetime.now(timezone.utc),
                    "summary": title,
                    "content": title,
                })
        print(f"  NSE: {len(articles)} announcements")
    except Exception as e:
        print(f"  NSE scrape failed: {e}")
    return articles


def scrape_all():
    print("Scraping news sources...")
    all_articles = []
    for feed_cfg in RSS_FEEDS:
        all_articles.extend(scrape_rss(feed_cfg))
        time.sleep(0.5)
    all_articles.extend(scrape_rbi())
    time.sleep(0.5)
    all_articles.extend(scrape_nse())
    print(f"Total raw articles: {len(all_articles)}")
    return all_articles
