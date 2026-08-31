import argparse
import sys
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

    print(f"[INFO] Market news agent starting | slot={slot}")
    articles = deduplicate(collect(sources))
    print(f"[INFO] Articles after collection/dedup: {len(articles)}")

    events = [event_from_article(a, company_map) for a in articles]
    events = filter_new(events)
    print(f"[INFO] New events: {len(events)}")

    events = enrich(events, cfg["gemini"] if cfg["enable_gemini"] else "", company_map)
    selected = rank(events, cfg["min_impact"], cfg["min_relevance"], cfg["max_alerts"])
    print(f"[INFO] Selected alerts: {len(selected)}")

    text = format_alert(selected, slot)
    if dry_run:
        print(text or "[DRY RUN] No qualifying new events.")
        return True

    if not text:
        print("[INFO] No qualifying alerts; Telegram not called.")
        return True

    if not cfg["enable_telegram"]:
        print("[INFO] Telegram disabled.")
        return True

    delivered = deliver(text, cfg)
    if delivered:
        mark_sent(selected)
        print("[OK] Alert delivery complete.")
        return True

    print("[ERROR] Alert delivery failed; state was not marked sent.")
    return False

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--slot", required=True)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    sys.exit(0 if run(args.slot, args.dry_run) else 1)
