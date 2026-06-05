import json
import os
import re
import unicodedata

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

TICKER_DATA = None


def load_tickers():
    global TICKER_DATA
    if TICKER_DATA is None:
        path = os.path.join(DATA_DIR, "company_tickers.json")
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        TICKER_DATA = {}
        for symbol, info in raw.items():
            names = [info["name"].lower()] + [a.lower() for a in info.get("aliases", [])]
            TICKER_DATA[symbol] = {
                "name": info["name"],
                "sector": info.get("sector", ""),
                "sub_sector": info.get("sub_sector", ""),
                "names": names,
            }
    return TICKER_DATA


def extract_companies(text):
    if not text:
        return []
    tickers = load_tickers()
    text_lower = text.lower()
    text_lower = unicodedata.normalize("NFKD", text_lower)
    found = []
    for symbol, info in tickers.items():
        for name in info["names"]:
            name_norm = unicodedata.normalize("NFKD", name.lower())
            pattern = r"(?<![a-z])" + re.escape(name_norm) + r"(?![a-z])"
            if re.search(pattern, text_lower):
                found.append({
                    "symbol": symbol,
                    "name": info["name"],
                    "sector": info["sector"],
                    "sub_sector": info["sub_sector"],
                })
                break
    return found


def map_companies(articles):
    company_map = {}
    for art in articles:
        text = (art.get("title", "") or "") + " " + (art.get("summary", "") or "") + " " + (art.get("content", "") or "")
        companies = extract_companies(text)
        company_map[art.get("url", "")] = companies
    return company_map
