from datetime import datetime

def format_alert(events, slot):
    if not events:
        return ""
    lines = [f"🚨 ANIL MARKET INTELLIGENCE | {slot} IST", "", "TOP MARKET-MOVING NEWS"]
    for i, e in enumerate(events, 1):
        icon = "🟢" if e.direction == "POSITIVE" else "🔴" if e.direction == "NEGATIVE" else "🟡"
        stocks = ", ".join(e.companies) if e.companies else "No specific stock identified"
        sectors = ", ".join(e.sectors) if e.sectors else "N/A"
        lines += [
            "",
            f"{i}️⃣ {icon} {e.impact_score}/100 — {e.title}",
            f"Trading relevance: {e.trading_relevance}/100 | Confidence: {e.confidence}/100",
            f"Stocks: {stocks}",
            f"Sector: {sectors}",
            f"Horizon: {e.horizon} | Status: {e.status}",
            f"Why: {e.why_it_matters}",
            f"Source: {e.articles[0].source} — {e.articles[0].url}",
        ]
    return "\n".join(lines)
