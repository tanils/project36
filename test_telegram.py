import os, sys
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from src.news_agent.delivery import send_telegram

token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
chat=os.getenv("TELEGRAM_CHAT_ID", "").strip()
print("=== Telegram Local Test ===")
print("TELEGRAM_BOT_TOKEN:", "present" if token else "MISSING")
print("TELEGRAM_CHAT_ID:", "present" if chat else "MISSING")
if not token or not chat:
    sys.exit("Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env")
try:
    send_telegram(token, chat, "✅ anilnewtrade Telegram local test successful.")
    print("Telegram test: SUCCESS")
except Exception as exc:
    print(f"Telegram test: FAILED: {exc}")
    sys.exit(2)
