# GitHub Actions setup — v6

Required GitHub repository secrets (exact names):
- GEMINI_API_KEY
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID

Recommended environment:
- GEMINI_MODEL=gemini-3.6-flash
- MAX_GEMINI_REQUESTS_PER_RUN=3

Telegram diagnostics call getMe and getChat. The application sends plain-text
Telegram messages (no Markdown/HTML parsing), splits long messages, and prints
Telegram's API `description` on failures.

Gemini diagnostics use GET model metadata only; they do not consume a
generateContent request. HTTP 429 and 503 stop further Gemini calls for that run.

The workflow exits non-zero if Telegram delivery fails, so the failure is visible.
