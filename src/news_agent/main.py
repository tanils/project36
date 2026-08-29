import argparse
from .config import load_yaml, settings
from .collector import collect
from .dedup import deduplicate
from .scoring import event_from_article
from .ai import enrich
from .ranker import rank
from .state import filter_new, mark_sent
from .formatter import format_alert
from .delivery import deliver

def run(slot, dry_run=False):
    cfg = settings()
    sources = load_yaml("sources.yaml")
    company_map = load_yaml("company_map.yaml")

    articles = collect(sources)
    articles = deduplicate(articles)

    events = [event_from_article(a, company_map) for a in articles]
    events = filter_new(events)
    events = enrich(events, cfg["openai"] if cfg["enable_openai"] else "", company_map)
    selected = rank(events, cfg["min_impact"], cfg["min_relevance"], cfg["max_alerts"])

    text = format_alert(selected, slot)

    if dry_run:
        print(text or "[DRY RUN] No qualifying new events.")
        return

    delivered = deliver(text, cfg)
    if delivered:
        mark_sent(selected)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--slot", required=True)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    run(args.slot, args.dry_run)
