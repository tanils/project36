import os
import requests

# Telegram documents a 4096-character text limit. Keep a safety margin because
# Python character count and Telegram's internal limits can differ for Unicode.
TELEGRAM_MAX_LENGTH = 3500


def _chat_ids(value):
    """Accept TELEGRAM_CHAT_ID or comma-separated TELEGRAM_CHAT_IDS."""
    raw = (value or "").strip()
    return [x.strip() for x in raw.split(",") if x.strip()]


def _telegram_error(response):
    """Return Telegram's safe API error without ever exposing the bot token."""
    try:
        data = response.json()
        code = data.get("error_code", response.status_code)
        desc = data.get("description") or "Unknown Telegram error"
        return f"HTTP {code}: {desc}"
    except Exception:
        return f"HTTP {response.status_code}: {response.text[:1000]}"


def _api(base, method, **kwargs):
    try:
        response = requests.request(method, base + kwargs.pop("path"), timeout=30, **kwargs)
    except requests.RequestException as exc:
        raise RuntimeError(f"Telegram network error: {exc}") from exc
    if not response.ok:
        raise RuntimeError(_telegram_error(response))
    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError(f"Telegram returned non-JSON HTTP {response.status_code}") from exc
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data.get('description', 'unknown error')}")
    return data


def validate_telegram(token, chat_id):
    """Validate bot token and every configured destination before sending."""
    token = (token or "").strip()
    ids = _chat_ids(chat_id)
    if not token or not ids:
        missing = []
        if not token:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not ids:
            missing.append("TELEGRAM_CHAT_ID")
        raise RuntimeError("Telegram credentials not configured: missing " + ", ".join(missing))

    base = f"https://api.telegram.org/bot{token}"
    me = _api(base, "GET", path="/getMe")
    bot = me.get("result", {})
    print(f"[OK] Telegram bot: @{bot.get('username', 'unknown')}")

    valid = []
    for target in ids:
        chat = _api(base, "POST", path="/getChat", json={"chat_id": target})
        info = chat.get("result", {})
        label = info.get("title") or info.get("username") or info.get("first_name") or str(target)
        print(f"[OK] Telegram destination: {label} (id={target})")
        valid.append(target)
    return valid


def _chunks(text):
    text = text or ""
    if not text:
        return []
    return [text[i:i + TELEGRAM_MAX_LENGTH] for i in range(0, len(text), TELEGRAM_MAX_LENGTH)]


def send_telegram(token, chat_id, text):
    token = (token or "").strip()
    ids = _chat_ids(chat_id)
    if not token or not ids:
        missing = []
        if not token:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not ids:
            missing.append("TELEGRAM_CHAT_ID")
        raise RuntimeError("Telegram credentials not configured: missing " + ", ".join(missing))
    if not text:
        print("[INFO] Telegram: empty message; nothing sent.")
        return 0

    # Validate destinations first. This gives a useful error before sendMessage.
    valid_ids = validate_telegram(token, ",".join(ids))
    base = f"https://api.telegram.org/bot{token}"
    chunks = _chunks(text)
    sent = 0
    failures = []

    for target in valid_ids:
        for index, chunk in enumerate(chunks, 1):
            try:
                data = _api(
                    base,
                    "POST",
                    path="/sendMessage",
                    json={
                        "chat_id": target,
                        "text": chunk,
                        "disable_web_page_preview": True,
                    },
                )
                sent += 1
                print(f"[OK] Telegram sendMessage: chat={target}, chunk={index}/{len(chunks)}")
            except Exception as exc:
                failures.append(f"chat_id={target}, chunk={index}: {exc}")
                break

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
