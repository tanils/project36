# GitHub Actions setup

Repository Secrets (exact names):
- GEMINI_API_KEY
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID

The workflow uses GEMINI_MODEL=gemini-3.6-flash by default.

Telegram diagnostics run getMe and getChat before the agent. The workflow never prints secret values.

If Telegram sendMessage fails, the log prints Telegram's API `description` instead of only `400 Client Error`.

Gemini 429/503 are handled without repeated retries; the quantitative pipeline continues.
