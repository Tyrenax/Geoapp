"""Géométries : Natural Earth 10m (admin_0_map_units) → data/geo/world.topo.json, et label/small dans countries.json.

    python tools/data/build_geo.py

Objets du TopoJSON (topologie partagée, mapshaper) :
  countries : une géométrie par entité, propriété `id` (notre id ISO alpha-3) ;
  other     : zones neutres non quizzables (disputées, sans État ou sans code ISO), propriétés `ne`, `name_fr` ;
  land      : toutes les terres fusionnées (côtes), pour dessiner la terra incognita.

`small` = la plus grande pièce de l'entité fait moins de SMALL_KM2 (trop petite pour être cliquée à l'échelle
monde : ~120 × 120 km, soit environ 5 × 5 px sur une carte du monde de 1 600 px de large).
"""
from __future__ import annotations

import json
import subprocess
import sys

from pyproj import Geod
from shapely.geometry import shape, mapping
from shapely import STRtree
from shapely.ops import polylabel, unary_union

from common import CACHE, DATA, download, iso_rows, load_json, utf8_stdout, write_json

NE_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/{}.geojson"
SMALL_KM2 = 15000
TOPO_MAX_BYTES = 1_500_000
NEIGHBOR_DEG = 0.005  # ~500 m : tolère les micro-écarts entre polygones Natural Earth

# Unités Natural Earth sans ISO_A3 (« -99 ») → notre id (clé : SU_A3).
NE_TO_ID = {
    "GAZ": "PSE", "WEB": "PSE",                      # Gaza, Cisjordanie
    "SOP": "SOM", "SOX": "SOM", "SOL": "SOM",        # Puntland, Somalie, Somaliland → Somalie
    "SYU": "SYR",                                    # zone de la FNUOD, côté syrien
    "KNX": "KOR", "KNZ": "PRK",                      # moitiés de la zone démilitarisée
    "BFR": "BEL", "BWR": "BEL", "BCR": "BEL",
    "GEG": "GEO", "GEA": "GEO",
    "KOS": "XKX",
    "NIR": "GBR", "WLS": "GBR", "ENG": "GBR", "SCT": "GBR",
    "IRK": "IRQ", "IRR": "IRQ",
    "NLX": "NLD",
    "SRV": "SRB", "SRS": "SRB",
    "BHF": "BIH", "BIS": "BIH", "BHB": "BIH",
    "USG": "CUB",                                    # base de Guantánamo : territoire cubain loué
    "PRX": "PRT", "PMD": "PRT", "PAZ": "PRT",
    "PNX": "PNG", "PNB": "PNG",
    "CYN": "CYP",                                    # Chypre du Nord → Chypre (non reconnue, sauf par la Turquie)
    "KAB": "KAZ",                                    # Baïkonour, loué à la Russie
    "JQI": "UMI", "DQI": "UMI", "FQI": "UMI", "HQI": "UMI", "WQI": "UMI", "MQI": "UMI", "BQI": "UMI",
    "LQI": "UMI", "KQI": "UMI",
    "ACA": "ATG", "ACB": "ATG",
    "TZZ": "TZA",
    "NJM": "SJM",                                    # Jan Mayen fait partie du code ISO SJ
}

# Zones neutres (objet `other`) : SU_A3 → nom affiché.
NE_OTHER = {
    "ESB": "Dhekelia (base souveraine britannique)",
    "WSB": "Akrotiri (base souveraine britannique)",
    "CNM": "Zone tampon de l'ONU à Chypre",
    "KAS": "Glacier de Siachen (disputé)",
    "BRI": "Île brésilienne (disputée)",
    "SPI": "Champ de glace Sud de Patagonie (disputé)",
    "BRT": "Bir Tawil (revendiqué par aucun État)",
    "PFA": "Îles Paracels (disputées)",
    "PGA": "Îles Spratleys (disputées)",
    "BJN": "Banc Bajo Nuevo (disputé)",
    "SER": "Banc Serranilla (disputé)",
    "SCR": "Récif de Scarborough (disputé)",
    "CLP": "Île de Clipperton (France, sans code ISO)",
    "CSI": "Îles de la mer de Corail (Australie, sans code ISO)",
    "ATC": "Îles Ashmore-et-Cartier (Australie, sans code ISO)",
}

# Zones de ne_10m_admin_0_disputed_areas retirées de l'État qui les administre (vue « de fait » de Natural
# Earth) : clé (SU_A3, BRK_NAME) → ("id", cible) pour rattacher à une entité, ou ("other", nom) pour la
# couche neutre. Règle : un territoire de la liste ONU des territoires non autonomes garde toute son étendue ;
# une annexion non reconnue par l'ONU devient zone neutre, sans trancher.
DISPUTED_CARVE = {
    ("MAR", "W. Sahara"): ("id", "ESH"),
    ("RUC", "Crimea"): ("other", "Crimée (administrée par la Russie, revendiquée par l'Ukraine)"),
    ("ISR", "Golan Heights"): ("other", "Plateau du Golan (administré par Israël, revendiqué par la Syrie)"),
}

GEOD = Geod(ellps="WGS84")
RELABEL = {"ESH", "MAR"}  # étendue changée par DISPUTED_CARVE : étiquette recalculée (pôle d'inaccessibilité)


def km2(geom) -> float:
    return abs(GEOD.geometry_area_perimeter(geom)[0]) / 1e6


def apply_stats(c: dict, stats: dict) -> None:
    """label/small d'une entité ; sans géométrie : marqueur sur la capitale, small = True."""
    s = stats.get(c["id"])
    if s:
        c["label"], c["small"] = s["label"], s["small"]
        c["neighbors"] = s["neighbors"]
    else:
        cap = c["capitals"][0] if c.get("capitals") else None
        c["label"] = {"lat": cap["lat"], "lon": cap["lon"]} if cap else c.get("label")
        c["small"] = True


def pieces(geom):
    return list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]


def tag_units(ids: set[str]) -> tuple[dict, dict, list[str]]:
    src = download(NE_URL.format("ne_10m_admin_0_map_units"), CACHE / "ne" / "ne_10m_admin_0_map_units.geojson")
    feats = load_json(src)["features"]
    by_id, other, problems = {}, {}, []
    for f in feats:
        p = f["properties"]
        iso, su = p["ISO_A3"], p["SU_A3"]
        geom = shape(f["geometry"]).buffer(0)
        if iso in ids:
            cid = iso
        elif su in NE_TO_ID:
            cid = NE_TO_ID[su]
        elif su in NE_OTHER:
            other[su] = {"geom": geom, "name_fr": NE_OTHER[su]}
            continue
        else:
            problems.append(f"unité Natural Earth non rattachée : {su} {p['NAME']} (ISO {iso})")
            continue
        by_id.setdefault(cid, []).append((geom, p))

    src = download(NE_URL.format("ne_10m_admin_0_disputed_areas"),
                   CACHE / "ne" / "ne_10m_admin_0_disputed_areas.geojson")
    found = set()
    for f in load_json(src)["features"]:
        p = f["properties"]
        k = (p["SU_A3"], p["BRK_NAME"])
        if k not in DISPUTED_CARVE:
            continue
        found.add(k)
        zone = shape(f["geometry"]).buffer(0)
        for cid in list(by_id):
            cut = [(clean(g.difference(zone)) if g.intersects(zone) else g, q) for g, q in by_id[cid]]
            by_id[cid] = [(g, q) for g, q in cut if not g.is_empty]
        kind, target = DISPUTED_CARVE[k]
        if kind == "id":
            by_id[target].append((zone, {**p, "LABEL_X": None, "LABEL_Y": None}))
        else:
            other[p["SU_A3"]] = {"geom": zone, "name_fr": target}
    for k in set(DISPUTED_CARVE) - found:
        problems.append(f"zone disputée Natural Earth introuvable : {k}")
    return by_id, other, problems


def clean(g):
    """Retire les miettes (< 1 km²) laissées par une différence entre polygones presque jointifs."""
    parts = [x for x in pieces(g.buffer(0)) if not x.is_empty and km2(x) >= 1] if not g.is_empty else []
    return unary_union(parts) if parts else g.__class__()


def main():
    utf8_stdout()
    ids = {r["alpha-3"] for r in iso_rows()}
    by_id, other, problems = tag_units(ids)

    feats, stats = [], {}
    for cid, units in sorted(by_id.items()):
        geom = unary_union([g for g, _ in units])
        main_unit = max(units, key=lambda u: km2(u[0]))[1]
        biggest_piece = max(pieces(geom), key=km2)
        biggest = km2(biggest_piece)
        if main_unit.get("LABEL_X") is None or cid in RELABEL:
            pt = polylabel(biggest_piece, tolerance=0.01)
            main_unit = {"LABEL_X": pt.x, "LABEL_Y": pt.y}
        stats[cid] = {"label": {"lat": round(main_unit["LABEL_Y"], 3), "lon": round(main_unit["LABEL_X"], 3)},
                      "small": biggest < SMALL_KM2, "km2": km2(geom)}
        feats.append({"type": "Feature", "properties": {"id": cid}, "geometry": mapping(geom)})
    # voisins terrestres : géométries 10m à moins de ~500 m l'une de l'autre
    geoms = {cid: unary_union([g for g, _ in units]) for cid, units in by_id.items()}
    tree_ids = sorted(geoms)
    tree = STRtree([geoms[c] for c in tree_ids])
    for cid in tree_ids:
        near = tree.query(geoms[cid].buffer(NEIGHBOR_DEG))
        stats[cid]["neighbors"] = sorted(tree_ids[i] for i in near if tree_ids[i] != cid
                                         and geoms[cid].distance(geoms[tree_ids[i]]) < NEIGHBOR_DEG)
    other_feats = [{"type": "Feature", "properties": {"ne": k, "name_fr": v["name_fr"]}, "geometry": mapping(v["geom"])}
                   for k, v in sorted(other.items())]

    tmp = CACHE / "geo"
    tmp.mkdir(parents=True, exist_ok=True)
    (tmp / "countries.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": feats}), encoding="utf-8")
    (tmp / "other.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": other_feats}), encoding="utf-8")

    out = DATA / "geo" / "world.topo.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    pct = 0.30
    while True:
        cmd = ["npx", "-y", "mapshaper", "-i", str(tmp / "countries.geojson"), str(tmp / "other.geojson"),
               "combine-files", "snap",
               "-simplify", f"{pct:.3f}", "weighted", "keep-shapes", "planar",
               "-clean", "target=*", "allow-empty",
               "-dissolve2", "target=countries", "+", "name=land_c",
               "-dissolve2", "target=other", "+", "name=land_o",
               "-merge-layers", "target=land_c,land_o", "name=land", "force",
               "-dissolve2", "target=land",
               "-o", str(out), "format=topojson", "quantization=1000000", "target=countries,other,land"]
        subprocess.run(cmd, check=True, shell=sys.platform == "win32", capture_output=True)
        size = out.stat().st_size
        if size <= TOPO_MAX_BYTES or pct < 0.01:
            break
        pct *= 0.8
    topo = load_json(out)
    got = {g["properties"]["id"] for g in topo["objects"]["countries"]["geometries"] if g.get("type")}
    missing = sorted(ids - got)

    # label/small : relus par build_countries.py ; on met aussi à jour countries.json s'il existe déjà
    write_json(CACHE / "geo" / "stats.json", {k: {**v, "km2": round(v["km2"], 1)} for k, v in stats.items()})
    if (DATA / "countries.json").exists():
        countries = load_json(DATA / "countries.json")
        for c in countries:
            apply_stats(c, stats)
        write_json(DATA / "countries.json", countries)

    print(f"{out.relative_to(DATA.parent)} : {size / 1e6:.2f} Mo (simplification {pct:.3f}) ; "
          f"{len(got)} entités, {len(other_feats)} zones neutres ; small : {sum(s['small'] for s in stats.values())} ; "
          f"sans géométrie : {missing}")
    for p in problems:
        print("PROBLÈME :", p)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
