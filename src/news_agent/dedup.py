import hashlib, re
from rapidfuzz.fuzz import ratio

def normalize(text):
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower()).strip()

def deduplicate(articles):
    kept = []
    seen_hashes = set()
    for a in articles:
        key = hashlib.sha1(normalize(a.title).encode()).hexdigest()
        if key in seen_hashes:
            continue
        duplicate = False
        for k in kept:
            if ratio(normalize(a.title), normalize(k.title)) >= 88:
                duplicate = True
                break
        if not duplicate:
            kept.append(a)
            seen_hashes.add(key)
    return kept
