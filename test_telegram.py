import os, sys, json, urllib.request, urllib.parse, urllib.error
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

token=os.getenv("TELEGRAM_BOT_TOKEN","").strip()
raw=os.getenv("TELEGRAM_CHAT_ID","").strip() or os.getenv("TELEGRAM_CHAT_IDS","").strip()
chat_ids=[x.strip() for x in raw.split(",") if x.strip()]
print("=== Telegram Local Test ===")
print(f"TELEGRAM_BOT_TOKEN: {'present' if token else 'MISSING'}")
print(f"TELEGRAM_CHAT_ID: {'present' if chat_ids else 'MISSING'}")
if not token or not chat_ids:
    sys.exit("ERROR: Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env")
base=f"https://api.telegram.org/bot{token}"

def call(path, payload=None):
    data=None
    headers={}
    if payload is not None:
        data=json.dumps(payload).encode(); headers["Content-Type"]="application/json"
    req=urllib.request.Request(base+path,data=data,headers=headers,method="POST" if payload is not None else "GET")
    try:
        with urllib.request.urlopen(req,timeout=30) as r: return r.status,json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body=e.read().decode(errors="replace")
        try: return e.code,json.loads(body)
        except Exception: return e.code,{"ok":False,"description":body}

status,data=call("/getMe")
print(f"getMe HTTP: {status}")
if not data.get("ok"): sys.exit(f"Telegram bot error: {data.get('description')}")
print(f"Bot: @{data['result'].get('username','unknown')}")
for chat_id in chat_ids:
    status,data=call("/getChat",{"chat_id":chat_id})
    print(f"getChat {chat_id} HTTP: {status}")
    if not data.get("ok"):
        sys.exit(f"Chat validation failed for {chat_id}: {data.get('description')}")
    chat=data["result"]
    print(f"Chat OK: {chat.get('title') or chat.get('username') or chat.get('first_name') or chat.get('id')}")
    status,data=call("/sendMessage",{"chat_id":chat_id,"text":"anilnewtrade local Telegram test successful."})
    print(f"sendMessage {chat_id} HTTP: {status}")
    if not data.get("ok"):
        sys.exit(f"Telegram send failed for {chat_id}: {data.get('description')}")
print("Telegram message: SENT")
