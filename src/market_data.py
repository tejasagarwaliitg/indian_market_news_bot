import requests
import re
import json
from datetime import datetime, timezone, timedelta
import time

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HEADERS = {"User-Agent": USER_AGENT}


def _nse_session():
    sess = requests.Session()
    sess.headers.update(HEADERS)
    try:
        sess.get("https://www.nseindia.com", timeout=10)
        time.sleep(1)
    except:
        pass
    return sess


def get_fii_dii():
    sess = _nse_session()
    try:
        resp = sess.get("https://www.nseindia.com/api/fiidii", timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            rows = data.get("data", []) if isinstance(data, dict) else data
            if rows and isinstance(rows, list):
                latest = rows[-1]
                return {
                    "fii_cash": format_cr(parse_val(latest.get("fii_cash", 0))),
                    "dii_cash": format_cr(parse_val(latest.get("dii_cash", 0))),
                    "fii_deriv": format_cr(parse_val(latest.get("fii_deriv", 0))),
                    "date": latest.get("date", ""),
                }
    except Exception as e:
        print(f"  FII/DII scrape failed: {e}")

    try:
        resp = requests.get("https://www.moneycontrol.com/india/stockmarket/fiidii/", headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            m = re.search(r'FII.*?[-+]?\s*[\d,]+\.?\d*\s*(Cr|Crore)', resp.text, re.IGNORECASE)
            d = re.search(r'DII.*?[-+]?\s*[\d,]+\.?\d*\s*(Cr|Crore)', resp.text, re.IGNORECASE)
            fii_val = m.group(0) if m else "N/A"
            dii_val = d.group(0) if d else "N/A"
            return {"fii_cash": fii_val, "dii_cash": dii_val, "fii_deriv": "N/A", "date": "Today"}
    except:
        pass
    return {"fii_cash": "N/A", "dii_cash": "N/A", "fii_deriv": "N/A", "date": ""}


def get_indices():
    sess = _nse_session()
    result = {"nifty": "N/A", "sensex": "N/A", "vix": "N/A", "nifty_chg": "", "sensex_chg": ""}
    try:
        resp = sess.get("https://www.nseindia.com/api/allIndices", timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            for idx in data.get("data", []):
                if idx.get("index") == "NIFTY 50":
                    result["nifty"] = idx.get("last", "N/A")
                    result["nifty_chg"] = f"{idx.get('change', 0):+.2f} ({idx.get('percChange', 0):+.2f}%)"
                if idx.get("index") == "INDIA VIX":
                    result["vix"] = f"{idx.get('last', 'N/A'):.2f}"
    except Exception as e:
        print(f"  Indices scrape failed: {e}")

    try:
        resp2 = requests.get("https://api.bseindia.com/BseIndiaAPI/api/GetSensex/w?", headers={**HEADERS, "Referer": "https://www.bseindia.com/"}, timeout=10)
        if resp2.status_code == 200:
            d2 = resp2.json()
            result["sensex"] = f"{d2.get('CurrSel', 'N/A'):,}"
            result["sensex_chg"] = f"{d2.get('Chg', 0):+.2f} ({d2.get('PercChg', 0):+.2f}%)"
    except:
        try:
            resp2 = requests.get("https://www.bseindia.com/", headers=HEADERS, timeout=10)
            m = re.search(r'SENSEX.*?([\d,]+\.\d+)', resp2.text)
            if m:
                result["sensex"] = m.group(1)
        except:
            pass
    return result


def get_bulk_deals():
    sess = _nse_session()
    try:
        resp = sess.get("https://www.nseindia.com/api/snapshot-daywatch?index=BULK_DEALS", timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            deals = data.get("data", []) if isinstance(data, dict) else data
            out = []
            for d in (deals if isinstance(deals, list) else []):
                out.append({
                    "symbol": d.get("symbol", d.get("SYMBOL", "")),
                    "buyer": d.get("buyerName", d.get("BUYER_NAME", "")),
                    "seller": d.get("sellerName", d.get("SELLER_NAME", "")),
                    "qty": d.get("quantity", d.get("QTY", 0)),
                    "price": d.get("price", d.get("TRADE_PRICE", 0)),
                })
            return out[:10]
    except Exception as e:
        print(f"  Bulk deals scrape failed: {e}")

    try:
        resp = requests.get("https://www.moneycontrol.com/india/stockmarket/bulk-deals/", headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            rows = re.findall(r'<tr[^>]*>.*?</tr>', resp.text, re.DOTALL)
            deals = []
            for r in rows[:11]:
                cells = re.findall(r'<td[^>]*>(.*?)</td>', r, re.DOTALL)
                if len(cells) >= 4:
                    deals.append({
                        "symbol": re.sub(r'<[^>]+>', '', cells[0]).strip(),
                        "buyer": re.sub(r'<[^>]+>', '', cells[2] if len(cells) > 2 else cells[1]).strip(),
                        "seller": re.sub(r'<[^>]+>', '', cells[3] if len(cells) > 3 else "").strip(),
                        "qty": "N/A", "price": "N/A",
                    })
            return deals[:10]
    except:
        pass
    return []


def extract_analyst_calls(articles):
    calls = []
    keywords = ["buy", "sell", "target", "outperform", "underperform", "overweight", "underweight",
                "add", "reduce", "hold", "maintain", "upgrade", "downgrade", "accumulate",
                "subscribe", "recommendation", "target price", "rated"]
    for art in articles:
        title = (art.get("title", "") or "")
        summary = (art.get("summary", "") or "")
        combined = (title + " " + summary).lower()
        matched = [k for k in keywords if k.lower() in combined]
        if len(matched) >= 2:
            company = ""
            if "mentioned_companies" in art and art["mentioned_companies"]:
                company = ", ".join([c["symbol"] for c in art["mentioned_companies"][:2]])
            calls.append({
                "title": title[:120],
                "url": art.get("url", ""),
                "company": company or extract_ticker_from_title(title),
                "source": art.get("source", ""),
            })
    return calls[:8]


def extract_ticker_from_title(title):
    tickers = ["TCS", "INFY", "RELIANCE", "HDFCBANK", "ICICIBANK", "SBIN", "TATAMOTORS",
               "M&M", "MARUTI", "BAJFINANCE", "WIPRO", "HCLTECH", "AXISBANK", "KOTAKBANK",
               "SUNPHARMA", "NTPC", "POWERGRID", "LT", "ULTRACEMCO", "HINDUNILVR", "ONGC",
               "JSWSTEEL", "TATASTEEL", "BHARTIARTL", "ITC", "TITAN", "BAJAJFINSV", "ADANIENT",
               "ADANIPORTS", "ADANIGREEN", "ADANIPOWER", "NESTLEIND", "BRITANNIA", "DRREDDY",
               "CIPLA", "HINDALCO", "COALINDIA", "IOCL", "BPCL", "HPCL", "GAIL", "BEL", "HAL"]
    title_upper = title.upper()
    for t in tickers:
        if t in title_upper:
            return t
    return ""


def format_cr(val):
    try:
        v = float(val)
        if v >= 0:
            return f"+{v:.2f} Cr"
        return f"{v:.2f} Cr"
    except:
        return str(val)


def parse_val(val):
    try:
        return float(val)
    except:
        return 0


def get_market_overview(articles):
    print("Fetching market overview...")
    fiidii = get_fii_dii()
    indices = get_indices()
    bulk = get_bulk_deals()
    analyst_calls = extract_analyst_calls(articles)
    return {
        "fiidii": fiidii,
        "indices": indices,
        "bulk_deals": bulk,
        "analyst_calls": analyst_calls,
    }
