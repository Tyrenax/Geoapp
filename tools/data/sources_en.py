"""Tableaux de Wikipédia EN (wikitexte en cache) utilisés pour recouper la carte d'identité :
- « International vehicle registration code » → codes de plaque en usage ;
- « Left- and right-hand traffic » → sens de circulation.

    python tools/data/sources_en.py        (re)télécharge les deux wikitextes dans cache/sources/
"""
from __future__ import annotations

import re

from common import CACHE, load_json

SRC = {
    "ivrc": ("International vehicle registration code", CACHE / "sources" / "ivrc.wikitext"),
    "lrht": ("Left- and right-hand traffic", CACHE / "sources" / "lrht.wikitext"),
}


def fetch(refresh: bool = False) -> None:
    import wiki_cache as W
    for title, path in SRC.values():
        if path.exists() and not refresh:
            continue
        d = W.api_get("en", {"action": "parse", "page": title, "prop": "wikitext", "redirects": "1"})
        path.write_text(d["parse"]["wikitext"], encoding="utf-8")


ALIAS = {"ROK": "KOR"}  # modèles de drapeau Wikipédia qui ne sont ni ISO ni CIO


def _resolver(countries: list[dict] | None = None):
    from build_web import english_names, key
    countries = countries or load_json(CACHE.parent / "data" / "countries.json")
    ids = {c["id"] for c in countries}
    iso2 = {c["iso2"]: c["id"] for c in countries}
    names = english_names(countries)
    ioc = {m["cioc"]: ("XKX" if m["cca3"] == "UNK" else m["cca3"])
           for m in load_json(CACHE / "sources" / "mledoze_countries.json") if m.get("cioc")}

    def resolve(cell: str) -> str | None:
        """Essaie, dans l'ordre : argument du modèle drapeau, nom du modèle (ISO3, ISO2, CIO), lien [[...]]."""
        cands = []
        m = re.search(r"\{\{\s*flag(?:country|icon|deco)?\s*\|\s*([^|}]+)", cell, flags=re.I)
        if m:
            cands.append(m.group(1))
        m = re.search(r"\{\{\s*([A-Za-z]{2,3})\s*\}\}", cell)
        if m:
            cands.append(m.group(1))
        cands += [l.split("|")[-1] for l in re.findall(r"\[\[(?!File:)([^\]]+)\]\]", cell)]
        for token in cands:
            token = token.strip()
            for found in (token if token in ids else None, iso2.get(token), ioc.get(token), ALIAS.get(token),
                          names.get(key(token))):
                if found in ids:
                    return found
        return None
    return resolve


def _tables(text: str) -> list[str]:
    return re.findall(r"\n\{\|.*?\n\|\}", text, flags=re.S)


def plate_codes(countries: list[dict] | None = None) -> dict[str, list[str]]:
    """Codes en usage (tableau principal « Code | Country | From | Previous | Notes »)."""
    text = SRC["ivrc"][1].read_text(encoding="utf-8")
    resolve = _resolver(countries)
    out: dict[str, list[str]] = {}
    table = next(t for t in _tables(text) if "!Code" in t and "!Previous" in t)
    for row in table.split("\n|-")[1:]:
        cells = [c.strip() for c in row.strip().split("\n|") if c.strip()]
        cells = [c.lstrip("|").strip() for c in cells]
        if len(cells) < 2:
            continue
        code = re.sub(r"<ref.*?(</ref>|/>)|\[\[|\]\]|'''?", "", cells[0]).strip()
        cid = resolve(cells[1])
        if cid and re.fullmatch(r"[A-Z]{1,4}", code):
            out.setdefault(cid, []).append(code)
    return out


def driving_sides(countries: list[dict] | None = None) -> dict[str, str]:
    text = SRC["lrht"][1].read_text(encoding="utf-8")
    resolve = _resolver(countries)
    out: dict[str, str] = {}
    table = next(t for t in _tables(text) if "Road traffic" in t)
    for row in table.split("\n|-")[1:]:
        side = re.search(r"\b(RHT|LHT)\b", row)
        cid = resolve(row.strip().split("\n")[0])
        if cid and side and cid not in out:
            out[cid] = "droite" if side.group(1) == "RHT" else "gauche"
    return out


if __name__ == "__main__":
    fetch()
    p, s = plate_codes(), driving_sides()
    print(f"plaques : {len(p)} entités ; circulation : {len(s)} entités")
