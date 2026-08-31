import os,sys,requests
from .config import settings
from .delivery import validate_telegram

def main():
    cfg=settings(); errors=[]
    for name in ("GEMINI_API_KEY","TELEGRAM_BOT_TOKEN","TELEGRAM_CHAT_ID"):
        if not os.getenv(name): errors.append(f"{name} is missing")
        else: print(f"[OK] {name}: present")
    if cfg.get("gemini"):
        try:
            model=os.getenv("GEMINI_MODEL","gemini-3.6-flash")
            r=requests.get(f"https://generativelanguage.googleapis.com/v1beta/models/{model}",headers={"x-goog-api-key":cfg['gemini']},timeout=20)
            print(f"[INFO] Gemini metadata HTTP: {r.status_code}")
            if not r.ok: errors.append(f"Gemini metadata HTTP {r.status_code}: {r.text[:500]}")
        except Exception as e: errors.append(f"Gemini metadata error: {e}")
    if cfg.get("telegram_token") and cfg.get("telegram_chat_id"):
        try: validate_telegram(cfg['telegram_token'],str(cfg['telegram_chat_id']).split(',')[0].strip())
        except Exception as e: errors.append(str(e))
    if errors:
        for e in errors: print(f"[ERROR] {e}")
        return 1
    print("[OK] Credential diagnostics passed")
    return 0
if __name__=='__main__': sys.exit(main())
