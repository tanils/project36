import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "data" / "state.json"

def load():
    if not PATH.exists():
        return {"sent_event_ids": []}
    try:
        return json.loads(PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"sent_event_ids": []}

def filter_new(events):
    state = load()
    sent = set(state.get("sent_event_ids", []))
    return [e for e in events if e.event_id not in sent]

def mark_sent(events):
    state = load()
    sent = list(dict.fromkeys(state.get("sent_event_ids", []) + [e.event_id for e in events]))
    state["sent_event_ids"] = sent[-5000:]
    PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
