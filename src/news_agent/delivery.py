import requests

def send_telegram(token, chat_id, text):
    if not token or not chat_id:
        raise RuntimeError("Telegram credentials not configured")
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=20,
    )
    r.raise_for_status()

def deliver(text, cfg):
    if not text:
        print("[INFO] No qualifying new events; nothing sent.")
        return False
    try:
        send_telegram(cfg["telegram_token"], cfg["telegram_chat_id"], text)
        print("[OK] Telegram delivered")
        return True
    except Exception as exc:
        print(f"[ERROR] Telegram failed: {exc}")
        return False
