import feedparser
from .models import Article

def collect(sources):
    articles = []
    for source in sources.get("sources", []):
        try:
            feed = feedparser.parse(source["url"])
            for e in feed.entries[:50]:
                title = getattr(e, "title", "").strip()
                url = getattr(e, "link", "").strip()
                if not title or not url:
                    continue
                summary = getattr(e, "summary", "") or ""
                articles.append(Article(
                    source=source["name"],
                    title=title,
                    url=url,
                    published=getattr(e, "published", "") or "",
                    summary=summary[:1500],
                    source_priority=int(source.get("priority", 1))
                ))
        except Exception as exc:
            print(f"[WARN] source failed: {source.get('name')}: {exc}")
    return articles
