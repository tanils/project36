# Local testing

Confirmed working Gemini model: `gemini-3.6-flash`.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, then add your secrets.

Test Gemini:
```powershell
python test_gemini.py
```

Test Telegram:
```powershell
python test_telegram.py
```

Run the complete agent:
```powershell
python run_local.py
```

Never commit `.env` or expose API keys/tokens.
