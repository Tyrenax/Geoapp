"""Drapeaux en vraies proportions depuis Wikimedia Commons (P41 Wikidata) → data/flags/<ID>.svg + LICENSES.json.

    python tools/data/fetch_flags.py [--refresh]

Les SVG viennent directement de upload.wikimedia.org (chemin calculé par MD5, ce qui évite le quota de l'API) ;
les licences sont lues par lots de 50 via l'API Commons (imageinfo/extmetadata).
Repli : lipis/flag-icons (ratio 4:3 imposé, signalé) si Commons échoue.
Un territoire dont le drapeau est celui de son État souverain reçoit flag_shared_with + flag_quizzable: false.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import re
import sys
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

import curation as C
import wiki_cache as W
from build_countries import apply_flag, pick_flag_file
from common import CACHE, DATA, http, load_json, utf8_stdout, write_json

FLAGS = DATA / "flags"
LICENSES = FLAGS / "LICENSES.json"
LIPIS = "https://raw.githubusercontent.com/lipis/flag-icons/main/flags/4x3/{}.svg"


def commons_url(filename: str) -> str:
    name = filename.replace(" ", "_")
    h = hashlib.md5(name.encode()).hexdigest()
    return f"https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{name}"


def svg_ratio(data: bytes) -> float:
    """Largeur/hauteur d'un SVG ; lève ValueError si le fichier n'est pas un SVG exploitable."""
    root = ET.fromstring(data)
    if not root.tag.endswith("svg"):
        raise ValueError(f"racine {root.tag}")
    vb = root.get("viewBox")
    if vb:
        _, _, w, h = (float(x) for x in re.split(r"[\s,]+", vb.strip()))
    else:
        num = lambda v: float(re.match(r"[\d.]+", v).group())
        w, h = num(root.get("width")), num(root.get("height"))
    if w <= 0 or h <= 0:
        raise ValueError("dimensions nulles")
    return w / h


def fetch_svg(url: str) -> bytes:
    if "upload.wikimedia.org" in url:
        try:
            r = W.paced_get(url)
        except W.WikiError as e:
            raise ValueError(str(e)) from e
    else:
        r = http("GET", url)
    if r.status_code != 200:
        raise ValueError(f"HTTP {r.status_code} {url}")
    return r.content


def strip_html(s: str | None) -> str | None:
    if not s:
        return s
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def licences(files: list[str]) -> dict[str, dict]:
    """Licences Commons, mises en cache dans cache/flags/licences.json (relues sans réseau ensuite)."""
    path = CACHE / "flags" / "licences.json"
    out = load_json(path) if path.exists() else {}
    todo = [f for f in files if f not in out]
    for i in range(0, len(todo), 50):
        chunk = todo[i:i + 50]
        data = W.api_get("", {"action": "query", "prop": "imageinfo", "iiprop": "extmetadata|url",
                              "titles": "|".join("File:" + f for f in chunk)}, host="commons.wikimedia.org")
        norm = {n["to"]: n["from"] for n in data["query"].get("normalized", [])}
        for p in data["query"]["pages"]:
            title = norm.get(p["title"], p["title"])
            ii = (p.get("imageinfo") or [{}])[0]
            md = ii.get("extmetadata", {})
            val = lambda k: strip_html(md.get(k, {}).get("value"))
            out[title.removeprefix("File:").replace("_", " ")] = {
                "license": val("LicenseShortName"), "license_url": val("LicenseUrl"), "artist": val("Artist"),
                "page": ii.get("descriptionurl"),
            }
        write_json(path, out)
    return out


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--trust-existing", action="store_true",
                    help="reprendre les SVG déjà présents sans entrée dans LICENSES.json (sauf drapeaux corrigés)")
    args = ap.parse_args()
    ents = load_json(CACHE / "wikidata" / "entities.json")
    FLAGS.mkdir(parents=True, exist_ok=True)
    old = load_json(LICENSES) if LICENSES.exists() else {}

    files = {cid: (C.FLAG_OVERRIDE.get(cid, (None,))[0] or pick_flag_file(e)) for cid, e in ents.items()}
    problems = []

    def get(cid):
        fn = files[cid]
        dest = FLAGS / f"{cid}.svg"
        if dest.exists() and not args.refresh and cid in old and old[cid].get("file") == fn:
            return cid, "cache", None
        if (dest.exists() and args.trust_existing and cid not in old
                and not C.FLAG_OVERRIDE.get(cid, (None,))[0]):
            return cid, ("commons" if fn else "lipis"), (None if fn else "pas de P41 sur Wikidata")
        if fn:
            try:
                data = fetch_svg(commons_url(fn))
                svg_ratio(data)
                dest.write_bytes(data)
                return cid, "commons", None
            except (ValueError, ET.ParseError) as e:
                err = f"Commons : {e}"
        else:
            err = "pas de P41 sur Wikidata"
        try:
            data = fetch_svg(LIPIS.format(ents[cid]["iso2_wd"].lower() if ents[cid]["iso2_wd"] else cid.lower()))
            svg_ratio(data)
            dest.write_bytes(data)
            return cid, "lipis", err
        except (ValueError, ET.ParseError, AttributeError) as e2:
            return cid, "absent", f"{err} ; lipis : {e2}"

    with ThreadPoolExecutor(max_workers=3) as ex:
        results = list(ex.map(get, sorted(ents)))

    lic = licences(sorted({f for f in files.values() if f}))
    out = {}
    for cid, how, err in results:
        fn = files[cid]
        dest = FLAGS / f"{cid}.svg"
        if how == "absent":
            problems.append(f"{cid} : pas de drapeau ({err})")
            continue
        if how == "cache":
            out[cid] = old[cid]
            continue
        rec = {"file": fn, "source": how, "ratio": round(svg_ratio(dest.read_bytes()), 4)}
        if how == "commons":
            rec.update(lic.get(fn, {}))
        else:
            rec.update({"license": "MIT (lipis/flag-icons)", "page": "https://github.com/lipis/flag-icons",
                        "warning": "ratio 4:3 imposé, pas les vraies proportions", "commons_error": err})
        out[cid] = rec

    # drapeau partagé avec l'État souverain
    for cid, rec in out.items():
        sov = C.TERRITORIES.get(cid, (None, None))[0]
        if sov and sov in out and rec.get("file") and rec["file"] == out[sov].get("file"):
            rec["shared_with"] = sov
        else:
            rec.pop("shared_with", None)
    write_json(LICENSES, dict(sorted(out.items())))

    if (DATA / "countries.json").exists():
        countries = load_json(DATA / "countries.json")
        for c in countries:
            apply_flag(c, out)
        write_json(DATA / "countries.json", countries)

    src = {}
    for r in out.values():
        src[r["source"]] = src.get(r["source"], 0) + 1
    print(f"{len(out)} drapeaux ({src}) ; partagés avec l'État souverain : "
          f"{sorted(k for k, r in out.items() if r.get('shared_with'))} ; sans licence lue : "
          f"{sorted(k for k, r in out.items() if not r.get('license'))}")
    for p in problems:
        print("PROBLÈME :", p)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
