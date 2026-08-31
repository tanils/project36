import os, sys, json, urllib.request, urllib.error
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

key=os.getenv("GEMINI_API_KEY","").strip()
model=os.getenv("GEMINI_MODEL","gemini-3.6-flash").strip()
if model == "gemini-3.7-flash":
    print("WARNING: GEMINI_MODEL is set to gemini-3.7-flash; use gemini-3.6-flash for the confirmed working test.")
print("=== Gemini Local Test ===")
print("GEMINI_API_KEY:", "present" if key else "MISSING")
print("GEMINI_MODEL:", model)
if not key:
    sys.exit("ERROR: Add GEMINI_API_KEY to .env")

url=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
body={"contents":[{"parts":[{"text":"Reply with exactly GEMINI_OK"}]}]}
req=urllib.request.Request(
    url,
    data=json.dumps(body).encode(),
    headers={"Content-Type":"application/json","x-goog-api-key":key},
    method="POST")
try:
    with urllib.request.urlopen(req,timeout=45) as r:
        data=json.loads(r.read().decode())
    text=data["candidates"][0]["content"]["parts"][0]["text"]
    print("Gemini authentication: OK")
    print("Model Response:", text)
except urllib.error.HTTPError as e:
    print("Gemini HTTP",e.code)
    print(e.read().decode(errors="replace")[:3000])
    sys.exit(2)
