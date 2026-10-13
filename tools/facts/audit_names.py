"""Audit des noms propres : signale les mots à majuscule du texte d'un fait absents de ses citations.

Complète verify_facts.py (qui contrôle les citations et les nombres). Un nom propre écrit dans
title/short/long mais absent de toutes les citations du fait est souvent un détail ajouté de mémoire.
Ce n'est pas toujours une erreur (traduction, nom du pays lui-même) : c'est une liste à relire.

Usage : python tools/facts/audit_names.py [ID ...]
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FACTS = ROOT / "data" / "facts"
COUNTRIES = ROOT / "data" / "countries.json"

WORD = re.compile(r"[A-ZÀ-ÖØ-Þ][\w'’\-]{3,}")
# Mots à majuscule courants qui ne sont pas des détails factuels.
COMMON = {"Avant", "Après", "Depuis", "Pendant", "Comme", "Quand", "Selon", "Sous", "Dans", "Pour",
          "Mais", "Plus", "Elle", "Elles", "Ils", "Ses", "Son", "Sur", "Leur", "Leurs", "Cette", "Celui",
          "Celle", "Même", "Aujourd'hui", "Aujourd’hui", "Chaque", "Entre", "Deux", "Trois", "Quatre",
          "Cinq", "Seule", "Seul", "Tout", "Toute", "Tous", "Toutes", "Ensuite", "Puis", "Enfin", "Hormis",
          "Autrefois", "Longtemps", "Encore", "Ainsi", "Lors", "Vers", "Dès", "Face", "Faute", "Rouge",
          "Bleu", "Vert", "Jaune", "Blanc", "Noir", "Juste", "Piège", "Facile", "Ancien", "Ancienne",
          "Premier", "Première", "Dernier", "Dernière", "Grand", "Grande", "Petit", "Petite", "Nord", "Sud",
          "Est", "Ouest", "République", "Royaume", "Empire", "Histoire"}


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.replace("’", "'"))
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def stems(word: str) -> list[str]:
    w = fold(word).strip("'-")
    out = {w}
    for suf in ("iennes", "iens", "ienne", "ien", "aises", "ais", "aise", "ois", "oise", "es", "s", "e"):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            out.add(w[: -len(suf)])
    return sorted(out, key=len)


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    names: dict[str, set[str]] = {}
    if COUNTRIES.exists():
        for c in json.loads(COUNTRIES.read_text(encoding="utf-8")):
            parts = [c.get("name_fr", "")] + [k.get("name_fr", "") for k in c.get("capitals", [])]
            names[c["id"]] = {fold(p) for p in " ".join(parts).replace("-", " ").split() if len(p) > 3}
    ids = [a.upper() for a in argv] or sorted(p.stem for p in FACTS.glob("*.json"))
    total = 0
    for eid in ids:
        doc = json.loads((FACTS / f"{eid}.json").read_text(encoding="utf-8"))
        own = names.get(eid, set())
        for fact in doc.get("facts", []) + doc.get("capital_facts", []):
            text = " ".join(fact.get(k, "") for k in ("title", "short", "long"))
            quotes = fold(" ".join(s.get("quote", "") for s in fact.get("sources", [])))
            missing = []
            for m in WORD.finditer(text):
                w = re.sub(r"^[LDdl]['’]", "", m.group())
                before = text[:m.start()].rstrip()
                if not before or before[-1] in ".:!?«(—\"" or re.fullmatch(r"[IVXL]+(e|er|ème)?", w):
                    continue  # début de phrase ou siècle en chiffres romains
                if len(w) < 4 or w in COMMON or fold(w) in own:
                    continue
                if not any(st in quotes for st in stems(w)):
                    missing.append(w)
            if missing:
                total += 1
                print(f"{fact['id']:<8} {', '.join(dict.fromkeys(missing))}   — {fact.get('title', '')}")
    print(f"\n{total} faits à relire")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
