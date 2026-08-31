import os
import requests
from typing import Iterable, List

API = "https://api.telegram.org"

def _token():
    return os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

def _chat_ids() -> List[str]:
    raw = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    # Backward compatibility, but prefer singular variable.
    if not raw:
        raw = os.getenv("TELEGRAM_CHAT_IDS", "").strip()
    return [x.strip() for x in raw.split(",") if x.strip()]

def telegram_get(method: str, params=None):
    token = _token()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing")
    r = requests.get(f"{API}/bot{token}/{method}", params=params or {}, timeout=30)
    try:
        data = r.json()
    except Exception:
        data = {"ok": False, "error_code": r.status_code, "description": r.text}
    if not r.ok or not data.get("ok"):
        raise RuntimeError(
            f"Telegram API HTTP {r.status_code}: "
            f"{data.get('description', r.text)}"
        )
    return data

def validate_telegram() -> bool:
    token = _token()
    ids = _chat_ids()
    if not token:
        print("[ERROR] TELEGRAM_BOT_TOKEN is missing")
        return False
    if not ids:
        print("[ERROR] TELEGRAM_CHAT_ID is missing")
        return False

    try:
        me = telegram_get("getMe")
        print(f"[OK] Telegram bot: @{me['result'].get('username', 'unknown')}")
    except Exception as e:
        print(f"[ERROR] Telegram getMe failed: {e}")
        return False

    ok = True
    for chat_id in ids:
        try:
            chat = telegram_get("getChat", {"chat_id": chat_id})
            title = chat["result"].get("title") or chat["result"].get("username") or chat["result"].get("first_name") or chat_id
            print(f"[OK] Telegram destination {chat_id}: {title}")
        except Exception as e:
            print(f"[ERROR] Telegram destination {chat_id} failed: {e}")
            ok = False
    return ok

def _chunks(text: str, limit: int = 3500) -> Iterable[str]:
    text = text or ""
    while len(text) > limit:
        cut = text.rfind("\n", 0, limit)
        if cut < 1000:
            cut = limit
        yield text[:cut]
        text = text[cut:].lstrip("\n")
    if text:
        yield text

def send_message(text: str) -> bool:
    token = _token()
    ids = _chat_ids()
    if not token or not ids:
        print("[ERROR] Telegram credentials are not configured")
        return False

    success = True
    for chat_id in ids:
        for part_no, chunk in enumerate(_chunks(text), 1):
            payload = {
                "chat_id": chat_id,
                "text": chunk,
                "disable_web_page_preview": True,
            }
            try:
                r = requests.post(
                    f"{API}/bot{token}/sendMessage",
                    json=payload,
                    timeout=30,
                )
                try:
                    data = r.json()
                except Exception:
                    data = {"ok": False, "description": r.text}
                if not r.ok or not data.get("ok"):
                    print(
                        f"[ERROR] Telegram sendMessage failed for {chat_id}: "
                        f"HTTP {r.status_code}: {data.get('description', r.text)}"
                    )
                    success = False
                else:
                    print(f"[OK] Telegram message sent to {chat_id} (part {part_no})")
            except requests.RequestException as e:
                print(f"[ERROR] Telegram network error for {chat_id}: {e}")
                success = False
    return success

# Compatibility names used by older project code.
def send_telegram(text: str) -> bool:
    return send_message(text)

def deliver(text: str) -> bool:
    return send_message(text)
