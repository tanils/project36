import json
<<<<<<< HEAD
from google import genai

SYSTEM = """You are an Indian stock-market news intelligence analyst.
Rank events for a short-term trader. Do not give generic summaries.
Never invent stock impact. If uncertain, use UNKNOWN.
Return JSON only with:
impact_score, trading_relevance, confidence (0-100 integers),
direction, horizon, category, affected_stocks, affected_sectors,
status, why_it_matters (max 300 chars)."""
=======
from openai import OpenAI

SYSTEM = """You are an Indian stock-market news intelligence analyst.
Your job is to rank events for a short-term trader, not to provide generic news summaries.
Prefer official/company/exchange/regulatory confirmation.
Never invent a stock impact. If uncertain, say UNKNOWN.
Return JSON only with:
impact_score (0-100), trading_relevance (0-100), confidence (0-100),
direction (POSITIVE/NEGATIVE/NEUTRAL/MIXED/UNKNOWN),
horizon (INTRADAY/1-3 DAYS/3-10 DAYS/10-45 DAYS/LONG_TERM/UNKNOWN),
category, affected_stocks (NSE tickers), affected_sectors,
status (CONFIRMED/UNCONFIRMED/CONFLICTING),
why_it_matters (max 300 chars)."""
>>>>>>> 1bb262fe1f566ac7525c703936945d74ba5484e5

def enrich(events, api_key, company_map):
    if not api_key:
        return events
<<<<<<< HEAD
    client = genai.Client(api_key=api_key)
=======
    client = OpenAI(api_key=api_key)
>>>>>>> 1bb262fe1f566ac7525c703936945d74ba5484e5
    for e in events:
        payload = {
            "title": e.title,
            "summary": e.summary,
            "current_stocks_detected": e.companies,
            "current_sectors_detected": e.sectors,
            "category": e.category,
<<<<<<< HEAD
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
=======
            "source_count": len(e.articles)
        }
        try:
            r = client.chat.completions.create(
                model="gpt-5-mini",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": json.dumps(payload)}
                ],
                temperature=0.1
            )
            data = json.loads(r.choices[0].message.content)
            e.impact_score = int(data.get("impact_score", e.impact_score))
            e.trading_relevance = int(data.get("trading_relevance", e.trading_relevance))
            e.confidence = int(data.get("confidence", e.confidence))
            e.direction = data.get("direction", e.direction)
            e.horizon = data.get("horizon", e.horizon)
            e.category = data.get("category", e.category)
            e.companies = data.get("affected_stocks", e.companies) or e.companies
            e.sectors = data.get("affected_sectors", e.sectors) or e.sectors
            e.status = data.get("status", e.status)
            e.why_it_matters = data.get("why_it_matters", e.why_it_matters)
        except Exception as exc:
            print(f"[WARN] AI enrichment failed: {exc}")
>>>>>>> 1bb262fe1f566ac7525c703936945d74ba5484e5
    return events
