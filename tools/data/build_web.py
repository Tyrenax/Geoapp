"""Génère web/public/data/ (données servies au jeu). Idempotent : le dossier est entièrement régénéré.

    python tools/data/build_web.py

  countries.json      copie allégée de data/countries.json (sans les QID Wikidata, JSON compact)
  world.topo.json     copie de data/geo/world.topo.json
  flags/<ID>.svg      copie de data/flags/
  facts/<ID>.json     copie de data/facts/*.json (0 ou N fichiers) + facts/index.json (liste triée des id)
  flag_similar.json   {ID: [ids des drapeaux sosies]}, depuis anki-geo/ultimate-geography flag_similarity.csv
"""
from __future__ import annotations

import csv
import re
import shutil
import sys
import unicodedata

from common import CACHE, DATA, ROOT, download, load_json, utf8_stdout, write_json

WEB = ROOT / "web" / "public" / "data"
ANKI_SIM = "https://raw.githubusercontent.com/anki-geo/ultimate-geography/master/src/data/flag_similarity.csv"
MLEDOZE = "https://raw.githubusercontent.com/mledoze/countries/master/countries.json"

# Noms anglais d'anki-geo absents de mledoze/Wikidata.
ANKI_NAME_FIX = {"Ivory Coast": "CIV", "East Timor": "TLS", "Vatican City": "VAT", "Kosovo": "XKX",
                 "Micronesia": "FSM", "Cape Verde": "CPV", "Swaziland": "SWZ", "Burma": "MMR",
                 "Republic of the Congo": "COG", "Democratic Republic of the Congo": "COD",
                 "Palestine": "PSE", "Macedonia": "MKD", "North Macedonia": "MKD", "Czech Republic": "CZE"}


def key(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", s.replace("&", "and")).strip()


def english_names(countries: list[dict]) -> dict[str, str]:
    """Nom anglais normalisé → id (mledoze : common, official, altSpellings ; + titres Wikipédia EN)."""
    names = {}
    for c in load_json(download(MLEDOZE, CACHE / "sources" / "mledoze_countries.json")):
        cid = "XKX" if c["cca3"] == "UNK" else c["cca3"]
        for n in [c["name"]["common"], c["name"]["official"], *c.get("altSpellings", [])]:
            names.setdefault(key(n), cid)
    for c in countries:
        if c.get("wiki_en"):
            names.setdefault(key(c["wiki_en"].rsplit("/", 1)[1].replace("_", " ")), c["id"])
    for n, cid in ANKI_NAME_FIX.items():
        names[key(n)] = cid
    return names


def split_top(s: str) -> list[str]:
    """Découpe sur les virgules hors parenthèses."""
    out, depth, cur = [], 0, ""
    for ch in s:
        depth += ch == "("
        depth -= ch == ")"
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    return [x.strip() for x in out + [cur] if x.strip()]


def flag_similar(countries: list[dict], problems: list[str]) -> dict[str, list[str]]:
    ids = {c["id"] for c in countries}
    names = english_names(countries)
    path = download(ANKI_SIM, CACHE / "sources" / "anki_flag_similarity.csv")
    groups: dict[str, set[str]] = {}
    for row in csv.DictReader(path.open(encoding="utf-8")):
        a = names.get(key(row["country"]))
        if a not in ids:
            problems.append(f"flag_similar : pays anki non rattaché « {row['country']} »")
            continue
        for item in split_top(row["flag similarity"]):
            nm = re.sub(r"\s*\(.*\)\s*$", "", item).strip()
            b = names.get(key(nm))
            if b not in ids:
                problems.append(f"flag_similar : sosie anki non rattaché « {nm} » (pour {a})")
                continue
            if a != b:
                groups.setdefault(a, set()).add(b)
                groups.setdefault(b, set()).add(a)
    return {k: sorted(v) for k, v in sorted(groups.items())}


def light(c: dict) -> dict:
    c = {k: v for k, v in c.items() if k != "qid"}
    c["capitals"] = [{k: v for k, v in cap.items() if k != "qid"} for cap in c["capitals"]]
    return c


def main():
    utf8_stdout()
    problems = []
    countries = load_json(DATA / "countries.json")
    if WEB.exists():
        shutil.rmtree(WEB)
    (WEB / "flags").mkdir(parents=True)
    (WEB / "facts").mkdir(parents=True)

    write_json(WEB / "countries.json", [light(c) for c in countries], indent=None)
    shutil.copyfile(DATA / "geo" / "world.topo.json", WEB / "world.topo.json")

    n_flags = 0
    for c in countries:
        src = DATA / "flags" / f"{c['id']}.svg"
        if src.exists():
            shutil.copyfile(src, WEB / "flags" / src.name)
            n_flags += 1
        elif c.get("flag"):
            problems.append(f"{c['id']} : drapeau {src.name} absent")

    fact_ids = []
    for src in sorted((DATA / "facts").glob("*.json")):
        shutil.copyfile(src, WEB / "facts" / src.name)
        fact_ids.append(src.stem)
    write_json(WEB / "facts" / "index.json", fact_ids, indent=None)

    sim = flag_similar(countries, problems)
    write_json(WEB / "flag_similar.json", sim, indent=None)

    size = sum(p.stat().st_size for p in WEB.rglob("*") if p.is_file())
    print(f"web/public/data : {len(countries)} entités, {n_flags} drapeaux, {len(fact_ids)} fichiers de faits, "
          f"{len(sim)} entités avec sosies de drapeau, world.topo.json "
          f"{(WEB / 'world.topo.json').stat().st_size / 1e6:.2f} Mo, total {size / 1e6:.2f} Mo")
    for p in problems:
        print("PROBLÈME :", p)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
