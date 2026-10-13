"""Contrôle de data/countries.json par des sources indépendantes → data/DATA_REPORT.md.

    python tools/data/check_data.py

Recoupements : capitales (anki-geo/ultimate-geography `capital:fr`, mledoze/countries `capital`), continent
(mledoze `region`/`subregion`), voisins (Wikidata P47 et mledoze `borders` contre la géométrie Natural Earth),
superficie (mledoze `area`, écart > 10 %). Contrôle géométrique : chaque capitale dans son polygone
(ou à moins de 25 km). Complétude : nom, capitale (sauf cas documentés), drapeau, géométrie ou label.

Chaque désaccord doit avoir une décision : règle générale (écrite ici) ou entrée de curation.DECISIONS.
Code de sortie 1 s'il reste un désaccord non tranché ou une entité incomplète.
"""
from __future__ import annotations

import csv
import re
import datetime as dt
import sys

from pyproj import Geod
from shapely.geometry import Point, shape
from shapely.ops import nearest_points

import curation as C
import wiki_cache as W
from build_countries import fold
from build_web import english_names, key
from common import CACHE, DATA, download, load_json, sparql, utf8_stdout
from fetch_flags import svg_ratio

ANKI_CAP = "https://raw.githubusercontent.com/anki-geo/ultimate-geography/master/src/data/capital.csv"
MLEDOZE = "https://raw.githubusercontent.com/mledoze/countries/master/countries.json"
GEOD = Geod(ellps="WGS84")
MAX_CAPITAL_KM = 25
AREA_TOLERANCE = 0.10

MLEDOZE_REGION = {"afrique": "Africa", "asie": "Asia", "europe": "Europe", "oceanie": "Oceania",
                  "amerique-nord": "Americas", "amerique-sud": "Americas", "antarctique": "Antarctic"}


class Report:
    def __init__(self):
        self.sections: dict[str, list[tuple[str, str, str | None]]] = {}
        self.open = 0

    def add(self, section: str, cid: str, what: str, decision: str | None):
        """decision None → cherchée dans curation.DECISIONS[(section, cid)] ; absente = non tranché."""
        decision = decision or C.DECISIONS.get((section, cid))
        if decision is None:
            self.open += 1
        self.sections.setdefault(section, []).append((cid, what, decision))


def capital_names(c: dict) -> set[str]:
    return {fold(a) for cap in c["capitals"] for a in cap["aliases_fr"] + [cap["name_fr"]]}


def capital_en_labels(countries: list[dict]) -> dict[str, set[str]]:
    qids = sorted({cap["qid"] for c in countries for cap in c["capitals"] if cap.get("qid")})
    rows = sparql("SELECT ?c ?l WHERE { VALUES ?c { " + " ".join("wd:" + q for q in qids) + " } "
                  "?c rdfs:label|skos:altLabel ?l FILTER(lang(?l)=\"en\") }", "capitals_en")
    out: dict[str, set[str]] = {}
    for r in rows:
        out.setdefault(r["c"], set()).add(key(r["l"]))
    return out


def km_between(lat1, lon1, lat2, lon2) -> float:
    return GEOD.inv(lon1, lat1, lon2, lat2)[2] / 1000


def main():
    utf8_stdout()
    countries = load_json(DATA / "countries.json")
    by_id = {c["id"]: c for c in countries}
    ents = load_json(CACHE / "wikidata" / "entities.json")
    names = english_names(countries)
    mled = {("XKX" if m["cca3"] == "UNK" else m["cca3"]): m
            for m in load_json(download(MLEDOZE, CACHE / "sources" / "mledoze_countries.json"))}
    rep = Report()

    # ---- capitales : anki-geo (français)
    anki_seen = set()
    for row in csv.DictReader(download(ANKI_CAP, CACHE / "sources" / "anki_capital.csv").open(encoding="utf-8")):
        cid = names.get(key(row["country"]))
        if cid not in by_id:
            continue  # Angleterre, Écosse… : hors périmètre
        anki_seen.add(cid)
        c = by_id[cid]
        theirs = [x.strip() for x in row["capital:fr"].split(",") if x.strip()]
        ours = capital_names(c)
        missing = [t for t in theirs if fold(t) not in ours]
        if missing:
            rep.add("capitale", cid, f"anki-geo : « {row['capital:fr']} » ; nous : "
                    f"« {', '.join(cap['name_fr'] for cap in c['capitals']) or '—'} » (quiz : {c['quiz_capital']})", None)

    # ---- capitales : mledoze (anglais, comparé aux libellés anglais Wikidata de nos capitales)
    en = capital_en_labels(countries)
    for cid, c in by_id.items():
        m = mled.get(cid)
        if not m:
            rep.add("couverture", cid, "absent de mledoze/countries", "rien à recouper ici ; les autres contrôles s'appliquent")
            continue
        theirs = [x for x in m.get("capital", []) if x]
        ours_en = set().union(*(en.get(cap["qid"], set()) for cap in c["capitals"])) if c["capitals"] else set()
        missing = [t for t in theirs if key(t) not in ours_en]
        if missing or (not theirs and c["capitals"]) or (theirs and not c["capitals"]):
            rep.add("capitale-en", cid, f"mledoze : « {', '.join(theirs) or '—'} » ; nous : "
                    f"« {', '.join(cap['name_fr'] for cap in c['capitals']) or '—'} »", None)

    # ---- continent
    for cid, c in by_id.items():
        m = mled.get(cid)
        if not m:
            continue
        want = MLEDOZE_REGION[c["continent"]]
        ok = m["region"] == want and (c["continent"] != "amerique-sud" or m["subregion"] == "South America") \
            and not (c["continent"] == "amerique-nord" and m["subregion"] == "South America")
        if not ok:
            rep.add("continent", cid, f"mledoze : {m['region']} / {m['subregion']} ; nous : {c['continent']} "
                    f"({c['subregion_fr']})",
                    C.CONTINENT_OVERRIDE.get(cid, (None, None))[1])

    # ---- voisins : géométrie (décision) contre Wikidata P47 et mledoze
    for cid, c in by_id.items():
        geo = set(c["neighbors"])
        p47 = {b["id"] for b in ents[cid]["borders"] if b["rank"] != "DeprecatedRank" and not b.get("end")} - {cid}
        mb = {("XKX" if b == "UNK" else b) for b in mled.get(cid, {}).get("borders", [])}
        for label, other in (("Wikidata P47", p47), ("mledoze", mb)):
            extra, lacking = sorted(other - geo), sorted(geo - other)
            if not extra and not lacking:
                continue
            parts = []
            if extra:
                parts.append(f"{label} ajoute {', '.join(extra)}")
            if lacking:
                parts.append(f"{label} n'a pas {', '.join(lacking)}")
            rep.add("voisins", cid, " ; ".join(parts),
                    C.DECISIONS.get(("voisins", cid)) or
                    "règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; "
                    "les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas")

    # ---- superficie
    for cid, c in by_id.items():
        m = mled.get(cid)
        if not m or not m.get("area") or m["area"] <= 0 or not c.get("area_km2"):
            if not c.get("area_km2"):
                rep.add("superficie", cid, "pas de superficie Wikidata", None)
            continue
        diff = abs(c["area_km2"] - m["area"]) / max(m["area"], 1e-9)
        if diff > AREA_TOLERANCE:
            src = "nous (corrigé)" if cid in C.AREA_OVERRIDE else "Wikidata"
            rep.add("superficie", cid, f"{src} {c['area_km2']:,} km² ; mledoze {m['area']:,} km² (écart {diff:.0%})".replace(",", " "),
                    C.AREA_OVERRIDE.get(cid, (None, None))[1])

    # ---- capitales dans leur polygone
    geoms = {f["properties"]["id"]: shape(f["geometry"])
             for f in load_json(CACHE / "geo" / "countries.geojson")["features"]}
    for cid, c in by_id.items():
        g = geoms.get(cid)
        for cap in c["capitals"]:
            if cap.get("lat") is None:
                rep.add("géométrie", cid, f"{cap['name_fr']} sans coordonnées", None)
                continue
            if g is None:
                continue
            pt = Point(cap["lon"], cap["lat"])
            if g.contains(pt):
                continue
            q = nearest_points(g, pt)[0]  # point du polygone le plus proche, puis distance géodésique
            km = km_between(cap["lat"], cap["lon"], q.y, q.x)
            if km > MAX_CAPITAL_KM:
                rep.add("géométrie", cid, f"{cap['name_fr']} à {km:.0f} km du polygone", None)

    identity_checks(rep, countries, ents, mled)

    # ---- complétude
    incomplete = 0
    for cid, c in by_id.items():
        miss = []
        if not c.get("name_fr"):
            miss.append("nom")
        if not c["capitals"] and cid not in C.NO_CAPITAL:
            miss.append("capitale")
        svg = DATA / "flags" / f"{cid}.svg"
        if not svg.exists():
            miss.append("drapeau")
        else:
            try:
                svg_ratio(svg.read_bytes())
            except Exception as e:  # SVG illisible
                miss.append(f"drapeau invalide ({e})")
        if cid not in geoms and not c.get("label"):
            miss.append("géométrie ou label")
        if miss:
            incomplete += 1
            rep.add("complétude", cid, "manque : " + ", ".join(miss), None)
    cached_fr = sum(1 for c in countries if c.get("wiki_fr") and W.cached_path(c["wiki_fr"]))

    write_report(rep, countries, cached_fr)
    print(f"désaccords : {sum(len(v) for v in rep.sections.values())} ; non tranchés : {rep.open} ; "
          f"articles FR des pays en cache : {cached_fr}/{len(countries)} → data/DATA_REPORT.md")
    sys.exit(1 if rep.open else 0)


def identity_checks(rep: "Report", countries: list[dict], ents: dict, mled: dict) -> None:
    """Carte d'identité : chaque écart avec la seconde source est listé avec la règle ou la correction qui le tranche."""
    import identity as ID
    import sources_en
    sides = sources_en.driving_sides(countries)
    ov = lambda cid, f: C.IDENTITY_OVERRIDE.get(cid, {}).get(f, (None, None))[1]
    fk = lambda s: re.sub(r"[\s\-]", "", ID.fold(s or ""))
    for c in countries:
        cid, e, m = c["id"], ents[c["id"]], mled.get(c["id"], {})
        # plaque
        wd = ID.wikidata_plates(e)
        if set(wd) != set(c["plate_code"] or []) or ("plaque", cid) in C.DECISIONS:
            if c["plate_code"]:
                why = "règle : code enregistré à l'ONU (Convention de Vienne), tableau Wikipédia EN"
            else:
                why = "règle : aucun code enregistré à l'ONU pour cette entité (tableau Wikipédia EN) → null"
            rep.add("plaque", cid, f"ONU : {c['plate_code'] or '—'} ; Wikidata : {wd or '—'}", ov(cid, "plate_code") or C.DECISIONS.get(("plaque", cid)) or why)
        # circulation
        en = sides.get(cid)
        if en != c["driving_side"]:
            why = ov(cid, "driving_side") or ("absent du tableau EN : Wikidata conservé" if en is None else None)
            rep.add("circulation", cid, f"Wikidata : {c['driving_side'] or '—'} ; EN : {en or '—'}", why)
        # monnaies
        ours = sorted(x["code"] for x in c["currencies"] or [])
        theirs = sorted((m.get("currencies") or {}).keys())
        if m and ours != theirs:
            why = ov(cid, "currencies")
            if not why and set(ours) < set(theirs):
                why = "règle : monnaie officielle seulement (Wikidata) ; les monnaies qui circulent en parallèle ne sont pas retenues"
            if not why and set(ours) > set(theirs):
                why = "Wikidata conservé (source principale) : monnaie absente de mledoze"
            rep.add("monnaie", cid, f"nous : {ours or '—'} ; mledoze : {theirs or '—'}", why or C.DECISIONS.get(("monnaie", cid)))
        # langues
        wdl = [l["fr"] for l in ID.wikidata_languages(e)]
        mll = sorted((m.get("languages") or {}).values())
        if set(wdl) != set(c["languages_fr"] or []) or (m and len(mll) != len(c["languages_fr"] or [])):
            why = ov(cid, "languages_fr") or ("règle : langues présentes dans les deux sources (codes ISO 639-3) ; "
                                               "langues des signes non listées" if mll else "mledoze muet : Wikidata seul")
            rep.add("langues", cid, f"nous : {c['languages_fr'] or '—'} ; Wikidata : {wdl or '—'} ; mledoze : {mll or '—'}", why)
        # gentilé
        mm = ((m.get("demonyms") or {}).get("fra") or {}).get("m")
        if fk(mm) != fk(c["demonym_fr"]):
            if ov(cid, "demonym_fr"):
                why = ov(cid, "demonym_fr")
            elif not c["demonym_fr"]:
                why = "Wikidata vide → null (mledoze sert seulement au contrôle)"
            elif not mm:
                why = "mledoze muet : Wikidata conservé"
            elif fk(mm) == fk(c["demonym_fr"]) + "e":
                why = "mledoze donne le féminin ; masculin de Wikidata conservé"
            else:
                why = "forme Wikidata conservée (source principale)"
            rep.add("gentilé", cid, f"nous : {c['demonym_fr'] or '—'} ; mledoze : {mm or '—'}", why)
        # indicatif
        idd = m.get("idd") or {}
        root, suf = idd.get("root") or "", idd.get("suffixes") or []
        ml_code = root + suf[0] if root and len(suf) == 1 else root
        ours_c = (c["calling_code"] or "").replace(" ", "")
        if m and not (ours_c and ml_code and (ours_c.startswith(ml_code) or ml_code.startswith(ours_c.split(",")[0]))):
            if ov(cid, "calling_code"):
                why = ov(cid, "calling_code")
            elif not ours_c:
                why = "Wikidata vide → null (mledoze sert seulement au contrôle)"
            else:
                why = "Wikidata conservé (source principale)"
            rep.add("indicatif", cid, f"nous : {c['calling_code'] or '—'} ; mledoze : {ml_code or '—'}", why)
        # domaine
        mt = [t for t in (m.get("tld") or [])]
        if m and set((c["tld"] or "").split(", ")) - {""} != set(mt):
            if ov(cid, "tld"):
                why = ov(cid, "tld")
            elif not c["tld"]:
                why = "Wikidata vide → null (mledoze sert seulement au contrôle)"
            else:
                why = ("règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD "
                       "et domaine de l'État souverain écartés")
            rep.add("domaine", cid, f"nous : {c['tld'] or '—'} ; mledoze : {', '.join(mt) or '—'}", why)


TITLES = {
    "plaque": "Plaque d'immatriculation — code enregistré à l'ONU (tableau Wikipédia EN) contre Wikidata",
    "circulation": "Sens de circulation — Wikidata contre Wikipédia EN (« Left- and right-hand traffic »)",
    "monnaie": "Monnaies — Wikidata contre mledoze/countries",
    "langues": "Langues officielles — Wikidata contre mledoze/countries",
    "gentilé": "Gentilé — Wikidata contre mledoze/countries (`demonyms.fra.m`)",
    "indicatif": "Indicatif téléphonique — Wikidata contre mledoze/countries (`idd`)",
    "domaine": "Domaine internet — Wikidata contre mledoze/countries (`tld`)",
    "capitale": "Capitales — contre anki-geo/ultimate-geography (`capital:fr`)",
    "capitale-en": "Capitales — contre mledoze/countries (`capital`, libellés anglais Wikidata)",
    "continent": "Continent — contre mledoze/countries (`region`/`subregion`)",
    "voisins": "Voisins — Wikidata P47 et mledoze contre la géométrie Natural Earth",
    "superficie": f"Superficie — contre mledoze/countries (écart > {AREA_TOLERANCE:.0%})",
    "géométrie": f"Capitales hors de leur polygone (> {MAX_CAPITAL_KM} km)",
    "complétude": "Complétude",
    "couverture": "Couverture des sources de recoupement",
}


def write_report(rep: Report, countries: list[dict], cached_fr: int) -> None:
    n_etat = sum(c["kind"] == "etat" for c in countries)
    L = [
        "# Rapport de données — Geo Atlas",
        "",
        f"Généré par `tools/data/check_data.py` le {dt.date.today().isoformat()}. Ne pas éditer à la main : "
        "les décisions se règlent dans `tools/data/curation.py` (`CAPITALS`, `DECISIONS`…).",
        "",
        f"- Entités : {len(countries)} ({n_etat} États, {len(countries) - n_etat} territoires)",
        f"- Désaccords relevés : {sum(len(v) for v in rep.sections.values())} ; **non tranchés : {rep.open}**",
        f"- Articles Wikipédia FR des pays en cache : {cached_fr}/{len(countries)} "
        "(pas de pré-remplissage en masse : décision du coordinateur, limite Wikimedia de 10 requêtes/min ; "
        "les rédacteurs de faits récupèrent ce qu'ils citent)",
        "",
        "## Capitales réglées à la main",
        "",
        "| id | capitale(s) et rôle |",
        "|---|---|",
    ]
    by_id = {c["id"]: c for c in countries}
    for cid in sorted(C.CAPITALS):
        caps = by_id[cid]["capitals"]
        L.append(f"| {cid} | " + " ; ".join(f"**{x['name_fr']}** — {x['role_fr']}" for x in caps) + " |")
    for cid, why in sorted(C.NO_CAPITAL.items()):
        L.append(f"| {cid} | — {why} |")
    L += ["", "Notes de vérification : " + C.CAPITAL_NOTES, ""]
    lic = load_json(DATA / "flags" / "LICENSES.json")
    L += ["## Drapeaux réglés à la main", "", "| id | fichier | en quiz | note |", "|---|---|---|---|"]
    for cid, (fn, quizzable, note) in sorted(C.FLAG_OVERRIDE.items()):
        L.append(f"| {cid} | {lic.get(cid, {}).get('file') or fn or '—'} | {'oui' if quizzable else 'non'} | {note or ''} |")
    shared = sorted(k for k, v in lic.items() if v.get("shared_with"))
    lipis = sorted(k for k, v in lic.items() if v.get("source") == "lipis")
    L += ["", f"Drapeau identique à celui de l'État souverain (flag_shared_with, hors quiz) : {', '.join(shared)}.",
          f"Repli lipis/flag-icons (ratio 4:3, pas les vraies proportions) : {', '.join(lipis) or 'aucun'}.", ""]
    for sec in TITLES:
        items = rep.sections.get(sec)
        if not items:
            continue
        L += [f"## {TITLES[sec]}", "", "| id | désaccord | décision |", "|---|---|---|"]
        for cid, what, decision in sorted(items):
            L.append(f"| {cid} | {what} | {decision or '**NON TRANCHÉ**'} |")
        L.append("")
    if C.BLOCKERS:
        L += ["## Blocages", ""] + [f"- {b}" for b in C.BLOCKERS] + [""]
    (DATA / "DATA_REPORT.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
