import os
import requests

def main():
    print("=== Credential diagnostics ===")
    for name in ("GEMINI_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"):
        print(f"{name}: {'present' if os.getenv(name, '').strip() else 'MISSING'}")

    key=os.getenv("GEMINI_API_KEY","").strip()
    model=os.getenv("GEMINI_MODEL","gemini-3.6-flash").strip()
    if key:
        try:
            r=requests.get(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}",
                headers={"x-goog-api-key": key},
                timeout=30,
            )
            print(f"Gemini metadata HTTP: {r.status_code}")
            if r.ok:
                print(f"Gemini model available: {model}")
            else:
                print(r.text[:1000])
        except Exception as e:
            print(f"Gemini metadata error: {e}")

    token=os.getenv("TELEGRAM_BOT_TOKEN","").strip()
    chats=os.getenv("TELEGRAM_CHAT_ID","").strip() or os.getenv("TELEGRAM_CHAT_IDS","").strip()
    if token:
        try:
            r=requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=30)
            data=r.json()
            print(f"Telegram getMe HTTP: {r.status_code}")
            if data.get("ok"):
                print(f"Telegram bot: @{data['result'].get('username','unknown')}")
            else:
                print(f"Telegram error: {data.get('description', r.text)}")
        except Exception as e:
            print(f"Telegram getMe error: {e}")

    if token and chats:
        for chat_id in [x.strip() for x in chats.split(",") if x.strip()]:
            try:
                r=requests.get(
                    f"https://api.telegram.org/bot{token}/getChat",
                    params={"chat_id": chat_id},
                    timeout=30,
                )
                data=r.json()
                print(f"Telegram getChat {chat_id} HTTP: {r.status_code}")
                if data.get("ok"):
                    c=data["result"]
                    print(f"Telegram destination OK: {c.get('title') or c.get('username') or c.get('first_name') or chat_id}")
                else:
                    print(f"Telegram destination error: {data.get('description', r.text)}")
            except Exception as e:
                print(f"Telegram getChat error for {chat_id}: {e}")

if __name__ == "__main__":
    main()
