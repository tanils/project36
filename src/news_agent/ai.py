import json
from google import genai

SYSTEM = """You are an Indian stock-market news intelligence analyst.
Rank events for a short-term trader. Do not give generic summaries.
Never invent stock impact. If uncertain, use UNKNOWN.
Return JSON only with:
impact_score, trading_relevance, confidence (0-100 integers),
direction, horizon, category, affected_stocks, affected_sectors,
status, why_it_matters (max 300 chars)."""

def enrich(events, api_key, company_map):
    if not api_key:
        return events
    client = genai.Client(api_key=api_key)
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
            r = client.models.generate_content(
                model="gemini-3.7-flash",
                contents=SYSTEM + "\n\nAnalyze:\n" + json.dumps(payload, ensure_ascii=False),
                config={"temperature": 0.1, "response_mime_type": "application/json"},
            )
            d = json.loads(r.text)
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
