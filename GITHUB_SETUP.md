# GitHub Actions setup

Required repository secrets: `GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
The workflow uses `gemini-3.6-flash` and `MAX_GEMINI_REQUESTS_PER_RUN=3`.
Never commit `.env` or credentials.
Run Actions -> Market News Intelligence -> Run workflow.
