def rank(events, min_impact=70, min_relevance=65, max_alerts=10):
    eligible = [
        e for e in events
        if e.impact_score >= min_impact and e.trading_relevance >= min_relevance
    ]
    eligible.sort(
        key=lambda e: (e.impact_score * 0.55 + e.trading_relevance * 0.35 + e.confidence * 0.10),
        reverse=True
    )
    return eligible[:max_alerts]
