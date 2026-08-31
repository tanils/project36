import hashlib
import json
import os
import requests

# Current Gemini REST API. Google recommends the Interactions API for new projects.
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
MAX_REQUESTS_PER_RUN = int(os.getenv("MAX_GEMINI_REQUESTS_PER_RUN", "3"))

SYSTEM = """You are an Indian stock-market news intelligence analyst.
Rank events for a short-term trader. Do not give generic summaries.
Never invent stock impact. If uncertain, use UNKNOWN.
Return JSON only with:
impact_score, trading_relevance, confidence (0-100 integers),
direction, horizon, category, affected_stocks, affected_sectors,
status, why_it_matters (max 300 chars)."""


def _clean_api_key(api_key):
    key = (api_key or "").strip()
    for prefix in ("Bearer ", "bearer ", "API_KEY=", "GEMINI_API_KEY="):
        if key.startswith(prefix):
            key = key[len(prefix):].strip()
    if len(key) >= 2 and key[0] == key[-1] and key[0] in ("'", '"'):
        key = key[1:-1].strip()
    return key


def credential_fingerprint(api_key):
    """Safe diagnostic: never prints the secret itself."""
    key = _clean_api_key(api_key)
    if not key:
        return "missing"
    return f"present(length={len(key)}, sha256_8={hashlib.sha256(key.encode()).hexdigest()[:8]})"


def _extract_text(data):
    # Interactions API convenience shape can vary by SDK/API revision.
    if isinstance(data.get("output_text"), str) and data["output_text"]:
        return data["output_text"]
    for step in data.get("steps", []) or []:
        if step.get("type") == "model_output":
            for content in step.get("content", []) or []:
                if isinstance(content, dict) and isinstance(content.get("text"), str):
                    return content["text"]
    raise RuntimeError(f"Gemini response did not contain text: {json.dumps(data)[:1200]}")


def _generate(api_key, prompt):
    key = _clean_api_key(api_key)
    if not key:
        raise RuntimeError("Gemini API key is empty")

    # Confirmed working endpoint/model: generateContent + x-goog-api-key.
    # Do NOT send Interactions API fields such as `input` or `response_format`.
    response = requests.post(
        GEMINI_ENDPOINT,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": key,
        },
        json={
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "OBJECT",
                    "properties": {
                        "impact_score": {"type": "INTEGER"},
                        "trading_relevance": {"type": "INTEGER"},
                        "confidence": {"type": "INTEGER"},
                        "direction": {"type": "STRING"},
                        "horizon": {"type": "STRING"},
                        "category": {"type": "STRING"},
                        "affected_stocks": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "affected_sectors": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "status": {"type": "STRING"},
                        "why_it_matters": {"type": "STRING"}
                    },
                    "required": [
                        "impact_score", "trading_relevance", "confidence",
                        "direction", "horizon", "category",
                        "affected_stocks", "affected_sectors", "status",
                        "why_it_matters"
                    ]
                }
            }
        },
        timeout=60,
    )

    if not response.ok:
        raise RuntimeError(
            f"Gemini API HTTP {response.status_code}: {response.text[:2000]}"
        )

    data = response.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        raise RuntimeError(f"Gemini response did not contain text: {json.dumps(data)[:1500]}")

def test_gemini(api_key):
    """Make one tiny authenticated request for setup verification."""
    text = _generate(api_key, 'Return a valid stock-news enrichment JSON object. Use impact_score=1, trading_relevance=1, confidence=1, direction=UNKNOWN, horizon=UNKNOWN, category=general, affected_stocks=[], affected_sectors=[], status=TEST, why_it_matters=authentication test.')
    parsed = json.loads(text)
    required = {"impact_score", "trading_relevance", "confidence", "direction", "horizon", "category", "affected_stocks", "affected_sectors", "status", "why_it_matters"}
    if not required.issubset(parsed):
        raise RuntimeError(f"Gemini test returned unexpected response: {text[:500]}")
    return True


def enrich(events, api_key, company_map):
    if not api_key:
        print("[INFO] Gemini disabled: GEMINI_API_KEY is empty.")
        return events

    request_count = 0
    for e in events:
        if request_count >= MAX_REQUESTS_PER_RUN:
            print(f"[INFO] Gemini request cap reached ({MAX_REQUESTS_PER_RUN}); remaining events use rule-based scores.")
            break

        payload = {
            "title": e.title,
            "summary": e.summary,
            "current_stocks_detected": e.companies,
            "current_sectors_detected": e.sectors,
            "category": e.category,
            "source_count": len(e.articles),
        }
        try:
            text = _generate(
                api_key,
                SYSTEM + "\n\nAnalyze:\n" + json.dumps(payload, ensure_ascii=False),
            )
            request_count += 1
            d = json.loads(text)
            e.impact_score = int(d.get("impact_score", e.impact_score))
            e.trading_relevance = int(d.get("trading_relevance", e.trading_relevance))
            e.confidence = int(d.get("confidence", e.confidence))
            e.direction = d.get("direction", e.direction)
            e.horizon = d.get("horizon", e.horizon)
            e.category = d.get("category", e.category)
            e.companies = d.get("affected_stocks", e.companies) or e.companies
            e.sectors = d.get("affected_sectors", e.sectors) or e.sectors
            e.status = d.get("status", e.status)
            e.why_it_matters = d.get("why_it_matters", e.why_it_matters)
        except Exception as exc:
            msg = str(exc)
            print(f"[WARN] Gemini enrichment failed: {msg}")
            if "HTTP 429" in msg or "RESOURCE_EXHAUSTED" in msg:
                print("[WARN] Gemini quota exhausted; stopping further Gemini calls for this run.")
                break
            if "HTTP 503" in msg or "UNAVAILABLE" in msg:
                print("[WARN] Gemini temporarily unavailable; stopping further Gemini calls for this run.")
                break
    return events
