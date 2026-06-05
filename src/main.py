import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.scraper import scrape_all
from src.dedup import deduplicate
from src.ticker_map import map_companies
from src.ranker import rank_articles
from src.formatter import format_message
from src.telegram import send_message
from datetime import datetime, timezone, timedelta


def main():
    print("=" * 50)
    print("INDIAN MARKET NEWS BOT")
    print("=" * 50)

    articles = scrape_all()

    articles = deduplicate(articles)

    company_map = map_companies(articles)

    top_articles = rank_articles(articles, company_map)

    print(f"\nTop {len(top_articles)} articles selected")
    for a in top_articles:
        companies = a.get("mentioned_companies", [])
        tickers = [c["symbol"] for c in companies[:5]]
        print(f"  [{a['rank_score']}] {a['title'][:80]} -> {', '.join(tickers) if tickers else '-'}")

    message = format_message(top_articles)

    success = send_message(message)

    if success:
        print("\nDone! News brief delivered.")
    else:
        print("\nDone! Run with TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to deliver.")
        try:
            print("\n--- PREVIEW ---")
            print(message[:2000])
            print("... (truncated)")
            print("--- END PREVIEW ---")
        except UnicodeEncodeError:
            print("\n--- PREVIEW (saved to preview.txt) ---")
            with open("preview.txt", "w", encoding="utf-8") as f:
                f.write(message[:3000])
            print("Preview written to preview.txt")


if __name__ == "__main__":
    main()
