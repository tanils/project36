import os
from .ai import credential_fingerprint, test_gemini
from .delivery import send_telegram


def main():
    gemini = os.getenv("GEMINI_API_KEY", "")
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat = os.getenv("TELEGRAM_CHAT_ID", "")

    print("=== Credential diagnostics ===")
    print(f"GEMINI_API_KEY: {credential_fingerprint(gemini)}")
    print(f"TELEGRAM_BOT_TOKEN: {'present' if telegram_token else 'missing'}")
    print(f"TELEGRAM_CHAT_ID: {'present' if telegram_chat else 'missing'}")

    if gemini:
        try:
            test_gemini(gemini)
            print("[OK] Gemini authentication test passed")
        except Exception as exc:
            print(f"[ERROR] Gemini authentication test failed: {exc}")
    else:
        print("[SKIP] Gemini test: key missing")

    if telegram_token and telegram_chat:
        # Telegram getMe verifies the bot token without sending a message.
        import requests
        try:
            r = requests.get(f"https://api.telegram.org/bot{telegram_token}/getMe", timeout=20)
            r.raise_for_status()
            print("[OK] Telegram bot token test passed")
        except Exception as exc:
            print(f"[ERROR] Telegram bot token test failed: {exc}")
    else:
        print("[SKIP] Telegram test: credentials incomplete")


if __name__ == "__main__":
    main()
