"""Collecte Wikidata (SPARQL) pour les ~250 entités → cache/wikidata/entities.json (données brutes, avec rangs).

    python tools/data/fetch_wikidata.py [--refresh]

Les choix (capitale retenue, population la plus récente…) sont faits dans build_countries.py.
"""
from __future__ import annotations

import argparse
from collections import defaultdict

from common import CACHE, iso_rows, sparql, utf8_stdout, write_json

# Codes ISO à plusieurs éléments Wikidata, ou dont la déclaration P298 est dépréciée.
QID_OVERRIDE = {
    "ATA": "Q51",       # Antarctique (pas la « région du Traité sur l'Antarctique »)
    "PSE": "Q219060",   # État de Palestine (pas « Territoires palestiniens occupés »)
    "XKX": "Q1246",     # Kosovo : code utilisateur XK/XKX, P298 dépréciée sur Wikidata
    "NLD": "Q55",       # Pays-Bas (partie européenne), pas le Royaume des Pays-Bas (ABW, CUW, SXM ont leur code)
}


def iso_to_qid(refresh: bool) -> dict[str, str]:
    rows = sparql("""SELECT ?item ?code ?rank ?end WHERE {
      ?item p:P298 ?st . ?st ps:P298 ?code ; wikibase:rank ?rank .
      OPTIONAL { ?st pq:P582 ?end } }""", "iso3", refresh)
    cands = defaultdict(set)
    for r in rows:
        if r["rank"] != "DeprecatedRank" and "end" not in r:
            cands[r["code"]].add(r["item"])
    out = {}
    for row in iso_rows():
        code = row["alpha-3"]
        if code in QID_OVERRIDE:
            out[code] = QID_OVERRIDE[code]
        elif len(cands[code]) == 1:
            out[code] = next(iter(cands[code]))
        else:
            raise SystemExit(f"{code} : éléments Wikidata ambigus {sorted(cands[code])}")
    return out


def values(qids) -> str:
    return "VALUES ?item { " + " ".join(f"wd:{q}" for q in sorted(qids)) + " }"


def collect(refresh: bool = False) -> dict:
    qids = iso_to_qid(refresh)
    by_qid = {q: c for c, q in qids.items()}
    V = values(by_qid)
    ent = {c: {"id": c, "qid": q, "official_fr": [], "alt_fr": [], "capitals": [], "population": [], "area": [],
               "borders": [], "flag_images": [], "flag_items": [], "history_items": [], "un_member": False,
               "country": [], "instance_of": [],
               "plates": [], "driving": [], "currencies": [], "languages": [], "demonyms": [], "calling": [],
               "tlds": [], "highest": [], "mottos": []}
           for c, q in qids.items()}

    def each(name, query):
        for r in sparql(query, name, refresh):
            yield ent[by_qid[r["item"]]], r

    for e, r in each("base", f"""SELECT ?item ?fr ?en ?iso2 ?wfr ?wen WHERE {{ {V}
        OPTIONAL {{ ?item rdfs:label ?fr FILTER(lang(?fr)="fr") }}
        OPTIONAL {{ ?item rdfs:label ?en FILTER(lang(?en)="en") }}
        OPTIONAL {{ ?item wdt:P297 ?iso2 }}
        OPTIONAL {{ ?wfr schema:about ?item ; schema:isPartOf <https://fr.wikipedia.org/> }}
        OPTIONAL {{ ?wen schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> }} }}"""):
        e.update(label_fr=r.get("fr"), label_en=r.get("en"), iso2_wd=r.get("iso2"),
                 wiki_fr=r.get("wfr"), wiki_en=r.get("wen"))

    for e, r in each("alt", f"""SELECT ?item ?alt WHERE {{ {V} ?item skos:altLabel ?alt FILTER(lang(?alt)="fr") }}"""):
        e["alt_fr"].append(r["alt"])

    for e, r in each("official", f"""SELECT ?item ?name ?rank ?end WHERE {{ {V}
        ?item p:P1448 ?st . ?st ps:P1448 ?name ; wikibase:rank ?rank . FILTER(lang(?name)="fr")
        OPTIONAL {{ ?st pq:P582 ?end }} }}"""):
        e["official_fr"].append({"name": r["name"], "rank": r["rank"], "end": r.get("end")})

    for e, r in each("capitals", f"""SELECT ?item ?st ?cap ?capfr ?rank ?start ?end ?role ?rolefr ?coord ?wfr ?nat WHERE {{ {V}
        ?item p:P36 ?st . ?st ps:P36 ?cap ; wikibase:rank ?rank .
        OPTIONAL {{ ?st pq:P580 ?start }} OPTIONAL {{ ?st pq:P582 ?end }}
        OPTIONAL {{ ?st pq:P3831 ?role . OPTIONAL {{ ?role rdfs:label ?rolefr FILTER(lang(?rolefr)="fr") }} }}
        OPTIONAL {{ ?cap rdfs:label ?capfr0 FILTER(lang(?capfr0)="fr") }}
        OPTIONAL {{ ?cap rdfs:label ?capen FILTER(lang(?capen)="en") }}
        BIND(COALESCE(?capfr0, ?capen) AS ?capfr)
        OPTIONAL {{ ?cap wdt:P625 ?coord }}
        OPTIONAL {{ ?st pq:P1310 ?nat }}
        OPTIONAL {{ ?wfr schema:about ?cap ; schema:isPartOf <https://fr.wikipedia.org/> }} }}"""):
        e["capitals"].append({k: r.get(k) for k in ("st", "cap", "capfr", "rank", "start", "end", "role", "rolefr",
                                                     "coord", "wfr", "nat")})

    for e, r in each("population", f"""SELECT ?item ?pop ?date ?rank WHERE {{ {V}
        ?item p:P1082 ?st . ?st ps:P1082 ?pop ; wikibase:rank ?rank . OPTIONAL {{ ?st pq:P585 ?date }} }}"""):
        e["population"].append({"value": r["pop"], "date": r.get("date"), "rank": r["rank"]})

    for e, r in each("area", f"""SELECT ?item ?m2 ?rank ?date ?applies WHERE {{ {V}
        ?item p:P2046 ?st . ?st psn:P2046 ?v ; wikibase:rank ?rank . ?v wikibase:quantityAmount ?m2 .
        OPTIONAL {{ ?st pq:P585 ?date }} OPTIONAL {{ ?st pq:P518 ?applies }} }}"""):
        e["area"].append({"m2": r["m2"], "rank": r["rank"], "date": r.get("date"), "applies": r.get("applies")})

    for e, r in each("borders", f"""SELECT ?item ?other ?rank ?end WHERE {{ {V}
        ?item p:P47 ?st . ?st ps:P47 ?other ; wikibase:rank ?rank . OPTIONAL {{ ?st pq:P582 ?end }} }}"""):
        if r["other"] in by_qid:
            e["borders"].append({"id": by_qid[r["other"]], "rank": r["rank"], "end": r.get("end")})

    for e, r in each("flagimg", f"""SELECT ?item ?img ?rank ?start ?end WHERE {{ {V}
        ?item p:P41 ?st . ?st ps:P41 ?img ; wikibase:rank ?rank .
        OPTIONAL {{ ?st pq:P580 ?start }} OPTIONAL {{ ?st pq:P582 ?end }} }}"""):
        e["flag_images"].append({"file": r["img"].rsplit("/", 1)[1], "rank": r["rank"], "start": r.get("start"),
                                 "end": r.get("end")})

    for e, r in each("flagitem", f"""SELECT ?item ?flag ?rank ?end ?wfr WHERE {{ {V}
        ?item p:P163 ?st . ?st ps:P163 ?flag ; wikibase:rank ?rank . OPTIONAL {{ ?st pq:P582 ?end }}
        OPTIONAL {{ ?wfr schema:about ?flag ; schema:isPartOf <https://fr.wikipedia.org/> }} }}"""):
        e["flag_items"].append({"qid": r["flag"], "rank": r["rank"], "end": r.get("end"), "wfr": r.get("wfr")})

    for e, r in each("history", f"""SELECT ?item ?h ?wfr WHERE {{ {V} ?item wdt:P2184 ?h .
        OPTIONAL {{ ?wfr schema:about ?h ; schema:isPartOf <https://fr.wikipedia.org/> }} }}"""):
        e["history_items"].append({"qid": r["h"], "wfr": r.get("wfr")})

    for e, r in each("un", f"""SELECT ?item WHERE {{ {V} ?item p:P463 ?st . ?st ps:P463 wd:Q1065 .
        FILTER NOT EXISTS {{ ?st pq:P582 ?end }} }}"""):
        e["un_member"] = True

    for e, r in each("country", f"""SELECT ?item ?c ?cfr WHERE {{ {V} ?item wdt:P17 ?c .
        OPTIONAL {{ ?c rdfs:label ?cfr FILTER(lang(?cfr)="fr") }} }}"""):
        e["country"].append({"qid": r["c"], "id": by_qid.get(r["c"]), "label_fr": r.get("cfr")})

    for e, r in each("instance", f"""SELECT ?item ?c ?cfr WHERE {{ {V} ?item wdt:P31 ?c .
        OPTIONAL {{ ?c rdfs:label ?cfr FILTER(lang(?cfr)="fr") }} }}"""):
        e["instance_of"].append(r.get("cfr") or r["c"])

    collect_identity(V, each)
    return dict(sorted(ent.items()))


def collect_identity(V: str, each) -> None:
    """Carte d'identité : plaque, circulation, monnaies, langues, gentilé, indicatif, domaine, sommet, devise."""
    def st(name, prop, extra_select="", extra_where=""):
        return f"""SELECT ?item ?v ?rank ?end {extra_select} WHERE {{ {V}
        ?item p:{prop} ?st . ?st ps:{prop} ?v ; wikibase:rank ?rank . OPTIONAL {{ ?st pq:P582 ?end }} {extra_where} }}"""

    for e, r in each("plates", st("plates", "P395", "?start", "OPTIONAL { ?st pq:P580 ?start }")):
        e["plates"].append({"code": r["v"], "rank": r["rank"], "end": r.get("end"), "start": r.get("start")})
    for e, r in each("driving", st("driving", "P1622", "?start", "OPTIONAL { ?st pq:P580 ?start }")):
        e["driving"].append({"qid": r["v"], "rank": r["rank"], "end": r.get("end"), "start": r.get("start")})
    for e, r in each("currencies", st("currencies", "P38", "?iso ?fr ?sym",
                                      """OPTIONAL { ?v wdt:P498 ?iso } OPTIONAL { ?v rdfs:label ?fr FILTER(lang(?fr)="fr") }
                                         OPTIONAL { ?v wdt:P5061 ?sym }""")):
        e["currencies"].append({"qid": r["v"], "rank": r["rank"], "end": r.get("end"), "iso": r.get("iso"),
                                "fr": r.get("fr"), "symbol": r.get("sym")})
    for e, r in each("languages", st("languages", "P37", "?fr ?iso3",
                                     """OPTIONAL { ?v rdfs:label ?fr FILTER(lang(?fr)="fr") }
                                        OPTIONAL { ?v wdt:P220 ?iso3 }""")):
        e["languages"].append({"qid": r["v"], "rank": r["rank"], "end": r.get("end"), "fr": r.get("fr"),
                               "iso3": r.get("iso3")})
    for e, r in each("demonyms", st("demonyms", "P1549", "?feat",
                                    """FILTER(lang(?v)="fr") OPTIONAL { ?st pq:P5713 ?feat }""")):
        e["demonyms"].append({"text": r["v"], "rank": r["rank"], "end": r.get("end"), "feat": r.get("feat")})
    for e, r in each("calling", st("calling", "P474")):
        e["calling"].append({"code": r["v"], "rank": r["rank"], "end": r.get("end")})
    for e, r in each("tlds", st("tlds", "P78", "?lab", """OPTIONAL { ?v rdfs:label ?lab FILTER(lang(?lab)="en") }""")):
        e["tlds"].append({"qid": r["v"], "rank": r["rank"], "end": r.get("end"), "label": r.get("lab")})
    for e, r in each("highest", st("highest", "P610", "?fr ?elev",
                                   """OPTIONAL { ?v rdfs:label ?fr FILTER(lang(?fr)="fr") }
                                      OPTIONAL { ?v p:P2044 ?es . ?es psn:P2044 ?en . ?en wikibase:quantityAmount ?elev .
                                                 ?es wikibase:rank ?er FILTER(?er != wikibase:DeprecatedRank) }""")):
        e["highest"].append({"qid": r["v"], "rank": r["rank"], "end": r.get("end"), "fr": r.get("fr"),
                             "elev": r.get("elev")})
    for e, r in each("mottos", st("mottos", "P1451", "?lang", """BIND(lang(?v) AS ?lang)""")):
        e["mottos"].append({"text": r["v"], "lang": r.get("lang"), "rank": r["rank"], "end": r.get("end")})


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()
    ent = collect(args.refresh)
    write_json(CACHE / "wikidata" / "entities.json", ent)
    n = len(ent)
    print(f"{n} entités ; membres ONU : {sum(e['un_member'] for e in ent.values())} ; "
          f"sans capitale P36 : {sum(not e['capitals'] for e in ent.values())} ; "
          f"sans drapeau P41 : {sum(not e['flag_images'] for e in ent.values())} ; "
          f"sans article fr : {sum(not e.get('wiki_fr') for e in ent.values())}")


if __name__ == "__main__":
    main()
