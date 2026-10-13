"""Carte d'identité des entités : plaque, circulation, monnaies, langues, gentilé, indicatif, domaine, sommet, devise.

Valeurs tirées de Wikidata (cache/wikidata/entities.json), sauf :
- plate_code : codes enregistrés à l'ONU (Convention de Vienne), tableau « International vehicle registration code »
  de Wikipédia EN (sources_en.py) ; Wikidata sert de contrôle (il contient des codes anciens ou non officiels) ;
- highest_point : retenu seulement si l'article Wikipédia FR de l'entité nomme le sommet avec une altitude à moins
  de 1 % de celle de Wikidata ; l'altitude affichée est celle de l'article (celle que citent les faits).
mledoze/countries (ODbL) ne fournit aucune valeur : il sert seulement à filtrer ou à départager celles de Wikidata
(langues confirmées par les deux sources, graphie du gentilé). Corrections motivées : curation.IDENTITY_OVERRIDE.
"""
from __future__ import annotations

import re
import unicodedata

import curation as C

RIGHT, LEFT = "Q14565199", "Q11920728"
MASCULINE, FEMININE, PLURAL = "Q499327", "Q1775415", "Q146786"

# Codes ISO 639-3 considérés comme la même langue pour le recoupement Wikidata / mledoze.
LANG_EQ = {"cmn": "zho", "yue": "zho", "ell": "gre", "gsw": "deu", "nob": "nor", "nno": "nor", "zgh": "ber",
           "tzm": "ber", "ckb": "kur", "kmr": "kur", "smi": "sme", "nrf": "nfr", "zsm": "msa", "prs": "fas",
           "pes": "fas"}
SUMMIT_STOP = {"mont", "monts", "pic", "pico", "monte", "mount", "cerro", "nevado", "pointe", "signal", "morne",
               "djebel", "jabal", "jebel", "de", "du", "la", "le", "les", "des", "massif", "sommet", "montagne"}


def fold(s: str) -> str:
    s = unicodedata.normalize("NFD", (s or "").lower())
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn")


def _ok(st: dict) -> bool:
    return st.get("rank") != "DeprecatedRank" and not st.get("end")


def _current(stmts: list[dict]) -> list[dict]:
    """Déclarations en cours ; si l'une est préférée, seulement les préférées."""
    cur = [s for s in stmts if _ok(s)]
    if any(s["rank"] == "PreferredRank" for s in cur):
        cur = [s for s in cur if s["rank"] == "PreferredRank"]
    return cur


def _uniq(seq):
    out = []
    for x in seq:
        if x and x not in out:
            out.append(x)
    return out


# --------------------------------------------------------------------------- champs


def wikidata_plates(e: dict) -> list[str]:
    return _uniq(s["code"].strip() for s in _current(e["plates"]))


def driving_side(e: dict) -> str | None:
    sides = _uniq({RIGHT: "droite", LEFT: "gauche"}.get(s["qid"]) for s in _current(e["driving"]))
    return sides[0] if len(sides) == 1 else None


def currencies(e: dict) -> list[dict]:
    by_iso: dict[str, dict] = {}
    for s in _current(e["currencies"]):
        iso = s.get("iso") or ""
        if not re.fullmatch(r"[A-Z]{3}", iso):
            continue                                   # codes numériques ISO 4217, monnaies sans code
        name = s.get("fr")
        name = name[:1].lower() + name[1:] if name else name
        cur = by_iso.setdefault(iso, {"code": iso, "name_fr": name, "symbol": s.get("symbol")})
        sym = s.get("symbol")
        if sym and _symbol_rank(sym) < _symbol_rank(cur["symbol"]):
            cur["symbol"] = sym
        if not cur["name_fr"] and s.get("fr"):
            cur["name_fr"] = s["fr"]
    return sorted(by_iso.values(), key=lambda c: c["code"])


def _symbol_rank(sym: str | None) -> tuple:
    """Préférence : symbole lisible en écriture latine ou signe monétaire courant, puis le plus court.
    Les signes Unicode les plus récents (à partir de U+20C0) ne s'affichent pas encore dans la plupart des polices."""
    if not sym or any(ord(ch) >= 0x20C0 and not 0xFB50 <= ord(ch) <= 0xFDFF for ch in sym):
        return (9, 0)
    latin = all(ord(ch) < 0x250 or 0x20A0 <= ord(ch) < 0x20C0 for ch in sym)
    return (0 if latin else 1, len(sym))


def wikidata_languages(e: dict) -> list[dict]:
    out: dict[str, dict] = {}
    for s in _current(e["languages"]):
        fr = s.get("fr")
        if not fr or fold(fr).startswith("langue des signes"):
            continue                                   # règle : langues des signes non listées
        label = fr[:1].lower() + fr[1:]
        rec = out.setdefault(fr, {"fr": C.LANG_NAME_FR.get(label, label), "iso3": s.get("iso3")})
        if s.get("iso3") and not rec["iso3"]:
            rec["iso3"] = s["iso3"]
    return sorted(out.values(), key=lambda l: l["fr"])


def languages(e: dict, ml: dict | None) -> list[str]:
    """Langues Wikidata confirmées par mledoze (codes ISO 639-3 rapprochés) ; Wikidata seul si mledoze est muet."""
    wd = wikidata_languages(e)
    ml_codes = {LANG_EQ.get(k, k) for k in ((ml or {}).get("languages") or {})}
    if not ml_codes:
        return [l["fr"] for l in wd]
    return [l["fr"] for l in wd if l.get("iso3") and LANG_EQ.get(l["iso3"], l["iso3"]) in ml_codes]


def demonym(e: dict, ml: dict | None) -> str | None:
    feats: dict[str, set] = {}
    for s in e["demonyms"]:
        if _ok(s):
            feats.setdefault(s["text"].strip(), set()).add(s.get("feat"))
    if not feats:
        return None
    masc = [t for t, f in feats.items() if MASCULINE in f and not f & {FEMININE, PLURAL}]
    plain = [t for t, f in feats.items() if not f & {FEMININE, PLURAL}] or list(feats)
    base = min(masc or plain, key=len)                 # « Ivoirien » plutôt que « Ivoirienne »
    ml_m = (((ml or {}).get("demonyms") or {}).get("fra") or {}).get("m")
    key = lambda s: re.sub(r"[\s\-]", "", fold(s))
    if ml_m and key(ml_m) != key(base) + "e":         # mledoze donne parfois le féminin (Kirghize, Tadjike)
        same = [t for t in feats if key(t) == key(ml_m)]
        if same:
            base = same[0]                             # graphie de Wikidata, mot confirmé par mledoze
    return "-".join(part[:1].upper() + part[1:] for part in base.split("-"))   # « Sud-Africain »


def calling_code(e: dict) -> str | None:
    codes = _uniq("+" + re.sub(r"[^\d ]", "", s["code"]).strip() for s in _current(e["calling"]))
    codes = [c for c in codes if c != "+"]
    return ", ".join(codes) if codes else None


def tlds(e: dict) -> list[str]:
    """Domaines nationaux en lettres latines (2 lettres) ; les gTLD et domaines internationalisés sont écartés."""
    labs = _uniq((s.get("label") or "").strip().lower() for s in _current(e["tlds"]))
    return [l if l.startswith(".") else "." + l for l in labs if re.fullmatch(r"\.?[a-z]{2}", l)]


def wikidata_highest(e: dict) -> dict | None:
    """Sommet unique, altitudes Wikidata concordantes entre elles (à 1 %)."""
    pts: dict[str, dict] = {}
    for s in _current(e["highest"]):
        p = pts.setdefault(s["qid"], {"name_fr": s.get("fr"), "elev": set()})
        if s.get("elev"):
            p["elev"].add(float(s["elev"]))
    if len(pts) != 1:
        return None
    p = next(iter(pts.values()))
    if not p["name_fr"] or not p["elev"] or max(p["elev"]) - min(p["elev"]) > 0.01 * max(p["elev"]):
        return None
    return {"name_fr": p["name_fr"], "elevation_m": round(sorted(p["elev"])[len(p["elev"]) // 2])}


# Termes génériques français : minuscule initiale (« mont Blanc », « massif Vinson ») ; les génériques étrangers
# font partie du nom propre (« Pico Duarte », « Nevado Sajama », « Ben Nevis »).
SUMMIT_GENERIC = ("mont", "monts", "massif", "pic", "pointe", "sommet", "col", "volcan", "montagne", "morne",
                  "piton", "signal", "djebel")


def summit_name(name: str) -> str:
    """Minuscule au terme générique français en tête de nom (et après « / » : « Aoraki/mont Cook »)."""
    def fix(part: str) -> str:
        generic = " " in part and fold(part.split(" ", 1)[0]) in SUMMIT_GENERIC
        return (part[:1].lower() if generic else part[:1].upper()) + part[1:]   # « La Soufrière » reste capitalisé
    return "/".join(fix(p) for p in name.split("/"))


def highest_point(e: dict, fr_text: str | None) -> dict | None:
    hp = wikidata_highest(e)
    if not hp or not fr_text:
        return None
    words = [w for w in re.findall(r"[\w']+", fold(hp["name_fr"])) if w not in SUMMIT_STOP and len(w) > 2]
    ft = fold(fr_text)
    for w in words:
        for m in re.finditer(re.escape(w), ft):
            win = fr_text[max(0, m.start() - 160):m.end() + 160]
            for n in re.finditer(r"(\d{1,2}[\s  ]?\d{3}|\d{2,4})(?:[,.]\d+)?\s*(?:m\b|mètres)", win):
                v = int(re.sub(r"[\s  ]", "", n.group(1)))
                if abs(v - hp["elevation_m"]) <= 0.01 * hp["elevation_m"]:
                    return {"name_fr": summit_name(hp["name_fr"]), "elevation_m": v}
    return None


def motto(e: dict) -> str | None:
    fr = _uniq(s["text"].strip() for s in e["mottos"] if _ok(s) and (s.get("lang") or "").startswith("fr"))
    return fr[0] if fr else None


# --------------------------------------------------------------------------- assemblage


def identity(cid: str, e: dict, *, un_plates: dict[str, list[str]], ml: dict | None, fr_text: str | None,
             sovereign: str | None, sovereign_tlds: list[str], sovereign_motto: str | None) -> dict:
    tld = [t for t in tlds(e) if not (sovereign and t in sovereign_tlds)]
    mot = motto(e)
    if sovereign and mot and sovereign_motto and fold(mot) == fold(sovereign_motto):
        mot = None                                     # territoire : pas la devise de l'État souverain
    out = {
        "plate_code": un_plates.get(cid) or None,
        "driving_side": driving_side(e),
        "currencies": [{k: c[k] for k in ("code", "name_fr", "symbol")} for c in currencies(e)] or None,
        "languages_fr": languages(e, ml) or None,
        "demonym_fr": demonym(e, ml),
        "calling_code": calling_code(e),
        "tld": ", ".join(tld) or None,
        "highest_point": highest_point(e, fr_text),
        "motto_fr": mot,
    }
    for cur in out["currencies"] or []:
        if _symbol_rank(cur["symbol"])[0] == 9:
            cur["symbol"] = None
    for k, (v, _why) in C.IDENTITY_OVERRIDE.get(cid, {}).items():
        out[k] = v
    return out


# Noms français manquants sur Wikidata (libellé absent).
CURRENCY_NAME_FR = {"EUR": "euro"}

IDENTITY_FIELDS = ("plate_code", "driving_side", "currencies", "languages_fr", "demonym_fr", "calling_code", "tld",
                   "highest_point", "motto_fr")
