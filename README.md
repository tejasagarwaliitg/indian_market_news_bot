# Indian Market News Bot

Daily 8 AM IST Telegram bot delivering the top 25 financial news articles relevant to the Indian stock market, sorted by importance.

## Features

- **Scrapes** 8+ sources: Moneycontrol, Economic Times, Business Standard, Livemint, Google Finance, RBI press releases, NSE announcements
- **Deduplicates** articles by URL and title similarity
- **Ranks** using rule-based scoring: recency, source authority, keyword importance, company mentions
- **Extracts** affected companies with NSE tickers, sectors, and sub-sectors
- **Delivers** top 25 stories via Telegram with summaries and links

## Setup

### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts
3. Copy the bot token (looks like `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
4. Send `/start` to your bot
5. Get your chat ID by sending a message to [@userinfobot](https://t.me/userinfobot)

### 2. Fork / Clone this repo

```bash
git clone <your-repo-url>
cd indian-market-news-bot
```

### 3. Add GitHub Secrets

Go to **Settings > Secrets and variables > Actions** and add:

| Secret | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Your bot token from BotFather |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID |

### 4. Enable the workflow

The workflow runs automatically at **2:30 AM UTC (8:00 AM IST)** daily. You can also trigger it manually from the Actions tab.

## Local Testing

```bash
pip install -r requirements.txt
TELEGRAM_BOT_TOKEN=your_token TELEGRAM_CHAT_ID=your_chat_id python src/main.py
```
