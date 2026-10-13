"""Vérification indépendante de la carte d'identité contre le texte des articles Wikipédia FR en cache.

Données construit ces champs à partir de Wikidata, de mledoze/countries et de tableaux de Wikipédia EN.
Ce script recoupe avec une autre source : le texte de l'article FR de l'entité (et de sa capitale).
Pour chaque langue, monnaie, gentilé et point culminant, il cherche la mention dans le texte.

    python tools/data/verif_identite.py            résumé + entrées non retrouvées
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "data"))
from wiki_cache import lookup  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower().replace("’", "'"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s)


def text_of(url: str | None) -> str:
    e = lookup(url) if url else None
    return norm((ROOT / e["file"]).read_text(encoding="utf-8")) if e else ""


def found(term: str, text: str) -> bool:
    t = norm(term)
    if t in text:
        return True
    # pluriels et variantes simples : « Français » ↔ « Françaises », « monts Hombori » ↔ « Hombori »
    stem = t.rstrip("s")
    if len(stem) >= 4 and stem in text:
        return True
    words = [w for w in re.split(r"[\s'/-]+", t) if len(w) >= 4 and w not in {"mont", "monts", "massif", "pic", "pico", "cerro", "nevado", "djebel", "montagne", "piton", "morne", "dollar", "franc", "livre", "standard", "nord", "sud"}]
    return bool(words) and all(w in text for w in words)


countries = json.loads((ROOT / "data" / "countries.json").read_text(encoding="utf-8"))
stats = {k: [0, 0] for k in ("langues", "monnaies", "gentilé", "sommet")}
misses: list[str] = []
for c in countries:
    text = text_of(c.get("wiki_fr")) + " " + " ".join(text_of(k.get("wiki_fr")) for k in c.get("capitals", []))
    if not text.strip():
        continue
    checks = [("langues", l) for l in c.get("languages_fr") or []]
    checks += [("monnaies", m["name_fr"]) for m in c.get("currencies") or [] if m.get("name_fr")]
    if c.get("demonym_fr"):
        checks.append(("gentilé", c["demonym_fr"]))
    if c.get("highest_point"):
        checks.append(("sommet", c["highest_point"]["name_fr"]))
    for kind, term in checks:
        stats[kind][1] += 1
        if found(term, text):
            stats[kind][0] += 1
        else:
            misses.append(f"{c['id']:4} {kind:9} {term}")

for kind, (ok, n) in stats.items():
    print(f"{kind:9} {ok}/{n} retrouvés dans l'article FR")
print(f"\n{len(misses)} entrées non retrouvées (à relire à la main) :")
for m in misses:
    print("  " + m)
