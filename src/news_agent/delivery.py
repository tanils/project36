"""Telegram delivery with explicit API diagnostics and safe message splitting."""
import os
from typing import Iterable, List
import requests

API_BASE = "https://api.telegram.org"

def _token() -> str:
    return os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

def _chat_ids() -> List[str]:
    raw = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not raw:
        raw = os.getenv("TELEGRAM_CHAT_IDS", "").strip()  # backward compatibility
    return [x.strip() for x in raw.split(",") if x.strip()]

def _api(method: str, *, params=None, json_body=None):
    token = _token()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing")
    url = f"{API_BASE}/bot{token}/{method}"
    r = requests.get(url, params=params, timeout=30) if json_body is None else requests.post(
        url, json=json_body, timeout=30
    )
    try:
        data = r.json()
    except Exception:
        data = {"ok": False, "description": r.text}
    if not r.ok or not data.get("ok"):
        raise RuntimeError(
            f"Telegram API HTTP {r.status_code}: "
            f"{data.get('description', r.text).strip()}"
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
        me = _api("getMe")
        print(f"[OK] Telegram bot: @{me['result'].get('username', 'unknown')}")
    except Exception as exc:
        print(f"[ERROR] Telegram getMe failed: {exc}")
        return False

    ok = True
    for chat_id in ids:
        try:
            chat = _api("getChat", params={"chat_id": chat_id})
            result = chat["result"]
            name = result.get("title") or result.get("username") or result.get("first_name") or chat_id
            print(f"[OK] Telegram destination {chat_id}: {name}")
        except Exception as exc:
            print(f"[ERROR] Telegram destination {chat_id} failed: {exc}")
            ok = False
    return ok

def _chunks(text: str, limit: int = 3500) -> Iterable[str]:
    text = text or ""
    while len(text) > limit:
        cut = text.rfind("\n", 0, limit)
        if cut < 500:
            cut = limit
        yield text[:cut]
        text = text[cut:].lstrip()
    if text:
        yield text

def send_message(text: str, cfg=None) -> bool:
    # cfg is accepted for compatibility with the existing main.py.
    if not text or not text.strip():
        print("[INFO] Telegram: no alert text to send.")
        return True

    if not _token() or not _chat_ids():
        print("[ERROR] Telegram credentials are not configured")
        return False

    success = True
    for chat_id in _chat_ids():
        for part_no, chunk in enumerate(_chunks(text), 1):
            payload = {
                "chat_id": chat_id,
                "text": chunk,
                "disable_web_page_preview": True,
            }
            try:
                data = _api("sendMessage", json_body=payload)
                msg_id = data["result"].get("message_id", "?")
                print(f"[OK] Telegram message sent to {chat_id} (part {part_no}, message_id={msg_id})")
            except Exception as exc:
                print(f"[ERROR] Telegram sendMessage failed for {chat_id} (part {part_no}): {exc}")
                success = False
    return success

def send_telegram(text: str, cfg=None) -> bool:
    return send_message(text, cfg)

def deliver(text: str, cfg=None) -> bool:
    return send_message(text, cfg)
