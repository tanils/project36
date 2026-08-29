import hashlib, re
from .models import Event

HIGH_IMPACT = [
    "rbi", "sebi", "government", "cabinet", "budget", "tariff", "duty",
    "interest rate", "repo rate", "order", "contract", "acquisition",
    "merger", "demerger", "buyback", "fund raising", "qip", "promoter",
    "results", "earnings", "profit", "revenue", "ebitda", "guidance",
    "dividend", "regulatory", "approval", "ban", "license", "penalty",
    "fraud", "default", "downgrade", "upgrade", "capex", "expansion"
]

CATEGORY_KEYS = {
    "REGULATORY": ["rbi", "sebi", "regulatory", "ban", "license", "penalty"],
    "GOVERNMENT": ["government", "cabinet", "budget", "ministry", "policy", "tariff", "duty"],
    "RESULTS": ["results", "earnings", "profit", "revenue", "ebitda", "guidance", "margin"],
    "CORPORATE_ACTION": ["buyback", "dividend", "qip", "fund raising", "split", "bonus"],
    "DEAL_ORDER": ["order", "contract", "acquisition", "merger", "demerger", "joint venture"],
}

def event_from_article(a, company_map):
    text = f"{a.title} {a.summary}".lower()
    companies, sectors = [], []
    for ticker, info in company_map.get("companies", {}).items():
        if any(n.lower() in text for n in info.get("names", [])) or re.search(rf"\\b{re.escape(ticker.lower())}\\b", text):
            companies.append(ticker)
            sectors.extend(info.get("sectors", []))
    companies = list(dict.fromkeys(companies))
    sectors = list(dict.fromkeys(sectors))

    keyword_hits = sum(1 for k in HIGH_IMPACT if k in text)
    impact = min(100, 45 + keyword_hits * 7 + (15 if companies else 0) + a.source_priority * 3)
    relevance = min(100, 35 + keyword_hits * 6 + (22 if companies else 0) + a.source_priority * 2)

    category = "OTHER"
    for cat, keys in CATEGORY_KEYS.items():
        if any(k in text for k in keys):
            category = cat
            break

    direction = "NEUTRAL"
    positive = ["profit", "order", "approval", "acquisition", "buyback", "dividend", "upgrade", "expansion"]
    negative = ["loss", "penalty", "ban", "fraud", "default", "downgrade", "cut", "delay"]
    p = sum(k in text for k in positive)
    n = sum(k in text for k in negative)
    if p > n: direction = "POSITIVE"
    elif n > p: direction = "NEGATIVE"

    confidence = min(100, 50 + a.source_priority * 8 + (20 if companies else 0))
    status = "CONFIRMED" if a.source_priority >= 5 else "UNCONFIRMED"
    horizon = "1-10 DAYS" if relevance >= 80 else "10-45 DAYS"

    event_id = hashlib.sha1((a.title + a.url).encode()).hexdigest()[:16]
    return Event(
        event_id=event_id, title=a.title, summary=a.summary[:500],
        articles=[a], companies=companies, sectors=sectors,
        impact_score=impact, trading_relevance=relevance,
        confidence=confidence, direction=direction, horizon=horizon,
        category=category, status=status,
        why_it_matters="Potential near-term market/stock impact based on the event type, named companies and source quality."
    )
