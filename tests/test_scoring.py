from src.news_agent.models import Article
from src.news_agent.scoring import event_from_article

def test_company_order_scores_high():
    a = Article(
        source="Test", title="HAL receives major defence order",
        url="https://example.com", summary="Large order announced", source_priority=3
    )
    company_map = {"companies": {"HAL": {"names": ["Hindustan Aeronautics"], "sectors": ["Defence"]}}}
    e = event_from_article(a, company_map)
    assert e.impact_score >= 70
    assert "HAL" in e.companies
