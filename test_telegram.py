import os, sys
from src.news_agent.delivery import validate_telegram, send_message
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

print("=== Telegram Local Test ===")
if not validate_telegram():
    sys.exit(1)
if not send_message("✅ anilnewtrade Telegram connectivity test successful."):
    sys.exit(2)
print("Telegram test: SUCCESS")
