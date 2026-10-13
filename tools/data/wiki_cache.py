"""Cache local des textes Wikipédia (contrat : docs/ARCHITECTURE.md, section « Cache Wikipédia »).

    python tools/data/wiki_cache.py fetch <url>…     télécharge (si absent) et affiche « url -> chemin »
    python tools/data/wiki_cache.py path <url>       affiche le chemin du texte en cache (code 1 si absent)
    python tools/data/wiki_cache.py text <url>       affiche le texte en cache

Options de fetch : --refresh (retélécharge), --quiet (n'affiche que les erreurs).

Depuis Python : `from wiki_cache import fetch, cached_path, read_text, normalize_url`.

Texte brut par l'API `action=query&prop=extracts&explaintext=1&redirects=1` ; l'URL canonique est
celle d'après redirection. index.json est mis à jour sous un verrou de fichier : plusieurs processus
peuvent remplir le cache en même temps.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import threading
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

import requests

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "cache" / "wiki"
INDEX = CACHE / "index.json"
LOCK = CACHE / "index.lock"
USER_AGENT = "GeoAtlas/0.1 (jeu d'étude local)"
MAX_WORKERS = 3  # ≤ 3 requêtes Wikimedia en parallèle

_session_local = threading.local()


class WikiError(Exception):
    pass


# --------------------------------------------------------------------------- URL


def _upper_first(title: str) -> str:
    return title[:1].upper() + title[1:] if title else title


def normalize_title(title: str) -> str:
    title = unicodedata.normalize("NFC", unquote(title)).replace(" ", "_").strip("_")
    title = re.sub(r"_+", "_", title)
    return _upper_first(title)


def split_url(url: str) -> tuple[str, str]:
    """(langue, titre normalisé) d'une URL Wikipédia, sans réseau."""
    url = url.strip()
    parts = urlsplit(url if "://" in url else "https://" + url)
    m = re.fullmatch(r"([a-z\-]+)(?:\.m)?\.wikipedia\.org", parts.netloc.lower())
    if not m:
        raise WikiError(f"pas une URL Wikipédia : {url}")
    lang = m.group(1)
    if parts.path.startswith("/wiki/"):
        title = parts.path[len("/wiki/"):]
    else:
        q = parse_qs(parts.query)
        if "title" not in q:
            raise WikiError(f"titre introuvable dans l'URL : {url}")
        title = q["title"][0]
    title = normalize_title(title)
    if not title:
        raise WikiError(f"titre vide : {url}")
    return lang, title


def make_url(lang: str, title: str) -> str:
    return f"https://{lang}.wikipedia.org/wiki/{normalize_title(title)}"


def normalize_url(url: str) -> str:
    """Forme normalisée sans réseau (ne résout pas les redirections)."""
    return make_url(*split_url(url))


_WIN_RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


def safe_filename(title: str) -> str:
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", title).rstrip(". ")
    if name.split(".")[0].upper() in _WIN_RESERVED:
        name = "_" + name
    if len(name) > 120:  # chemins Windows : on garde de la marge
        name = name[:110] + "_" + hashlib.sha1(title.encode()).hexdigest()[:8]
    return name


# --------------------------------------------------------------------------- index


def load_index() -> dict:
    if not INDEX.exists():
        return {}
    return json.loads(INDEX.read_text(encoding="utf-8"))


class _FileLock:
    """Verrou inter-processus par création exclusive ; un verrou de plus de 60 s est considéré mort."""

    def __init__(self, path: Path = LOCK):
        self.path = path

    def __enter__(self):
        CACHE.mkdir(parents=True, exist_ok=True)
        deadline = time.time() + 120
        while True:
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                return self
            except FileExistsError:
                try:
                    if time.time() - self.path.stat().st_mtime > 60:
                        self.path.unlink(missing_ok=True)
                        continue
                except FileNotFoundError:
                    continue
                if time.time() > deadline:
                    raise WikiError(f"verrou {self.path} bloqué")
                time.sleep(0.05)

    def __exit__(self, *exc):
        self.path.unlink(missing_ok=True)


_thread_lock = threading.Lock()


def _update_index(entries: dict) -> None:
    with _thread_lock, _FileLock():
        index = load_index()
        index.update(entries)
        tmp = INDEX.with_suffix(f".{os.getpid()}.tmp")
        tmp.write_text(json.dumps(dict(sorted(index.items())), ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tmp, INDEX)


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _pick_file(lang: str, title: str, canonical: str, index: dict) -> Path:
    """Chemin du texte ; suffixe de hachage si un autre titre occupe déjà le même nom (Windows ignore la casse)."""
    base = safe_filename(title)
    taken = {e["file"].lower(): u for u, e in index.items() if not e.get("redirect_to")}
    rel = f"cache/wiki/{lang}/{base}.txt"
    owner = taken.get(rel.lower())
    if owner is not None and owner != canonical:
        rel = f"cache/wiki/{lang}/{base}__{hashlib.sha1(title.encode()).hexdigest()[:8]}.txt"
    return ROOT / rel


# --------------------------------------------------------------------------- réseau


def _contact() -> str | None:
    """Contact (URL ou e-mail) pour le User-Agent : variable GEOATLAS_UA_CONTACT ou fichier cache/ua_contact.txt."""
    c = os.environ.get("GEOATLAS_UA_CONTACT")
    f = ROOT / "cache" / "ua_contact.txt"
    if not c and f.exists():
        c = f.read_text(encoding="utf-8").strip()
    return c or None


def user_agent() -> str:
    c = _contact()
    return f"GeoAtlas/0.1 (jeu d'étude local; {c})" if c else USER_AGENT


# Wikimedia : 10 requêtes/min pour un client sans contact dans l'UA, 200/min avec. La cadence est partagée
# par tous les processus via cache/wiki/next_slot (créneau suivant) ; un 429 repousse tout le monde.
SLOT = CACHE / "next_slot"
SLOT_LOCK = CACHE / "next_slot.lock"


def _interval() -> float:
    return 0.4 if _contact() else 6.5


def _wait_slot(push_to: float | None = None, key: str = "") -> None:
    """Attend son créneau (file partagée `key` : "" = API, "upload" = fichiers de upload.wikimedia.org)."""
    slot_file = SLOT.with_name(SLOT.name + (f"_{key}" if key else ""))
    with _FileLock(SLOT_LOCK):
        now = time.time()
        try:
            nxt = float(slot_file.read_text())
        except (FileNotFoundError, ValueError):
            nxt = 0.0
        if push_to is not None:
            slot_file.write_text(str(max(nxt, push_to)))
            return
        slot = max(now, nxt)
        slot_file.write_text(str(slot + _interval()))
    time.sleep(max(0.0, slot - time.time()))


def paced_get(url: str, key: str = "upload", tries: int = 10) -> requests.Response:
    """GET cadencé (même règle que l'API) pour les fichiers Wikimedia ; 404 renvoyé tel quel."""
    delay = 2.0
    for _ in range(tries):
        _wait_slot(key=key)
        try:
            r = _session().get(url, timeout=60)
        except requests.RequestException:
            time.sleep(delay)
            delay *= 2
            continue
        if r.status_code == 429 or r.status_code >= 500:
            _wait_slot(push_to=time.time() + min(float(r.headers.get("Retry-After") or delay), 120), key=key)
            delay *= 2
            continue
        return r
    raise WikiError(f"abandon après {tries} essais : {url}")


def _session() -> requests.Session:
    s = getattr(_session_local, "s", None)
    if s is None:
        s = requests.Session()
        _session_local.s = s
    s.headers["User-Agent"] = user_agent()
    return s


def api_get(lang: str, params: dict, tries: int = 10, host: str | None = None) -> dict:
    """API MediaWiki de <lang>.wikipedia.org (ou de `host`, ex. commons.wikimedia.org), cadence partagée."""
    url = f"https://{host or lang + '.wikipedia.org'}/w/api.php"
    params = {"format": "json", "formatversion": "2", **params}
    delay = 2.0
    for attempt in range(tries):
        _wait_slot()
        try:
            r = _session().get(url, params=params, timeout=60)
        except requests.RequestException as e:
            if attempt == tries - 1:
                raise WikiError(f"réseau : {e}") from e
            time.sleep(delay)
            delay *= 2
            continue
        if r.status_code == 429 or r.status_code >= 500:
            wait = min(float(r.headers.get("Retry-After") or delay), 120)
            _wait_slot(push_to=time.time() + wait)
            delay *= 2
            continue
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            if data["error"].get("code") == "maxlag":
                time.sleep(delay)
                delay *= 2
                continue
            raise WikiError(f"API {lang} : {data['error']}")
        return data
    raise WikiError(f"API {lang} : abandon après {tries} essais")


def _fetch_one(url: str, refresh: bool) -> tuple[str, str]:
    """Retourne (url canonique, chemin relatif)."""
    lang, title = split_url(url)
    asked = make_url(lang, title)
    if not refresh:
        e = load_index().get(asked)
        if e and (ROOT / e["file"]).exists():
            return e.get("redirect_to", asked), e["file"]

    data = api_get(lang, {
        "action": "query", "prop": "extracts|info|pageprops", "explaintext": "1", "exsectionformat": "wiki",
        "redirects": "1", "ppprop": "disambiguation", "titles": title.replace("_", " "),
    })
    q = data["query"]
    pages = q.get("pages", [])
    if not pages or pages[0].get("missing") or pages[0].get("invalid"):
        raise WikiError(f"article absent : {asked}")
    page = pages[0]
    text = page.get("extract")
    if not text:
        raise WikiError(f"texte vide : {asked}")
    canonical = make_url(lang, page["title"])

    # titres parcourus avant l'arrivée (normalisation de casse, redirections)
    aliases = {asked}
    for step in q.get("normalized", []) + q.get("redirects", []):
        aliases.add(make_url(lang, step["from"]))
        aliases.add(make_url(lang, step["to"]))
    aliases.discard(canonical)

    with _thread_lock:
        path = _pick_file(lang, page["title"].replace(" ", "_"), canonical, load_index())
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        entry = {"file": _rel(path), "revid": page.get("lastrevid"), "fetched": dt.date.today().isoformat()}
        if "disambiguation" in page.get("pageprops", {}):
            entry["disambiguation"] = True
        entries = {canonical: entry}
        for a in aliases:
            entries[a] = {**entry, "redirect_to": canonical}
    _update_index(entries)
    return canonical, entry["file"]


def fetch(urls: list[str], refresh: bool = False, workers: int = MAX_WORKERS) -> dict[str, tuple[str, str] | WikiError]:
    """Télécharge les URL manquantes. Retourne {url demandée: (url canonique, chemin) ou WikiError}."""
    def run(u):
        try:
            return u, _fetch_one(u, refresh)
        except (WikiError, requests.HTTPError) as e:
            return u, WikiError(str(e))

    with ThreadPoolExecutor(max_workers=min(workers, MAX_WORKERS)) as ex:
        return dict(ex.map(run, urls))


def lookup(url: str) -> dict | None:
    """Entrée d'index (sans réseau) ; suit redirect_to."""
    index = load_index()
    e = index.get(normalize_url(url))
    if e and e.get("redirect_to"):
        e = index.get(e["redirect_to"], e)
    return e


def cached_path(url: str) -> Path | None:
    e = lookup(url)
    if e and (ROOT / e["file"]).exists():
        return ROOT / e["file"]
    return None


def canonical_url(url: str) -> str | None:
    index = load_index()
    key = normalize_url(url)
    e = index.get(key)
    return None if e is None else e.get("redirect_to", key)


def read_text(url: str) -> str | None:
    p = cached_path(url)
    return p.read_text(encoding="utf-8") if p else None


# --------------------------------------------------------------------------- CLI


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("urls", nargs="+")
    f.add_argument("--refresh", action="store_true")
    f.add_argument("--quiet", action="store_true")
    p = sub.add_parser("path")
    p.add_argument("url")
    t = sub.add_parser("text")
    t.add_argument("url")
    args = ap.parse_args(argv)

    if args.cmd == "fetch":
        failed = 0
        for asked, res in fetch(args.urls, refresh=args.refresh).items():
            if isinstance(res, WikiError):
                failed += 1
                print(f"ERREUR {asked} : {res}", file=sys.stderr)
            elif not args.quiet:
                canonical, rel = res
                note = "" if canonical == normalize_url(asked) else f"  (redirigé vers {canonical})"
                if load_index().get(canonical, {}).get("disambiguation"):
                    note += "  [page d'homonymie]"
                print(f"{canonical} -> {rel}{note}")
        return 1 if failed else 0

    try:
        path = cached_path(args.url)
    except WikiError as e:
        print(f"ERREUR : {e}", file=sys.stderr)
        return 2
    if path is None:
        print(f"absent du cache : {args.url}", file=sys.stderr)
        return 1
    if args.cmd == "path":
        print(_rel(path))
    else:
        sys.stdout.write(path.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
