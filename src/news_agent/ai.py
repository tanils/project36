import hashlib
import json
import os
import requests

# Current Gemini REST API. Google recommends the Interactions API for new projects.
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions"
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")

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

    response = requests.post(
        GEMINI_ENDPOINT,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": key,
        },
        json={
            "model": MODEL,
            "input": prompt,
            "response_format": {
                "type": "text",
                "mime_type": "application/json",
                "schema": {
                    "type": "object",
                    "properties": {
                        "impact_score": {"type": "integer"},
                        "trading_relevance": {"type": "integer"},
                        "confidence": {"type": "integer"},
                        "direction": {"type": "string"},
                        "horizon": {"type": "string"},
                        "category": {"type": "string"},
                        "affected_stocks": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "affected_sectors": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "status": {"type": "string"},
                        "why_it_matters": {"type": "string"}
                    },
                    "required": [
                        "impact_score", "trading_relevance", "confidence",
                        "direction", "horizon", "category",
                        "affected_stocks", "affected_sectors",
                        "status", "why_it_matters"
                    ]
                }
            },
        },
        timeout=60,
    )

    if not response.ok:
        raise RuntimeError(
            f"Gemini API HTTP {response.status_code}: {response.text[:1200]}"
        )

    return _extract_text(response.json())


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
                SYSTEM + "\n\nAnalyze:\n" + json.dumps(payload, ensure_ascii=False),
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
