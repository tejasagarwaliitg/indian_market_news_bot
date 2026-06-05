from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))


def fmt_bold(t):
    return f"*{t}*"


def format_market_overview(data, date_str=None):
    if not date_str:
        date_str = datetime.now(IST).strftime("%d %b %Y")
    lines = [f"\U0001f4ca *Market Overview \u2014 {date_str}*"]
    lines.append("")
    lines.append("\u2501" * 35)

    indices = data.get("indices", {})
    nifty = indices.get("nifty", "N/A")
    nifty_chg = indices.get("nifty_chg", "")
    sensex = indices.get("sensex", "N/A")
    sensex_chg = indices.get("sensex_chg", "")
    vix = indices.get("vix", "N/A")

    lines.append(f"\n\U0001f4c8 *INDICES*")
    lines.append(f"Nifty 50: {nifty}  {nifty_chg}")
    lines.append(f"Sensex:   {sensex}  {sensex_chg}")
    lines.append(f"India VIX: {vix}")

    fiidii = data.get("fiidii", {})
    fii_cash = fiidii.get("fii_cash", "N/A")
    dii_cash = fiidii.get("dii_cash", "N/A")
    fii_deriv = fiidii.get("fii_deriv", "")

    lines.append(f"\n\U0001f504 *FII / DII ACTIVITY*")
    lines.append(f"FIIs (Cash): {fii_cash}")
    lines.append(f"DIIs (Cash): {dii_cash}")
    if fii_deriv and fii_deriv != "N/A" and fii_deriv != "0.00 Cr":
        lines.append(f"FIIs (Deriv): {fii_deriv}")

    bulk = data.get("bulk_deals", [])
    if bulk:
        lines.append(f"\n\U0001f4cb *BULK DEALS*")
        for d in bulk[:6]:
            symbol = d.get("symbol", "")
            buyer = d.get("buyer", "")
            seller = d.get("seller", "")
            qty = d.get("qty", "")
            price = d.get("price", "")
            parts = []
            if buyer:
                parts.append(f"Buyer: {buyer}")
            if seller:
                parts.append(f"Seller: {seller}")
            if qty != "N/A" and qty:
                parts.append(f"Qty: {qty}")
            if price != "N/A" and price:
                parts.append(f"\u20b9{price}")
            deal_str = " | ".join(parts)
            lines.append(f"\u2022 *{symbol}* \u2014 {deal_str}")

    calls = data.get("analyst_calls", [])
    if calls:
        lines.append(f"\n\U0001f4a1 *TOP ANALYST CALLS*")
        for c in calls[:6]:
            company = c.get("company", "")
            title = c.get("title", "")
            source = c.get("source", "")
            url = c.get("url", "")
            call_str = f"\u2022 "
            if company:
                call_str += f"*{company}*: "
            call_str += f"{title[:100]}"
            if source:
                call_str += f" ({source})"
            lines.append(call_str)
            if url:
                lines.append(f"    \U0001f517 [Read more]({url})")

    lines.append("")
    lines.append("\u2501" * 35)
    lines.append(f"_Delivered by Indian Market News Bot_")
    return "\n".join(lines)
