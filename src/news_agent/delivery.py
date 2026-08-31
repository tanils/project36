import os
import requests

TELEGRAM_MAX_LENGTH = 4096


def _chat_ids(value):
    """Accept TELEGRAM_CHAT_ID or comma-separated TELEGRAM_CHAT_IDS."""
    raw = (value or "").strip()
    return [x.strip() for x in raw.split(",") if x.strip()]


def _telegram_error(response):
    try:
        data = response.json()
        desc = data.get("description") or "Unknown Telegram error"
        code = data.get("error_code", response.status_code)
        return f"HTTP {code}: {desc}"
    except Exception:
        return f"HTTP {response.status_code}: {response.text[:1000]}"


def send_telegram(token, chat_id, text):
    token = (token or "").strip()
    ids = _chat_ids(chat_id)
    if not token or not ids:
        missing = []
        if not token: missing.append("TELEGRAM_BOT_TOKEN")
        if not ids: missing.append("TELEGRAM_CHAT_ID")
        raise RuntimeError("Telegram credentials not configured: missing " + ", ".join(missing))

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    chunks = [text[i:i + TELEGRAM_MAX_LENGTH] for i in range(0, len(text), TELEGRAM_MAX_LENGTH)] or [""]
    failures = []
    sent = 0
    for target in ids:
        for chunk in chunks:
            r = requests.post(url, json={"chat_id": target, "text": chunk}, timeout=30)
            if not r.ok:
                failures.append(f"chat_id={target}: {_telegram_error(r)}")
                break
            data = r.json()
            if not data.get("ok"):
                failures.append(f"chat_id={target}: {data.get('description','Telegram returned ok=false')}")
                break
            sent += 1
    if failures:
        raise RuntimeError("; ".join(failures))
    return sent


def deliver(text, cfg):
    if not text:
        print("[INFO] No qualifying new events; nothing sent.")
        return False
    if not cfg.get("enable_telegram", True):
        print("[INFO] Telegram disabled.")
        return False
    try:
        sent = send_telegram(cfg["telegram_token"], cfg["telegram_chat_id"], text)
        print(f"[OK] Telegram delivered ({sent} message chunk(s))")
        return True
    except Exception as exc:
        print(f"[ERROR] Telegram failed: {exc}")
        return False
