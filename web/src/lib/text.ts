// Comparaison des réponses libres : accents, casse, tirets, articles, alias, petites fautes.

const ARTICLES = /^(le|la|les|l|the)\s+/

/** « L'Île-Maurice » → « ile maurice ». */
export function normalize(s: string): string {
  return s
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/œ/g, 'oe')
    .replace(/æ/g, 'ae')
    .replace(/[-‐‑–—'’`´.,()/]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(ARTICLES, '')
}

export function levenshtein(a: string, b: string): number {
  if (a === b) return 0
  if (!a.length) return b.length
  if (!b.length) return a.length
  let prev = Array.from({ length: b.length + 1 }, (_, i) => i)
  for (let i = 1; i <= a.length; i++) {
    const cur = [i]
    for (let j = 1; j <= b.length; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1
      cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
    }
    prev = cur
  }
  return prev[b.length]
}

/** Fautes tolérées selon la longueur du mot attendu. */
export function tolerance(len: number): number {
  if (len < 5) return 0
  if (len < 9) return 1
  return 2
}

export type Verdict = 'exact' | 'proche' | 'faux'

/**
 * `accepted` : toutes les formes justes (nom, alias, autres capitales) ;
 * `others` : les formes justes d'autres réponses possibles (autres pays) — une saisie qui y correspond
 * exactement, ou qui en est au moins aussi proche, est fausse (« Niger » n'est pas « Nigeria »).
 */
export function judge(input: string, accepted: string[], others: string[] = []): Verdict {
  const x = normalize(input)
  if (!x) return 'faux'
  const acc = accepted.map(normalize).filter(Boolean)
  if (acc.includes(x)) return 'exact'
  const oth = others.map(normalize).filter((o) => o && !acc.includes(o))
  if (oth.includes(x)) return 'faux'
  let best = Infinity
  for (const a of acc) {
    const d = levenshtein(x, a)
    if (d <= tolerance(a.length)) best = Math.min(best, d)
  }
  if (best === Infinity) return 'faux'
  for (const o of oth) if (levenshtein(x, o) <= best) return 'faux'
  return 'proche'
}

export interface Suggestion {
  label: string
  value: string
}

/** Liste de complétion : préfixe d'abord, puis début d'un mot, puis contenu. */
export function complete(input: string, items: Suggestion[], max = 6): Suggestion[] {
  const x = normalize(input)
  if (!x) return []
  const scored: { s: Suggestion; rank: number; n: string }[] = []
  const seen = new Set<string>()
  for (const s of items) {
    const n = normalize(s.label)
    let rank = -1
    if (n.startsWith(x)) rank = 0
    else if (n.split(' ').some((w) => w.startsWith(x))) rank = 1
    else if (x.length >= 3 && n.includes(x)) rank = 2
    if (rank >= 0 && !seen.has(s.value + '|' + s.label)) {
      seen.add(s.value + '|' + s.label)
      scored.push({ s, rank, n })
    }
  }
  scored.sort((a, b) => a.rank - b.rank || (a.n < b.n ? -1 : a.n > b.n ? 1 : 0))
  // Une même réponse n'apparaît qu'une fois (nom et alias qui commencent pareil).
  const out: Suggestion[] = []
  const values = new Set<string>()
  for (const { s } of scored) {
    if (values.has(s.value)) continue
    values.add(s.value)
    out.push(s)
    if (out.length >= max) break
  }
  return out
}

/** « la Bolivie », « l'Argentine », « les Fidji », « Saint-Christophe-et-Niévès ». */
export function withArticle(article: string | undefined | null, name: string): string {
  if (!article) return name
  if (article.endsWith("'") || article.endsWith('’')) return article + name
  return article + ' ' + name
}

/** « du Pérou », « de la Bolivie », « de l'Italie », « des Fidji », « de Saint-Christophe ». */
export function deArticle(article: string | undefined | null, name: string): string {
  if (article === 'le') return 'du ' + name
  if (article === 'les') return 'des ' + name
  if (!article) return 'de ' + name
  return 'de ' + withArticle(article, name)
}

export function capitalize(s: string): string {
  return s ? s[0].toUpperCase() + s.slice(1) : s
}

const nf = new Intl.NumberFormat('fr-FR')
/**
 * « 9 300 », avec une espace insécable ordinaire : l'espace fine (U+202F) d'Intl n'a pas de chasse
 * dans toutes les fontes et se lisait « 9300 ».
 */
export function formatNumber(n: number): string {
  return nf.format(n).replace(/[\u202f\u00a0\s]/g, '\u00a0')
}

/** Distance arrondie pour la lecture : « 2 300 km », « 85 km ». */
export function formatKm(km: number): string {
  const r = km >= 1000 ? Math.round(km / 100) * 100 : km >= 100 ? Math.round(km / 10) * 10 : Math.round(km)
  return formatNumber(r) + '\u00a0km'
}

/**
 * Typographie française à l'affichage : espace insécable dans les guillemets et avant « : ; ? ! »,
 * pour qu'un « » ou un deux-points ne se retrouve jamais seul en début de ligne.
 */
export function typo(s: string): string {
  return s
    .replace(/«\s+/g, '«\u00a0')
    .replace(/\s+»/g, '\u00a0»')
    .replace(/\s+([:;?!])/g, '\u00a0$1')
}

/** Notes de maintenance de Wikipédia (« [réf. nécessaire] », « [Quand ?] »…) : du bruit, pas du contenu. */
const WIKI_MARKERS =
  /\s*\[(?:réf\.[^\]]*|Quand\s?\?|Qui\s?\?|Lequel\s?\?|Laquelle\s?\?|Selon qui\s?\?|Combien\s?\?|Où\s?\?|pas clair|source insuffisante|à vérifier|précision nécessaire|Passage contradictoire|interprétation personnelle|non neutre|style à revoir)\]/g

/**
 * Citation de source, à l'affichage seulement (la donnée reste exacte pour le contrôle des faits) :
 * les titres de section wiki (« == Symbolisme == ») sont retirés, les sauts de ligne simples deviennent
 * des espaces, les lignes vides séparent des paragraphes. Une citation qui n'était qu'un titre affiche
 * ce titre sans les « = ».
 */
export function displayQuote(q: string): string[] {
  const heads: string[] = []
  const kept = q
    .replace(WIKI_MARKERS, '')
    .split('\n')
    .map((line) => {
      // Titre de section, y compris coupé en fin de citation (« === Présidence de… » sans les « = » de fin).
      if (/^\s*={2,}\s*[^=\s]/.test(line)) {
        heads.push(line.replace(/^\s*=+|=+\s*$/g, '').trim())
        return ''
      }
      return line
    })
  const paras = kept
    .join('\n')
    .split(/\n\s*\n/)
    .map((para) => para.replace(/\s+/g, ' ').trim())
    .filter(Boolean)
  if (paras.length) return paras
  if (heads.length) return [heads.join(', ')]
  return [q.trim()]
}
