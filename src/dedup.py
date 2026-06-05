import re

def normalize_title(title):
    t = title.lower().strip()
    t = re.sub(r'[^a-z0-9\s]', '', t)
    t = re.sub(r'\s+', ' ', t)
    return t.strip()


def deduplicate(articles):
    seen_urls = set()
    seen_titles = {}
    unique = []
    for art in articles:
        url = (art.get("url") or "").strip().rstrip("/")
        if url and url in seen_urls:
            continue
        seen_urls.add(url)
        title_norm = normalize_title(art.get("title", ""))
        if title_norm:
            for seen_title in seen_titles:
                if title_similar(title_norm, seen_title):
                    break
            else:
                seen_titles[title_norm] = True
                unique.append(art)
        else:
            unique.append(art)
    print(f"Deduplicated: {len(articles)} -> {len(unique)}")
    return unique


def title_similar(a, b):
    if a == b:
        return True
    words_a = set(a.split())
    words_b = set(b.split())
    if not words_a or not words_b:
        return False
    intersection = words_a & words_b
    return len(intersection) / max(len(words_a), len(words_b)) > 0.6
