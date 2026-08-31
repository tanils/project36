import hashlib
import json
import os
import time
import requests

DEFAULT_MODEL = "gemini-3.6-flash"
MAX_REQUESTS = max(0, int(os.getenv("MAX_GEMINI_REQUESTS_PER_RUN", "3")))
_REQUEST_COUNT = 0
_STOP_REASON = None

SYSTEM = """You are an Indian stock-market news intelligence analyst.
Rank events for a short-term trader. Do not give generic summaries.
Never invent stock impact. If uncertain, use UNKNOWN.
Return JSON only with: impact_score, trading_relevance, confidence (0-100 integers),
direction, horizon, category, affected_stocks, affected_sectors, status,
why_it_matters (max 300 chars)."""

def _clean_api_key(api_key):
    key=(api_key or "").strip()
    for prefix in ("Bearer ","bearer ","API_KEY=","GEMINI_API_KEY="):
        if key.startswith(prefix): key=key[len(prefix):].strip()
    if len(key)>=2 and key[0]==key[-1] and key[0] in ("'",'"'): key=key[1:-1].strip()
    return key

def credential_fingerprint(api_key):
    key=_clean_api_key(api_key)
    if not key: return "missing"
    return f"present(length={len(key)}, sha256_8={hashlib.sha256(key.encode()).hexdigest()[:8]})"

def _generate(api_key,prompt):
    global _REQUEST_COUNT,_STOP_REASON
    if _STOP_REASON:
        raise RuntimeError(_STOP_REASON)
    if _REQUEST_COUNT >= MAX_REQUESTS:
        _STOP_REASON=f"Gemini per-run request limit reached ({MAX_REQUESTS})"
        raise RuntimeError(_STOP_REASON)
    key=_clean_api_key(api_key)
    if not key: raise RuntimeError("Gemini API key is empty")
    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.2,"responseMimeType":"application/json","responseSchema":{"type":"OBJECT","properties":{"impact_score":{"type":"INTEGER"},"trading_relevance":{"type":"INTEGER"},"confidence":{"type":"INTEGER"},"direction":{"type":"STRING"},"horizon":{"type":"STRING"},"category":{"type":"STRING"},"affected_stocks":{"type":"ARRAY","items":{"type":"STRING"}},"affected_sectors":{"type":"ARRAY","items":{"type":"STRING"}},"status":{"type":"STRING"},"why_it_matters":{"type":"STRING"}},"required":["impact_score","trading_relevance","confidence","direction","horizon","category","affected_stocks","affected_sectors","status","why_it_matters"]}}}
    _REQUEST_COUNT += 1
    r=requests.post(url,headers={"Content-Type":"application/json","x-goog-api-key":key},json=payload,timeout=60)
    if r.status_code in (429,503):
        _STOP_REASON=f"Gemini temporarily unavailable (HTTP {r.status_code}); stopping further Gemini calls for this run."
        raise RuntimeError(r.text[:2000])
    if not r.ok: raise RuntimeError(f"Gemini API HTTP {r.status_code}: {r.text[:2000]}")
    data=r.json()
    try: return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError,IndexError,TypeError): raise RuntimeError(f"Gemini response did not contain text: {json.dumps(data)[:1500]}")

def test_gemini(api_key):
    return _generate(api_key,'Return JSON with impact_score=1,trading_relevance=1,confidence=1,direction=UNKNOWN,horizon=UNKNOWN,category=general,affected_stocks=[],affected_sectors=[],status=TEST,why_it_matters=authentication test.')

def enrich(events,api_key,company_map):
    if not api_key or not os.getenv("ENABLE_GEMINI","true").lower()=="true":
        print("[INFO] Gemini disabled."); return events
    for e in events:
        try:
            payload={"title":e.title,"summary":e.summary,"current_stocks_detected":e.companies,"current_sectors_detected":e.sectors,"category":e.category,"source_count":len(e.articles)}
            d=json.loads(_generate(api_key,SYSTEM+"\n\nAnalyze:\n"+json.dumps(payload,ensure_ascii=False)))
            e.impact_score=int(d.get("impact_score",e.impact_score)); e.trading_relevance=int(d.get("trading_relevance",e.trading_relevance)); e.confidence=int(d.get("confidence",e.confidence))
            e.direction=d.get("direction",e.direction); e.horizon=d.get("horizon",e.horizon); e.category=d.get("category",e.category); e.companies=d.get("affected_stocks",e.companies) or e.companies; e.sectors=d.get("affected_sectors",e.sectors) or e.sectors; e.status=d.get("status",e.status); e.why_it_matters=d.get("why_it_matters",e.why_it_matters)
        except Exception as exc:
            msg=str(exc)
            if _STOP_REASON:
                print(f"[WARN] {_STOP_REASON}"); break
            print(f"[WARN] Gemini enrichment failed: {msg}")
    print(f"[INFO] Gemini requests used this run: {_REQUEST_COUNT}/{MAX_REQUESTS}")
    return events
