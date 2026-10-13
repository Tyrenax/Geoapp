"""Juge des faits de Geo Atlas.

Vérifie data/facts/<ID>.json contre le contrat (docs/ARCHITECTURE.md) :
- schéma et nombre minimal de faits ;
- chaque citation (`quote`) figure mot pour mot dans le texte Wikipédia en cache ;
- chaque nombre d'au moins 2 chiffres (hors ordinaux) écrit dans title/short/long figure dans une citation du même fait.

Usage : python tools/facts/verify_facts.py [ID ...] [--quiet]
Code de sortie 1 s'il y a au moins une erreur.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
FACTS_DIR = ROOT / "data" / "facts"
INDEX = ROOT / "cache" / "wiki" / "index.json"
COUNTRIES = ROOT / "data" / "countries.json"

TOPICS = {"histoire", "geographie", "culture", "politique", "economie", "drapeau"}
MIN_FACTS = 4
MIN_HISTORY = 3
MIN_QUOTE = 30
MAX_QUOTE = 1200
MAX_SHORT = 340

SPACES = re.compile(r"[\s    ​﻿]+")
APOS = str.maketrans({"’": "'", "‘": "'", "ʼ": "'", "´": "'",
                      "“": '"', "”": '"', "«": '"', "»": '"',
                      "–": "-", "—": "-", "‑": "-", "‐": "-"})
NUMBER = re.compile(r"\d{1,3}(?:[    .,]\d{3})+(?![\d])|\d+")


def norm_text(s: str) -> str:
    s = unicodedata.normalize("NFC", s).translate(APOS)
    return SPACES.sub(" ", s).strip()


def norm_url(url: str) -> str:
    parts = urlsplit(url.strip())
    host = parts.netloc.lower().replace("m.wikipedia.org", "wikipedia.org")
    path = unicodedata.normalize("NFC", unquote(parts.path)).replace(" ", "_")
    if path.startswith("/wiki/") and len(path) > 6:
        path = "/wiki/" + path[6].upper() + path[7:]
    return f"https://{host}{path}"


ORDINAL = re.compile(r"\s?(?:e|er|re|ère|ème|eme|nd|nde)(?![\w])")


def numbers(s: str, min_digits: int = 2) -> set[str]:
    """Nombres d'au moins `min_digits` chiffres, hors ordinaux (« 20e siècle », « 1er »)."""
    out = set()
    for m in NUMBER.finditer(s):
        if min_digits > 0 and ORDINAL.match(s, m.end()):
            continue
        digits = re.sub(r"\D", "", m.group())
        if len(digits) >= min_digits:
            out.add(digits)
    return out


class Cache:
    def __init__(self) -> None:
        self.index: dict[str, dict] = {}
        if INDEX.exists():
            raw = json.loads(INDEX.read_text(encoding="utf-8"))
            self.index = {norm_url(k): v for k, v in raw.items()}
        self._texts: dict[str, str | None] = {}

    def text(self, url: str) -> str | None:
        key = norm_url(url)
        if key not in self._texts:
            entry = self.index.get(key)
            path = ROOT / entry["file"] if entry else None
            self._texts[key] = (norm_text(path.read_text(encoding="utf-8"))
                                if path and path.exists() else None)
        return self._texts[key]


def check_fact(fact: dict, where: str, cache: Cache, errors: list[str], warns: list[str]) -> None:
    for field in ("id", "topic", "title", "short", "sources"):
        if not fact.get(field):
            errors.append(f"{where}: champ « {field} » manquant ou vide")
    if fact.get("topic") and fact["topic"] not in TOPICS:
        errors.append(f"{where}: topic « {fact['topic']} » inconnu ({', '.join(sorted(TOPICS))})")
    if len(fact.get("short", "")) > MAX_SHORT:
        warns.append(f"{where}: « short » fait {len(fact['short'])} caractères (> {MAX_SHORT})")

    quotes: list[str] = []
    for i, src in enumerate(fact.get("sources") or []):
        sw = f"{where}.sources[{i}]"
        url, quote = src.get("url", ""), src.get("quote", "")
        if "wikipedia.org/wiki/" not in url:
            errors.append(f"{sw}: URL hors Wikipédia : {url}")
            continue
        text = cache.text(url)
        if text is None:
            errors.append(f"{sw}: article absent du cache : {url}")
            continue
        q = norm_text(quote)
        if len(q) < MIN_QUOTE:
            errors.append(f"{sw}: citation trop courte ({len(q)} car., minimum {MIN_QUOTE})")
        elif len(q) > MAX_QUOTE:
            errors.append(f"{sw}: citation trop longue ({len(q)} car., maximum {MAX_QUOTE})")
        if q and q not in text:
            errors.append(f"{sw}: citation introuvable mot pour mot dans {url} : « {q[:90]}… »")
        else:
            quotes.append(q)

    quoted = set().union(*(numbers(q, 0) for q in quotes)) if quotes else set()
    written = " ".join(fact.get(f, "") for f in ("title", "short", "long"))
    for n in sorted(numbers(written) - quoted):
        errors.append(f"{where}: le nombre {n} n'apparaît dans aucune citation de ce fait")


def check_file(path: Path, cache: Cache, known: dict[str, dict]) -> tuple[list[str], list[str], int]:
    errors: list[str] = []
    warns: list[str] = []
    eid = path.stem
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"{eid}: JSON invalide ({e})"], [], 0

    if data.get("id") != eid:
        errors.append(f"{eid}: « id » vaut {data.get('id')!r}, attendu {eid!r}")
    if known and eid not in known:
        errors.append(f"{eid}: entité absente de data/countries.json")
    thin = bool(data.get("thin"))
    sink = warns if thin else errors

    facts = data.get("facts") or []
    if len(facts) < MIN_FACTS:
        sink.append(f"{eid}: {len(facts)} faits, minimum {MIN_FACTS}")
    hist = sum(1 for f in facts if f.get("topic") == "histoire")
    if hist < MIN_HISTORY:
        sink.append(f"{eid}: {hist} faits historiques, minimum {MIN_HISTORY}")

    entity = known.get(eid, {})
    has_capital = bool(entity.get("capitals")) if known else True
    cfacts = data.get("capital_facts") or []
    if has_capital and not cfacts:
        sink.append(f"{eid}: aucun fait sur la capitale")

    ids: set[str] = set()
    for group, items in (("facts", facts), ("capital_facts", cfacts)):
        for i, fact in enumerate(items):
            fid = fact.get("id", "")
            if fid in ids:
                errors.append(f"{eid}.{group}[{i}]: id {fid!r} en double")
            ids.add(fid)
            if fid and not fid.startswith(eid + "-"):
                errors.append(f"{eid}.{group}[{i}]: id {fid!r} doit commencer par « {eid}- »")
            check_fact(fact, f"{eid}.{group}[{i}]", cache, errors, warns)

    tips = data.get("tips") or {}
    for key in ("position", "flag", "capital"):
        if not (tips.get(key) or "").strip():
            optional = (key == "flag" and entity.get("flag_quizzable") is False) or \
                       (key == "capital" and not has_capital)
            (warns if optional else errors).append(f"{eid}: astuce « {key} » manquante")

    return errors, warns, len(facts) + len(cfacts)


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    quiet = "--quiet" in argv
    ids = [a.upper() for a in argv if not a.startswith("--")]
    cache = Cache()
    if not cache.index:
        print(f"ATTENTION : index du cache introuvable ou vide ({INDEX.relative_to(ROOT)})")
    known: dict[str, dict] = {}
    if COUNTRIES.exists():
        known = {c["id"]: c for c in json.loads(COUNTRIES.read_text(encoding="utf-8"))}

    paths = [FACTS_DIR / f"{i}.json" for i in ids] if ids else sorted(FACTS_DIR.glob("*.json"))
    total_err = total_warn = total_facts = 0
    for path in paths:
        if not path.exists():
            print(f"{path.stem}: fichier absent ({path.relative_to(ROOT)})")
            total_err += 1
            continue
        errors, warns, n = check_file(path, cache, known)
        total_err += len(errors)
        total_warn += len(warns)
        total_facts += n
        for e in errors:
            print("ERREUR ", e)
        if not quiet:
            for w in warns:
                print("avert. ", w)

    print(f"\n{len(paths)} fichiers, {total_facts} faits, {total_err} erreurs, {total_warn} avertissements")
    if known and not ids:
        missing = sorted(i for i, c in known.items()
                         if c.get("quizzable", True) and not (FACTS_DIR / f"{i}.json").exists())
        print(f"Entités sans fichier de faits : {len(missing)}"
              + (f" ({', '.join(missing[:15])}{'…' if len(missing) > 15 else ''})" if missing else ""))
    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
