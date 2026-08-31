import requests

MAX_TELEGRAM_TEXT=3500

def _api(token,method,**kwargs):
    r=requests.post(f"https://api.telegram.org/bot{token}/{method}",timeout=20,**kwargs)
    try: data=r.json()
    except Exception: data={"ok":False,"description":r.text[:1000]}
    if not r.ok or not data.get("ok"):
        raise RuntimeError(f"Telegram API HTTP {r.status_code}: {data.get('description',r.text[:1000])}")
    return data

def validate_telegram(token,chat_id):
    if not token or not chat_id: raise RuntimeError("missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
    me=_api(token,"getMe")
    chat=_api(token,"getChat",params={"chat_id":chat_id})
    print(f"[OK] Telegram bot: @{me['result'].get('username','unknown')}")
    print(f"[OK] Telegram destination: {chat['result'].get('title') or chat['result'].get('username') or chat['result'].get('id')}")
    return True

def _chunks(text):
    while len(text)>MAX_TELEGRAM_TEXT:
        cut=text.rfind("\n",0,MAX_TELEGRAM_TEXT)
        if cut<1000: cut=MAX_TELEGRAM_TEXT
        yield text[:cut]; text=text[cut:].lstrip()
    if text: yield text

def send_telegram(token,chat_id,text):
    token=(token or '').strip(); chat_id=(chat_id or '').strip()
    if not token or not chat_id: raise RuntimeError("Telegram credentials not configured: missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
    for part in _chunks(text):
        data=_api(token,"sendMessage",json={"chat_id":chat_id,"text":part,"disable_web_page_preview":True})
        print(f"[OK] Telegram delivered message_id={data['result'].get('message_id')}")

def deliver(text,cfg):
    if not text: print("[INFO] No qualifying new events; nothing sent."); return False
    if not cfg.get("enable_telegram",True): print("[INFO] Telegram disabled."); return False
    try:
        ids=[x.strip() for x in str(cfg.get('telegram_chat_id','')).split(',') if x.strip()]
        if not ids: raise RuntimeError("TELEGRAM_CHAT_ID is empty")
        for cid in ids: send_telegram(cfg['telegram_token'],cid,text)
        return True
    except Exception as exc:
        print(f"[ERROR] Telegram failed: {exc}"); return False
