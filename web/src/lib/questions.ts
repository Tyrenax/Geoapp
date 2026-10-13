// Générateurs de questions par mode, distracteurs, formes justes.
// Phase 2 (autres villes) : ajouter un générateur et une clé de carte « ville:<qid> » ; le reste ne bouge pas.
import type { Dataset } from './data'
import { pickSession, type Card } from './scheduler'
import type { Settings } from './store'
import type { AnswerStyle, Country, Mode, Variant } from './types'
import { MODES } from './types'
import { judge, type Suggestion, type Verdict } from './text'

export type Rand = () => number

export interface Question {
  key: string // carte de révision, « capitale:BOL »
  mode: Mode
  variant: Variant
  target: Country
  answer: AnswerStyle
  /** quatre entités, cible comprise, dans l'ordre d'affichage (choix multiples et planche de drapeaux) */
  choices: Country[]
}

export const cardKey = (mode: Mode, id: string) => `${mode}:${id}`
export const parseKey = (key: string) => {
  const [mode, id] = key.split(':')
  return { mode: mode as Mode, id }
}
/** Une série ne pose jamais deux fois la même entité, même dans des modes différents. */
const entityOf = (key: string) => parseKey(key).id

export function hasGeometry(ds: Dataset, id: string): boolean {
  return geometryIds(ds).has(id)
}

const geomCache = new WeakMap<Dataset, Set<string>>()
export function geometryIds(ds: Dataset): Set<string> {
  let s = geomCache.get(ds)
  if (!s) {
    const obj = ds.world.objects.countries as { geometries?: { id?: string | number; properties?: { id?: string } }[] }
    s = new Set((obj.geometries ?? []).map((g) => String(g.properties?.id ?? g.id ?? '')))
    geomCache.set(ds, s)
  }
  return s
}

/** L'entité peut-elle être posée dans ce mode (indépendamment des filtres) ? */
export function eligible(ds: Dataset, c: Country, mode: Mode): boolean {
  if (c.quizzable === false) return false
  if (mode === 'carte') return !!c.label || hasGeometry(ds, c.id)
  if (mode === 'drapeau') return !!c.flag && c.flag_quizzable !== false
  return c.capitals.length > 0 && !!c.quiz_capital
}

export function inFilters(c: Country, s: Pick<Settings, 'continents' | 'territories'>): boolean {
  return s.continents.includes(c.continent) && (s.territories || c.kind === 'etat')
}

export function modesOf(s: Settings): Mode[] {
  return s.mode === 'tout' ? MODES : [s.mode]
}

/** Ordre des nouvelles : les pays les plus peuplés (les plus connus) ont plus de chances de sortir tôt, mais le hasard domine. */
function newPriority(c: Country, rand: Rand): number {
  return Math.log10((c.population ?? 1000) + 10) + rand() * 4
}

export function sessionKeys(ds: Dataset, s: Settings, rand: Rand = Math.random): string[] {
  const pool = ds.countries.filter((c) => inFilters(c, s))
  const keys: { k: string; p: number }[] = []
  for (const m of modesOf(s))
    for (const c of pool) if (eligible(ds, c, m)) keys.push({ k: cardKey(m, c.id), p: newPriority(c, rand) })
  keys.sort((a, b) => b.p - a.p)
  return keys.map((x) => x.k)
}

export interface SessionPreview {
  due: number
  fresh: number
  total: number
  eligible: number
}

export function previewSession(ds: Dataset, s: Settings, cards: Record<string, Card>, now: number): SessionPreview {
  const keys = sessionKeys(ds, s, () => 0.5)
  const picks = pickSession(keys, cards, now, 15, 10, entityOf)
  return {
    due: picks.filter((p) => !p.isNew && (cards[p.key]?.due ?? 0) <= now).length,
    fresh: picks.filter((p) => p.isNew).length,
    total: picks.length,
    eligible: keys.length,
  }
}

function shuffle<T>(a: T[], rand: Rand): T[] {
  const b = [...a]
  for (let i = b.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1))
    ;[b[i], b[j]] = [b[j], b[i]]
  }
  return b
}

export function chooseVariant(ds: Dataset, mode: Mode, c: Country, rand: Rand): Variant {
  const r = rand()
  if (mode === 'carte') return r < 0.6 ? 'carte-ou' : 'carte-nommer'
  if (mode === 'drapeau') return r < 0.6 ? 'drapeau-nom' : 'nom-drapeau'
  const canPlace = !!capitalOf(c) && (hasGeometry(ds, c.id) || !!c.label)
  if (r < 0.5 || (!canPlace && r < 0.75)) return 'pays-capitale'
  if (r < 0.75 || !canPlace) return 'capitale-pays'
  return 'placer-capitale'
}

/** Pool des réponses possibles pour un mode (toutes régions, pour ne pas trahir les filtres). */
export function answerPool(ds: Dataset, mode: Mode, territories: boolean): Country[] {
  return ds.countries.filter((c) => eligible(ds, c, mode) && (territories || c.kind === 'etat'))
}

/**
 * Trois distracteurs plausibles : sosies de drapeau (mode drapeau), puis même sous-région, puis voisins,
 * puis même continent, puis le reste. Pour les capitales, les noms de capitale doivent différer.
 * `usage` (fois où chaque entité a déjà été proposée dans la session) fait tourner les choix d'un même palier.
 */
export function distractors(
  ds: Dataset,
  target: Country,
  mode: Mode,
  pool: Country[],
  rand: Rand = Math.random,
  n = 3,
  usage?: Map<string, number>,
): Country[] {
  const candidates = pool.filter((c) => c.id !== target.id)
  const tiers: Country[][] = []
  if (mode === 'drapeau') {
    const sim = new Set(ds.similar.get(target.id) ?? [])
    tiers.push(candidates.filter((c) => sim.has(c.id)))
  }
  const nb = new Set(target.neighbors ?? [])
  tiers.push(candidates.filter((c) => c.subregion_fr && c.subregion_fr === target.subregion_fr))
  tiers.push(candidates.filter((c) => nb.has(c.id)))
  tiers.push(candidates.filter((c) => c.continent === target.continent))
  tiers.push(candidates)
  const out: Country[] = []
  const used = new Set<string>([target.id])
  const capNames = new Set<string>([target.quiz_capital ?? ''])
  for (const tier of tiers) {
    const order = shuffle(tier, rand)
    if (usage) order.sort((a, b) => (usage.get(a.id) ?? 0) - (usage.get(b.id) ?? 0))
    for (const c of order) {
      if (out.length >= n) return out
      if (used.has(c.id)) continue
      if (mode === 'capitale') {
        if (!c.quiz_capital || capNames.has(c.quiz_capital)) continue
        capNames.add(c.quiz_capital)
      }
      used.add(c.id)
      out.push(c)
    }
  }
  return out
}

export function buildQuestion(
  ds: Dataset,
  key: string,
  s: Settings,
  rand: Rand = Math.random,
  usage?: Map<string, number>,
): Question | null {
  const { mode, id } = parseKey(key)
  const target = ds.byId.get(id)
  if (!target) return null
  const variant = chooseVariant(ds, mode, target, rand)
  const pool = answerPool(ds, mode, s.territories)
  const choices = shuffle([target, ...distractors(ds, target, mode, pool, rand, 3, usage)], rand)
  return { key, mode, variant, target, answer: s.answer, choices }
}

export function buildSession(
  ds: Dataset,
  s: Settings,
  cards: Record<string, Card>,
  now: number,
  rand: Rand = Math.random,
  size = 15,
): Question[] {
  // ordre entièrement mélangé : dues et nouvelles alternent au hasard
  const picks = shuffle(pickSession(sessionKeys(ds, s, rand), cards, now, size, 10, entityOf), rand)
  const usage = new Map<string, number>()
  const out: Question[] = []
  for (const p of picks) {
    const q = buildQuestion(ds, p.key, s, rand, usage)
    if (!q) continue
    for (const c of q.choices) usage.set(c.id, (usage.get(c.id) ?? 0) + 1)
    out.push(q)
  }
  return out
}

export function capitalOf(c: Country) {
  return c.capitals.find((k) => k.name_fr === c.quiz_capital) ?? c.capitals[0]
}

export function nameForms(c: Country): string[] {
  return [c.name_fr, ...(c.aliases_fr ?? []), ...(c.name_official_fr ? [c.name_official_fr] : [])]
}

export function capitalForms(c: Country): string[] {
  return c.capitals.flatMap((k) => [k.name_fr, ...(k.aliases_fr ?? [])])
}

/** Ce que la question attend en saisie : un nom de pays ou un nom de capitale. */
export function expects(q: Question): 'pays' | 'capitale' | null {
  if (q.variant === 'pays-capitale') return 'capitale'
  if (q.variant === 'drapeau-nom' || q.variant === 'carte-nommer' || q.variant === 'capitale-pays') return 'pays'
  return null
}

export function judgeText(ds: Dataset, q: Question, input: string, pool: Country[]): Verdict {
  const others = pool.filter((c) => c.id !== q.target.id)
  if (expects(q) === 'capitale') {
    // Une capitale homonyme d'une autre entité n'est pas fausse si elle figure parmi les formes justes.
    return judge(input, capitalForms(q.target), others.flatMap(capitalForms))
  }
  return judge(input, nameForms(q.target), others.flatMap(nameForms))
}

export function suggestions(pool: Country[], kind: 'pays' | 'capitale'): Suggestion[] {
  if (kind === 'pays')
    return pool.flatMap((c) => [c.name_fr, ...(c.aliases_fr ?? [])].map((label) => ({ label, value: c.id })))
  return pool.flatMap((c) =>
    c.capitals.flatMap((k, i) => [k.name_fr, ...(k.aliases_fr ?? [])].map((label) => ({ label, value: `${c.id}:${i}` }))),
  )
}

/** Tolérance pour « placer la capitale », selon la taille du pays. */
export function placeToleranceKm(c: Country): number {
  const a = c.area_km2 ?? 10000
  return Math.round(Math.min(500, Math.max(100, 0.35 * Math.sqrt(a))))
}
