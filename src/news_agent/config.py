import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

def load_yaml(name):
    with open(ROOT / "config" / name, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def settings():
    return {
        "max_alerts": int(os.getenv("MAX_ALERTS", "10")),
        "min_impact": int(os.getenv("MIN_IMPACT_SCORE", "70")),
        "min_relevance": int(os.getenv("MIN_TRADING_RELEVANCE", "65")),
<<<<<<< HEAD
        "gemini": os.getenv("GEMINI_API_KEY", ""),
        "enable_gemini": os.getenv("ENABLE_GEMINI", "true").lower() == "true",
=======
        "openai": os.getenv("OPENAI_API_KEY", ""),
        "enable_openai": os.getenv("ENABLE_OPENAI", "true").lower() == "true",
>>>>>>> 1bb262fe1f566ac7525c703936945d74ba5484e5
        "telegram_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
        "whatsapp_token": os.getenv("WHATSAPP_ACCESS_TOKEN", ""),
        "whatsapp_phone_id": os.getenv("WHATSAPP_PHONE_NUMBER_ID", ""),
        "whatsapp_to": os.getenv("WHATSAPP_TO", ""),
        "whatsapp_template": os.getenv("WHATSAPP_TEMPLATE_NAME", ""),
        "whatsapp_language": os.getenv("WHATSAPP_TEMPLATE_LANGUAGE", "en_US"),
        "enable_telegram": os.getenv("ENABLE_TELEGRAM", "true").lower() == "true",
        "enable_whatsapp": os.getenv("ENABLE_WHATSAPP", "true").lower() == "true",
    }
