// État de l'encre de chaque pays, déduit des cartes de révision.
import { cardKey } from './questions'
import { freshness, isDue, isMastered, type Card } from './scheduler'
import type { Country, Mode } from './types'
import { MODES } from './types'

export type ModeState = 'maitrise' | 'a-revoir' | 'efface' | 'jamais'

export interface Ink {
  /** nombre de modes maîtrisés : 0 à 3 (contour, lavis, nom) */
  level: number
  /** 1 = encre neuve ; plus bas = l'encre passe (révision due) */
  fade: number
  /** déjà su puis raté : trace effacée */
  ghost: boolean
  modes: Record<Mode, ModeState>
}

export function modeState(c: Card | undefined, now: number): ModeState {
  if (!c || c.seen === 0) return 'jamais'
  if (!isMastered(c)) return 'efface'
  return isDue(c, now) ? 'a-revoir' : 'maitrise'
}

export function inkOf(id: string, cards: Record<string, Card>, now: number): Ink {
  const modes = {} as Record<Mode, ModeState>
  let level = 0
  let fadeSum = 0
  let ghost = false
  for (const m of MODES) {
    const c = cards[cardKey(m, id)]
    modes[m] = modeState(c, now)
    if (isMastered(c)) {
      level++
      fadeSum += freshness(c, now)
    } else if (c && c.seen > 0 && c.reps === 0 && (c.lapses > 0 || c.seen > 0)) ghost = true
  }
  return { level, fade: level ? fadeSum / level : 1, ghost: level === 0 && ghost, modes }
}

export function inkMap(countries: Country[], cards: Record<string, Card>, now: number): Map<string, Ink> {
  return new Map(countries.map((c) => [c.id, inkOf(c.id, cards, now)]))
}

export interface AtlasCounts {
  inkedStates: number
  totalStates: number
  inkedTerritories: number
  toReview: number
}

export function atlasCounts(countries: Country[], inks: Map<string, Ink>): AtlasCounts {
  let inkedStates = 0
  let totalStates = 0
  let inkedTerritories = 0
  let toReview = 0
  for (const c of countries) {
    if (c.quizzable === false) continue
    const ink = inks.get(c.id)
    if (c.kind === 'etat') totalStates++
    if (ink && ink.level > 0) {
      if (c.kind === 'etat') inkedStates++
      else inkedTerritories++
    }
    if (ink && Object.values(ink.modes).some((m) => m === 'a-revoir' || m === 'efface')) toReview++
  }
  return { inkedStates, totalStates, inkedTerritories, toReview }
}
