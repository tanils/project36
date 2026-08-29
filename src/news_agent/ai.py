import json
import os
import requests

# Use the Gemini API-key authentication path explicitly.
# This avoids accidentally treating an API key as an OAuth bearer token.
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")

SYSTEM = """You are an Indian stock-market news intelligence analyst.
Rank events for a short-term trader. Do not give generic summaries.
Never invent stock impact. If uncertain, use UNKNOWN.
Return JSON only with:
impact_score, trading_relevance, confidence (0-100 integers),
direction, horizon, category, affected_stocks, affected_sectors,
status, why_it_matters (max 300 chars)."""


def _clean_api_key(api_key):
    """Normalize a secret copied from a secret manager without logging it."""
    key = (api_key or "").strip()
    # A Gemini API key is NOT an OAuth bearer token. Remove these only if
    # someone accidentally stored the prefix together with the key.
    for prefix in ("Bearer ", "bearer ", "API_KEY=", "GEMINI_API_KEY="):
        if key.startswith(prefix):
            key = key[len(prefix):].strip()
    # Remove matching quotes if the secret was pasted as "value".
    if len(key) >= 2 and key[0] == key[-1] and key[0] in ("'", '"'):
        key = key[1:-1].strip()
    return key


def _generate(api_key, prompt):
    key = _clean_api_key(api_key)
    if not key:
        raise RuntimeError("Gemini API key is empty")

    url = GEMINI_ENDPOINT.format(model=MODEL)
    response = requests.post(
        url,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": key,
        },
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
            },
        },
        timeout=45,
    )

    if not response.ok:
        # Do not include the API key in any diagnostic output.
        raise RuntimeError(
            f"Gemini API HTTP {response.status_code}: "
            f"{response.text[:1000]}"
        )

    data = response.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(
            f"Gemini response did not contain text: {json.dumps(data)[:1000]}"
        ) from exc


def enrich(events, api_key, company_map):
    if not api_key:
        print("[INFO] Gemini disabled: GEMINI_API_KEY is empty.")
        return events

    for e in events:
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
                SYSTEM + "\n\nAnalyze:\n" +
                json.dumps(payload, ensure_ascii=False),
            )
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
            print(f"[WARN] Gemini enrichment failed: {exc}")
    return events
