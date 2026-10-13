"""Outils partagés des scripts de données : chemins, requêtes HTTP mises en cache, SPARQL Wikidata."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "cache"
DATA = ROOT / "data"
USER_AGENT = "GeoAtlas/0.1 (jeu d'étude local)"
SPARQL_URL = "https://query.wikidata.org/sparql"

_session = requests.Session()
_session.headers["User-Agent"] = USER_AGENT


def utf8_stdout() -> None:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")


def http(method: str, url: str, tries: int = 6, **kw) -> requests.Response:
    """Requête avec réessai sur 429 / 5xx / erreur réseau."""
    delay = 2.0
    for attempt in range(tries):
        try:
            r = _session.request(method, url, timeout=kw.pop("timeout", 120), **kw)
        except requests.RequestException:
            if attempt == tries - 1:
                raise
            time.sleep(delay)
            delay *= 2
            continue
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(min(float(r.headers.get("Retry-After") or delay), 60))
            delay *= 2
            continue
        return r
    r.raise_for_status()
    return r


def download(url: str, dest: Path, refresh: bool = False) -> Path:
    """Télécharge une fois dans cache/ ; relit le fichier ensuite."""
    if dest.exists() and not refresh:
        return dest
    r = http("GET", url)
    r.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(r.content)
    return dest


def sparql(query: str, name: str, refresh: bool = False) -> list[dict]:
    """Résultat SPARQL simplifié (valeurs brutes), mis en cache dans cache/wikidata/<name>-<hash>.json."""
    h = hashlib.sha1(query.encode()).hexdigest()[:10]
    path = CACHE / "wikidata" / f"{name}-{h}.json"
    if path.exists() and not refresh:
        return json.loads(path.read_text(encoding="utf-8"))
    r = http("POST", SPARQL_URL, data={"query": query}, headers={"Accept": "application/sparql-results+json"})
    r.raise_for_status()
    rows = []
    for b in r.json()["results"]["bindings"]:
        row = {}
        for k, v in b.items():
            val = v["value"]
            if v["type"] == "uri" and val.startswith("http://www.wikidata.org/entity/"):
                val = val.rsplit("/", 1)[1]
            elif v["type"] == "uri" and "#" in val and "wikiba.se" in val:
                val = val.rsplit("#", 1)[1]
            row[k] = val
        rows.append(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=0), encoding="utf-8")
    return rows


ISO_CSV_URL = "https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv"


def iso_rows() -> list[dict]:
    """Liste ISO 3166-1 (249 codes, avec régions ONU M49) + Kosovo."""
    path = download(ISO_CSV_URL, CACHE / "sources" / "iso3166_all.csv")
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    rows.append({"name": "Kosovo", "alpha-2": "XK", "alpha-3": "XKX", "region": "Europe",
                 "sub-region": "Southern Europe", "intermediate-region": ""})
    return rows


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj, indent: int | None = 1) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=indent) + "\n", encoding="utf-8")
