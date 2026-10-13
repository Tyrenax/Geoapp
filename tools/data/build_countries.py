"""Construit data/countries.json depuis cache/wikidata/entities.json + curation.py (+ Wikipédia FR en cache).

    python tools/data/build_countries.py

Garde les champs de l'étape 2 (label, small…) déjà présents dans data/countries.json.
"""
from __future__ import annotations

import re
import sys
import unicodedata
from urllib.parse import unquote

import curation as C
import wiki_cache as W
import identity as ID
import sources_en
from build_geo import apply_stats
from common import CACHE, DATA, iso_rows, load_json, utf8_stdout, write_json

SUBREGION_FR = {
    "Northern Africa": "Afrique du Nord", "Eastern Africa": "Afrique de l'Est", "Middle Africa": "Afrique centrale",
    "Southern Africa": "Afrique australe", "Western Africa": "Afrique de l'Ouest", "Caribbean": "Caraïbes",
    "Central America": "Amérique centrale", "South America": "Amérique du Sud", "Northern America": "Amérique du Nord",
    "Central Asia": "Asie centrale", "Eastern Asia": "Asie de l'Est", "South-eastern Asia": "Asie du Sud-Est",
    "Southern Asia": "Asie du Sud", "Western Asia": "Asie de l'Ouest", "Eastern Europe": "Europe de l'Est",
    "Northern Europe": "Europe du Nord", "Southern Europe": "Europe du Sud", "Western Europe": "Europe de l'Ouest",
    "Australia and New Zealand": "Australie et Nouvelle-Zélande", "Melanesia": "Mélanésie",
    "Micronesia": "Micronésie", "Polynesia": "Polynésie",
}
CONTINENT = {"Africa": "afrique", "Asia": "asie", "Europe": "europe", "Oceania": "oceanie"}


def fold(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower().replace("’", "'"))
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn")


def upper_first(s: str) -> str:
    return s[:1].upper() + s[1:] if s else s


def strip_article(s: str) -> str:
    return re.sub(r"^(la |le |les |l'|l’)", "", s.strip(), flags=re.I).strip()


def ok(st: dict) -> bool:
    return st.get("rank") != "DeprecatedRank" and not st.get("end")


def year(date: str | None) -> int | None:
    return int(date[:4]) if date and date[:4].isdigit() else None


def wiki_url(sitelink: str | None) -> str | None:
    return W.normalize_url(unquote(sitelink)) if sitelink else None


def point(coord: str | None) -> tuple[float, float] | None:
    m = re.match(r"Point\(([-\d.eE]+) ([-\d.eE]+)\)", coord or "")
    return (round(float(m.group(2)), 4), round(float(m.group(1)), 4)) if m else None


# --------------------------------------------------------------------------- choix sur les données brutes


def continent_of(row: dict) -> tuple[str, str]:
    region, sub, inter = row["region"], row["sub-region"], row["intermediate-region"]
    if not region:
        return "antarctique", "Antarctique"
    name = inter if sub in ("Sub-Saharan Africa", "Latin America and the Caribbean") and inter else sub
    if region == "Americas":
        cont = "amerique-sud" if name == "South America" else "amerique-nord"
    else:
        cont = CONTINENT[region]
    return cont, SUBREGION_FR[name]


def pick_population(e: dict) -> tuple[int | None, int | None]:
    cands = [p for p in e["population"] if p["rank"] != "DeprecatedRank"]
    if not cands:
        return None, None
    best = max(cands, key=lambda p: (p["date"] or "", p["rank"] == "PreferredRank"))
    return int(float(best["value"])), year(best["date"])


AREA_PRIORITY = {None: 0, "Q16868672": 1, "Q11081619": 2}  # sans qualificatif > « total » > « terres »


def pick_area(e: dict) -> float | None:
    cands = [a for a in e["area"] if a["rank"] != "DeprecatedRank" and a["applies"] in AREA_PRIORITY]
    if not cands:
        return None
    best = min(cands, key=lambda a: (AREA_PRIORITY[a["applies"]], a["rank"] != "PreferredRank", -float(a["m2"])))
    km2 = float(best["m2"]) / 1e6
    return round(km2) if km2 >= 10 else round(km2, 2)


def pick_flag_article(e: dict) -> str | None:
    items = sorted((f for f in e["flag_items"] if ok(f) and f.get("wfr")), key=lambda f: f["rank"] != "PreferredRank")
    return wiki_url(items[0]["wfr"]) if items else None


def pick_flag_file(e: dict) -> str | None:
    imgs = [f for f in e["flag_images"] if ok(f)]
    imgs.sort(key=lambda f: (f["rank"] != "PreferredRank", -(year(f["start"]) or 0)))
    return unquote(imgs[0]["file"]) if imgs else None


def apply_flag(c: dict, lic: dict) -> None:
    rec = lic.get(c["id"], {})
    c.pop("flag_shared_with", None)
    c.pop("flag_quizzable", None)
    if not rec:
        c["flag"] = None
    c.pop("flag_note_fr", None)
    c["flag_quizzable"] = bool(rec)
    if rec.get("shared_with"):
        c["flag_shared_with"] = rec["shared_with"]
        c["flag_quizzable"] = False
    if c["id"] in C.FLAG_OVERRIDE:
        _, quizzable, note = C.FLAG_OVERRIDE[c["id"]]
        if not quizzable:
            c["flag_quizzable"] = False
        if note:
            c["flag_note_fr"] = note


def wikidata_capitals(e: dict) -> list[dict]:
    """Capitales actuelles distinctes (préférées d'abord)."""
    caps = {}
    for c in e["capitals"]:
        if not ok(c):
            continue
        cur = caps.get(c["cap"])
        if cur is None or (c["rank"] == "PreferredRank" and cur["rank"] != "PreferredRank"):
            caps[c["cap"]] = c
    out = list(caps.values())
    if any(c["rank"] == "PreferredRank" for c in out):
        out = [c for c in out if c["rank"] == "PreferredRank"]
    return out


def resolve_extra_capitals() -> dict[str, dict]:
    path = CACHE / "wikidata" / "extra_capitals.json"
    cached = load_json(path) if path.exists() else {}
    for name, title in C.EXTRA_CAPITALS.items():
        if name in cached:
            continue
        data = W.api_get("fr", {"action": "query", "prop": "pageprops|coordinates", "ppprop": "wikibase_item",
                                "redirects": "1", "titles": title})
        page = data["query"]["pages"][0]
        co = (page.get("coordinates") or [{}])[0]
        cached[name] = {"qid": page["pageprops"]["wikibase_item"], "lat": round(co["lat"], 4),
                        "lon": round(co["lon"], 4), "wiki_fr": W.make_url("fr", page["title"])}
    write_json(path, cached)
    return cached


def capital_record(name: str, role: str | None, c: dict | None, extra: dict) -> dict:
    if c is not None:
        ll = point(c["coord"])
        rec = {"name_fr": name, "role_fr": role, "qid": c["cap"], "lat": ll and ll[0], "lon": ll and ll[1],
               "wiki_fr": wiki_url(c["wfr"])}
    else:
        x = extra[name]
        rec = {"name_fr": name, "role_fr": role, "qid": x["qid"], "lat": x["lat"], "lon": x["lon"], "wiki_fr": x["wiki_fr"]}
    if not rec["wiki_fr"] and name in C.CAPITAL_WIKI_FR:
        rec["wiki_fr"] = W.make_url("fr", C.CAPITAL_WIKI_FR[name])
    rec["aliases_fr"] = [name] + [a for a in C.CAPITAL_ALIASES.get(name, []) if a != name]
    return rec


def build_capitals(cid: str, e: dict, extra: dict, problems: list) -> tuple[list[dict], str | None]:
    if cid in C.NO_CAPITAL:
        return [], None
    wd = wikidata_capitals(e)
    by_name = {c["capfr"]: c for c in e["capitals"] if ok(c)}
    by_name.update({c["capfr"]: c for c in wd})
    if cid in C.CAPITALS:
        caps = []
        for name, role in C.CAPITALS[cid]:
            c = by_name.get(name)
            if c is None and name not in extra:
                problems.append(f"{cid} : capitale « {name} » introuvable (ni P36 ni EXTRA_CAPITALS)")
                continue
            caps.append(capital_record(name, role, c, extra))
        return caps, caps[0]["name_fr"] if caps else None
    if len(wd) != 1:
        problems.append(f"{cid} : {len(wd)} capitales Wikidata, à trancher dans curation.CAPITALS : "
                        + ", ".join(c["capfr"] or c["cap"] for c in wd))
        return [], None
    rec = capital_record(wd[0]["capfr"], wd[0].get("rolefr"), wd[0], extra)
    return [rec], rec["name_fr"]


# --------------------------------------------------------------------------- Wikipédia FR : article et nom officiel

ART_RE = re.compile(r"^(La |Le |Les |L'|L’)?(.*)", re.S)


def article_from_text(name: str, text: str) -> str | None:
    """« La Bolivie, … » → « la » ; « Cuba, … » → «  » ; None si la 1re phrase ne commence pas par le nom."""
    m = ART_RE.match(text.lstrip())
    art, rest = m.group(1), m.group(2)
    first = fold(strip_article(name)).split()[0].split("-")[0]
    if not fold(rest).startswith(first):
        return None
    return {"La ": "la", "Le ": "le", "Les ": "les", "L'": "l'", "L’": "l'", None: ""}[art]


OFFICIAL_RE = re.compile(r"en forme longue\s*[,:]?\s+(?:(?:la|le|les)\s+|l['’])?(.+?)\s*[(,;)]")


def official_from_text(text: str) -> str | None:
    m = OFFICIAL_RE.search(text[:600])
    return upper_first(m.group(1).strip()) if m else None


def official_from_wikidata(e: dict) -> str | None:
    names = [o["name"] for o in e["official_fr"] if ok(o)]
    names = [n for n in names if not n.isupper()]
    if not names:
        return None
    names.sort(key=lambda n: (fold(n) != fold(strip_article(n)), len(n)))
    return upper_first(strip_article(names[0]))


def fr_intros(urls: list[str], offline: bool = False) -> dict[str, str]:
    """Introductions des articles FR (20 par requête, exintro) pour l'article défini et le nom officiel.

    Évite de télécharger le texte complet de 250 articles sous la limite de 10 requêtes/min.
    Cache : cache/wikidata/intros_fr.json.
    """
    path = CACHE / "wikidata" / "intros_fr.json"
    cached = load_json(path) if path.exists() else {}
    todo = [] if offline else [u for u in urls if u not in cached and not W.cached_path(u)]
    for i in range(0, len(todo), 20):
        chunk = todo[i:i + 20]
        titles = [W.split_url(u)[1].replace("_", " ") for u in chunk]
        data = W.api_get("fr", {"action": "query", "prop": "extracts", "exintro": "1", "explaintext": "1",
                                "exlimit": "20", "redirects": "1", "titles": "|".join(titles)})
        for p in data["query"]["pages"]:
            if p.get("extract"):
                cached[W.make_url("fr", p["title"])] = p["extract"]
        write_json(path, cached)
    return cached


# --------------------------------------------------------------------------- assemblage


def add_identity(out: list[dict], ents: dict, intros: dict) -> None:
    """Carte d'identité (identity.py) ajoutée à chaque entité, avant les champs de l'étape 2."""
    un_plates = sources_en.plate_codes(out)
    ml = {("XKX" if m["cca3"] == "UNK" else m["cca3"]): m
          for m in load_json(CACHE / "sources" / "mledoze_countries.json")}
    tlds = {cid: ID.tlds(e) for cid, e in ents.items()}
    mottos = {cid: (C.IDENTITY_OVERRIDE.get(cid, {}).get("motto_fr") or (ID.motto(e),))[0] for cid, e in ents.items()}
    for c in out:
        cid = c["id"]
        text = W.read_text(c["wiki_fr"]) or intros.get(c["wiki_fr"])
        ident = ID.identity(cid, ents[cid], un_plates=un_plates, ml=ml.get(cid), fr_text=text,
                            sovereign=c["sovereign"], sovereign_tlds=tlds.get(c["sovereign"], []),
                            sovereign_motto=mottos.get(c["sovereign"]))
        for cur in ident["currencies"] or []:
            cur["name_fr"] = cur["name_fr"] or ID.CURRENCY_NAME_FR.get(cur["code"])
        pos = list(c).index("label")
        items = list(c.items())
        c.clear()
        c.update(dict(items[:pos] + list(ident.items()) + items[pos:]))


def build(offline: bool = False) -> tuple[list[dict], list[str], list[str]]:
    ents = load_json(CACHE / "wikidata" / "entities.json")
    rows = {r["alpha-3"]: r for r in iso_rows()}
    extra = resolve_extra_capitals()

    intros = fr_intros([wiki_url(e["wiki_fr"]) for e in ents.values()], offline)

    flag_lic = load_json(DATA / "flags" / "LICENSES.json") if (DATA / "flags" / "LICENSES.json").exists() else {}
    geo_stats = load_json(CACHE / "geo" / "stats.json") if (CACHE / "geo" / "stats.json").exists() else {}
    problems, notes, out = [], [], []
    for cid, e in ents.items():
        row = rows[cid]
        kind = "etat" if (e["un_member"] or cid in C.EXTRA_ETATS) else "territoire"
        if kind == "territoire" and cid not in C.TERRITORIES:
            problems.append(f"{cid} : territoire sans statut dans curation.TERRITORIES")
        if kind == "etat" and cid in C.TERRITORIES:
            problems.append(f"{cid} : marqué État (ONU) mais présent dans TERRITORIES")
        sovereign, status = C.TERRITORIES.get(cid, (None, None)) if kind == "territoire" else (None, None)

        name = C.NAME_FR.get(cid) or upper_first(e["label_fr"])
        wiki_fr = wiki_url(e["wiki_fr"])
        text = W.read_text(wiki_fr) or intros.get(wiki_fr, "")
        article = C.ARTICLE_FR.get(cid)
        if article is None:
            article = article_from_text(name, text) if text else None
            if article is None and not text:
                problems.append(f"{cid} : article défini à compléter (introduction Wikipédia pas encore lue)")
                article = ""
            elif article is None:
                problems.append(f"{cid} : article défini indéterminé (1re phrase : {text[:60]!r})")
                article = ""
        official = official_from_text(text) or official_from_wikidata(e)
        variants = []
        if official:
            official = re.sub(r"\s+", " ", official.replace("’", "'"))
            official, *variants = [upper_first(strip_article(v)) for v in official.split(" ou ")]
        if cid in C.OFFICIAL_FR:
            official = C.OFFICIAL_FR[cid]
        if official and fold(official) == fold(name):
            official = None

        aliases = [name]
        for a in [strip_article(official or "")] + variants + C.ALIASES_FR.get(cid, []):
            if a and fold(a) not in {fold(x) for x in aliases}:
                aliases.append(a)

        capitals, quiz_capital = build_capitals(cid, e, extra, problems)
        pop, pop_year = pick_population(e)
        cont, subregion = continent_of(row)
        if cid in C.CONTINENT_OVERRIDE:
            cont, _, sub = C.CONTINENT_OVERRIDE[cid]
            subregion = sub or subregion
        neighbors = sorted({b["id"] for b in e["borders"] if ok(b) and b["id"] != cid})

        out.append({
            "id": cid,
            "iso2": row["alpha-2"],
            "qid": e["qid"],
            "kind": kind,
            "sovereign": sovereign,
            "status_fr": status,
            "name_fr": name,
            "name_official_fr": official,
            "article_fr": article,
            "aliases_fr": aliases,
            "continent": cont,
            "subregion_fr": subregion,
            "capitals": capitals,
            "quiz_capital": quiz_capital,
            "capital_note_fr": C.NO_CAPITAL.get(cid) or C.CAPITAL_NOTE.get(cid),
            "population": pop,
            "population_year": pop_year,
            "area_km2": C.AREA_OVERRIDE[cid][0] if cid in C.AREA_OVERRIDE else pick_area(e),
            "label": None,
            "small": None,
            "neighbors": neighbors,
            "wiki_fr": wiki_fr,
            "wiki_en": wiki_url(e["wiki_en"]),
            "flag": f"flags/{cid}.svg",
            "flag_wiki_fr": pick_flag_article(e),
            "quizzable": cid not in C.NOT_QUIZZABLE,
        })
        apply_stats(out[-1], geo_stats)
        if flag_lic:
            apply_flag(out[-1], flag_lic)
        if e["iso2_wd"] and e["iso2_wd"] != row["alpha-2"]:
            notes.append(f"{cid} : ISO2 Wikidata {e['iso2_wd']} ≠ liste ISO {row['alpha-2']}")

    by_id = {c["id"]: c for c in out}
    add_identity(out, ents, intros)
    for a, b in C.NEIGHBORS_ADD:
        for x, y in ((a, b), (b, a)):
            by_id[x]["neighbors"] = sorted(set(by_id[x]["neighbors"]) | {y})

    # alias partagés entre deux entités → ambigus, on les retire (sauf le nom usuel)
    owners = {}
    for c in out:
        for a in c["aliases_fr"]:
            owners.setdefault(fold(a), set()).add(c["id"])
    for c in out:
        keep = [a for a in c["aliases_fr"] if a == c["name_fr"] or len(owners[fold(a)]) == 1]
        for a in set(c["aliases_fr"]) - set(keep):
            notes.append(f"{c['id']} : alias « {a} » retiré (partagé avec {sorted(owners[fold(a)] - {c['id']})})")
        c["aliases_fr"] = keep
    return out, problems, notes


def main():
    utf8_stdout()
    out, problems, notes = build(offline="--offline" in sys.argv)
    write_json(DATA / "countries.json", out)
    n_etat = sum(c["kind"] == "etat" for c in out)
    print(f"{len(out)} entités ({n_etat} États, {len(out) - n_etat} territoires) → data/countries.json")
    print(f"capitales : {sum(len(c['capitals']) for c in out)} ; entités à plusieurs capitales : "
          f"{sum(len(c['capitals']) > 1 for c in out)} ; sans capitale : {sum(not c['capitals'] for c in out)}")
    for n in notes:
        print("note :", n)
    for p in problems:
        print("PROBLÈME :", p)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
