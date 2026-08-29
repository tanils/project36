from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Article:
    source: str
    title: str
    url: str
    published: str = ""
    summary: str = ""
    source_priority: int = 1

@dataclass
class Event:
    event_id: str
    title: str
    summary: str
    articles: List[Article] = field(default_factory=list)
    companies: List[str] = field(default_factory=list)
    sectors: List[str] = field(default_factory=list)
    impact_score: int = 0
    trading_relevance: int = 0
    confidence: int = 0
    direction: str = "NEUTRAL"
    horizon: str = "UNKNOWN"
    category: str = "OTHER"
    status: str = "UNCONFIRMED"
    why_it_matters: str = ""
