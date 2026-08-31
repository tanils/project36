import os, sys, json, urllib.request, urllib.parse, urllib.error

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

token=os.getenv("TELEGRAM_BOT_TOKEN","").strip()
chat_id=os.getenv("TELEGRAM_CHAT_ID","").strip()

print("=== Telegram Local Test ===")
print(f"TELEGRAM_BOT_TOKEN: {'present' if token else 'MISSING'}")
print(f"TELEGRAM_CHAT_ID: {'present' if chat_id else 'MISSING'}")

if not token or not chat_id:
    print("ERROR: Add both TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env")
    sys.exit(1)

base=f"https://api.telegram.org/bot{token}"
try:
    with urllib.request.urlopen(base+"/getMe", timeout=30) as r:
        data=json.loads(r.read().decode())
    if not data.get("ok"):
        print(data)
        sys.exit(2)
    print(f"Bot: @{data['result'].get('username','unknown')}")

    payload=urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": "✅ anilnewtrade local Telegram test successful."
    }).encode()
    req=urllib.request.Request(base+"/sendMessage", data=payload, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        data=json.loads(r.read().decode())
    if data.get("ok"):
        print("Telegram message: SENT")
    else:
        print(data)
        sys.exit(3)
except urllib.error.HTTPError as e:
    print(f"Telegram HTTP {e.code}: {e.read().decode(errors='replace')[:2000]}")
    sys.exit(4)
except Exception as e:
    print(f"Telegram error: {e}")
    sys.exit(5)
