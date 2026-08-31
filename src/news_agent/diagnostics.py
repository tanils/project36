import os
import requests
from .ai import credential_fingerprint


def main():
    gemini = os.getenv('GEMINI_API_KEY', '')
    model = os.getenv('GEMINI_MODEL', 'gemini-3.6-flash')
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    telegram_chat = os.getenv('TELEGRAM_CHAT_ID', '')

    print('=== Credential diagnostics ===')
    print(f'GEMINI_API_KEY: {credential_fingerprint(gemini)}')
    print(f'GEMINI_MODEL: {model}')
    print(f'TELEGRAM_BOT_TOKEN: {"present" if telegram_token else "missing"}')
    print(f'TELEGRAM_CHAT_ID: {"present" if telegram_chat else "missing"}')

    if gemini:
        try:
            r = requests.get(
                f'https://generativelanguage.googleapis.com/v1beta/models/{model}',
                headers={'x-goog-api-key': gemini}, timeout=30)
            r.raise_for_status()
            methods = [x.lower() for x in r.json().get('supportedGenerationMethods', [])]
            print(f'[OK] Gemini metadata access; generateContent supported: {"generatecontent" in methods}')
        except Exception as exc:
            print(f'[ERROR] Gemini metadata check failed: {exc}')
    else:
        print('[SKIP] Gemini check: key missing')

    if telegram_token and telegram_chat:
        try:
            r = requests.get(f'https://api.telegram.org/bot{telegram_token}/getMe', timeout=20)
            r.raise_for_status()
            print('[OK] Telegram bot token test passed')
        except Exception as exc:
            print(f'[ERROR] Telegram bot token test failed: {exc}')
    else:
        print('[SKIP] Telegram test: credentials incomplete')


if __name__ == '__main__':
    main()
