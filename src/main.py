import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.scraper import scrape_all
from src.dedup import deduplicate
from src.ticker_map import map_companies
from src.ranker import rank_articles
from src.formatter import format_message
from src.telegram import send_message
from src.market_data import get_market_overview
from src.market_formatter import format_market_overview


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

    news_message = format_message(top_articles)
    news_ok = send_message(news_message)

    market_data = get_market_overview(top_articles)
    market_message = format_market_overview(market_data)
    market_ok = send_message(market_message)

    if news_ok and market_ok:
        print("\nDone! Both messages delivered to Telegram.")
    elif news_ok:
        print("\nDone! News delivered, market overview failed.")
    elif market_ok:
        print("\nDone! Market overview delivered, news failed.")
    else:
        print("\nBoth messages failed.")
        try:
            print("\n--- MARKET PREVIEW (first 2000 chars) ---")
            print(market_message[:2000])
            print("\n--- END PREVIEW ---")
        except UnicodeEncodeError:
            with open("preview_market.txt", "w", encoding="utf-8") as f:
                f.write(market_message[:3000])
            print("Market preview written to preview_market.txt")


if __name__ == "__main__":
    main()
