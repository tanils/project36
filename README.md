# Market News Intelligence Agent

A separate project for high-signal Indian stock-market news alerts. It is intentionally independent of the existing swing-trading project.

## Goals

- Collect market-moving Indian/global financial news and official announcements.
- Deduplicate articles into events.
- Score market impact and short-term trading relevance.
- Map events to affected stocks and sectors.
- Produce only the highest-value alerts.
- Scheduled runs: 08:00, 13:00, 14:00, 15:00 and 20:00 IST.
- Primary delivery: WhatsApp Cloud API.
- Fallback delivery: Telegram.
- Store event history so the same story is not repeatedly alerted.
- Keep an architecture that can later add price, volume, F&O OI, market regime and historical learning.

## Important design principle

This is an intelligence pipeline, not a headline-forwarding bot. Multiple articles describing the same event should become one event.

## Current implementation

The first version is deliberately provider-agnostic where possible:

1. RSS/HTTP collection from configured feeds.
2. Normalization and deduplication.
3. Keyword/entity detection.
4. Rule-based impact/relevance scoring.
5. Optional Gemini enrichment for stronger classification and stock mapping.
6. Top-10 selection.
7. WhatsApp primary + Telegram fallback.
8. JSON history/state.

The Gemini step is optional. Set `GEMINI_API_KEY` to enable it.

## Setup

### 1. Create a new GitHub repository

Example:

`market-news-agent`

### 2. Copy this project

Install:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` for local testing.

### 3. Configure sources

Edit:

`config/sources.yaml`

Use RSS feeds or official/public feeds that you are permitted to access. Do not bypass paywalls, robots restrictions, login walls, or anti-bot controls.

### 4. Configure companies/sectors

Edit:

`config/company_map.yaml`

Start with the liquid NSE/F&O universe and expand it over time.

### 5. Run locally

```bash
python -m src.news_agent.main --slot 20:00 --dry-run
```

To send alerts:

```bash
python -m src.news_agent.main --slot 20:00
```

### 6. GitHub Actions secrets

Add only the credentials you need:

- `GEMINI_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `WHATSAPP_ACCESS_TOKEN`
- `WHATSAPP_PHONE_NUMBER_ID`
- `WHATSAPP_TO`
- `WHATSAPP_TEMPLATE_NAME` (recommended for proactive WhatsApp notifications)
- `WHATSAPP_TEMPLATE_LANGUAGE` (for example `en_US`)

### 7. Scheduling

The workflow runs at the requested IST times by using UTC equivalents:

- 08:00 IST = 02:30 UTC
- 13:00 IST = 07:30 UTC
- 14:00 IST = 08:30 UTC
- 15:00 IST = 09:30 UTC
- 20:00 IST = 14:30 UTC

GitHub Actions cron uses UTC.

## Alert policy

The default policy is:

- Maximum 10 events per run.
- Ignore weak/noisy items.
- Deduplicate aggressively.
- Prefer official exchange/company/government sources for confirmation.
- A single-source report can be labelled `UNCONFIRMED`.
- Official/confirmed events receive higher confidence.
- Intraday slots should only send meaningful NEW events.
- If nothing crosses the threshold, the agent can send no message.

## Safety / trading note

The agent is an information-ranking system, not an investment adviser. Scores are prioritization signals, not guaranteed price predictions.

## Future phases

### Phase 2
- NSE/BSE corporate announcements.
- Results calendar.
- Corporate actions.
- Government/RBI/SEBI calendars.
- Better company relationship graph.

### Phase 3
- Live price/volume.
- Sector relative strength.
- F&O OI and PCR.
- Market regime.
- News-versus-price reaction.

### Phase 4
- Historical news-event database.
- Outcome tracking at 30m/1d/3d/5d/10d/20d.
- Backtesting.
- Calibrated scoring based on observed outcomes.
