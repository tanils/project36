import requests

def send_telegram(token, chat_id, text):
    if not token or not chat_id:
        raise RuntimeError("Telegram credentials not configured")
<<<<<<< HEAD
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=20,
=======
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    r = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=20)
    r.raise_for_status()

def send_whatsapp(token, phone_id, to, template_name, language, text):
    if not all([token, phone_id, to, template_name]):
        raise RuntimeError("WhatsApp template credentials not configured")
    # Proactive WhatsApp Business messages generally require an approved template.
    # This implementation sends a template with one text parameter containing the report.
    url = f"https://graph.facebook.com/v23.0/{phone_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language},
            "components": [{
                "type": "body",
                "parameters": [{"type": "text", "text": text[:4000]}]
            }]
        }
    }
    r = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload, timeout=20
>>>>>>> 1bb262fe1f566ac7525c703936945d74ba5484e5
    )
    r.raise_for_status()

def deliver(text, cfg):
    if not text:
        print("[INFO] No qualifying new events; nothing sent.")
        return False
<<<<<<< HEAD
    try:
        send_telegram(cfg["telegram_token"], cfg["telegram_chat_id"], text)
        print("[OK] Telegram delivered")
        return True
    except Exception as exc:
        print(f"[ERROR] Telegram failed: {exc}")
        return False
=======

    if cfg["enable_whatsapp"]:
        try:
            send_whatsapp(
                cfg["whatsapp_token"], cfg["whatsapp_phone_id"], cfg["whatsapp_to"],
                cfg["whatsapp_template"], cfg["whatsapp_language"], text
            )
            print("[OK] WhatsApp delivered")
            return True
        except Exception as exc:
            print(f"[WARN] WhatsApp failed: {exc}")

    if cfg["enable_telegram"]:
        try:
            send_telegram(cfg["telegram_token"], cfg["telegram_chat_id"], text)
            print("[OK] Telegram delivered")
            return True
        except Exception as exc:
            print(f"[ERROR] Telegram failed: {exc}")

    return False
>>>>>>> 1bb262fe1f566ac7525c703936945d74ba5484e5
