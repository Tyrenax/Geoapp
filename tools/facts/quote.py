"""Citations exactes depuis le cache Wikipédia, et compilation des brouillons de faits.

    python tools/facts/quote.py find <url> <motif>...      phrases du cache qui contiennent le motif (regex, sans casse)
    python tools/facts/quote.py get <url> <début> <fin>    extrait exact de <début> jusqu'à <fin> inclus
    python tools/facts/quote.py build <ID>...              tools/facts/drafts/<ID>.json -> data/facts/<ID>.json

Dans un brouillon, une source s'écrit {"url": ..., "from": "début", "to": "fin"} (option "nth": n-ième
occurrence de "from", 1 par défaut) ; build la remplace par {"url": ..., "quote": extrait exact}.
Une source qui porte déjà "quote" est recopiée telle quelle. Les espaces de "from"/"to" s'apparient
à n'importe quel blanc du texte (espace insécable, retour à la ligne).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "cache" / "wiki" / "index.json"
DRAFTS = ROOT / "tools" / "facts" / "drafts"
OUT = ROOT / "data" / "facts"

_index = None


def cached_text(url):
    global _index
    if _index is None:
        _index = json.loads(INDEX.read_text(encoding="utf-8")) if INDEX.exists() else {}
    entry = _index.get(url)
    if entry is None:
        raise SystemExit(f"pas en cache : {url}  (python tools/data/wiki_cache.py fetch {url})")
    if "redirect_to" in entry:
        raise SystemExit(f"URL redirigée : citer {entry['redirect_to']} et non {url}")
    return (ROOT / entry["file"]).read_text(encoding="utf-8")


def loose(fragment):
    """Regex qui apparie le fragment littéralement, tout blanc valant n'importe quelle suite de blancs."""
    return r"\s+".join(re.escape(part) for part in fragment.split())


def extract(text, start, end, nth=None):
    starts = [m.start() for m in re.finditer(loose(start), text)]
    if len(starts) < (nth or 1):
        raise ValueError(f"début introuvable ({len(starts)} occurrence(s)) : {start!r}")
    if nth is None and len(starts) > 1:
        raise ValueError(f"début ambigu ({len(starts)} occurrences, préciser \"nth\") : {start!r}")
    pos = starts[(nth or 1) - 1]
    m = re.compile(loose(end)).search(text, pos)
    if m is None:
        raise ValueError(f"fin introuvable après le début : {end!r}")
    if m.end() < len(text) and text[m.end() - 1].isalnum() and text[m.end()].isalnum():
        raise ValueError(f"la fin coupe un mot : {end!r} suivi de {text[m.end():m.end() + 10]!r}")
    quote = text[pos:m.end()]
    if len(" ".join(quote.split())) < 30:
        raise ValueError(f"extrait trop court ({len(quote)} car., minimum 30) : {start!r}")
    if len(quote) > 900:
        raise ValueError(f"extrait trop long ({len(quote)} car.) : {start!r} … {end!r}")
    return quote


def find(url, patterns):
    text = cached_text(url)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    for pattern in patterns:
        rx = re.compile(pattern, re.IGNORECASE)
        hits = [s for s in sentences if rx.search(s)]
        print(f"== {pattern} : {len(hits)} phrase(s)")
        for s in hits:
            print("  -", " ".join(s.split()))


def build(entity_id):
    draft_path = DRAFTS / f"{entity_id}.json"
    doc = json.loads(draft_path.read_text(encoding="utf-8"))
    errors = []
    for group in ("facts", "capital_facts"):
        for fact in doc.get(group, []):
            for i, src in enumerate(fact.get("sources", [])):
                if "quote" in src:
                    continue
                try:
                    quote = extract(cached_text(src["url"]), src["from"], src["to"], src.get("nth"))
                except (ValueError, SystemExit) as exc:
                    errors.append(f"{fact.get('id')} source {i + 1} : {exc}")
                    continue
                fact["sources"][i] = {"url": src["url"], "quote": quote}
    if errors:
        print(f"{entity_id} : {len(errors)} erreur(s), rien écrit")
        for e in errors:
            print("  ", e)
        return False
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{entity_id}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{entity_id} : écrit data/facts/{entity_id}.json")
    return True


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    if len(argv) >= 3 and argv[0] == "find":
        find(argv[1], argv[2:])
    elif len(argv) == 4 and argv[0] == "get":
        print(json.dumps(extract(cached_text(argv[1]), argv[2], argv[3]), ensure_ascii=False))
    elif len(argv) >= 2 and argv[0] == "build":
        ok = [build(e.upper()) for e in argv[1:]]
        return 0 if all(ok) else 1
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
