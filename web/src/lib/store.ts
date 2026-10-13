// Progression en localStorage (try/catch partout : le jeu marche sans, la progression est alors perdue
// à la fermeture de l'onglet).
import type { Card } from './scheduler'
import type { AnswerStyle, Continent } from './types'

export type SessionMode = 'carte' | 'drapeau' | 'capitale' | 'tout'

export interface Settings {
  mode: SessionMode
  answer: AnswerStyle
  continents: Continent[]
  territories: boolean
  /** sons discrets ; coupés par défaut */
  sound?: boolean
}

export interface SaveState {
  version: 1
  cards: Record<string, Card>
  /** id du fait → date de découverte (ms) */
  facts: Record<string, number>
  settings: Settings
}

export const ALL_CONTINENTS: Continent[] = [
  'afrique',
  'amerique-nord',
  'amerique-sud',
  'asie',
  'europe',
  'oceanie',
]

export const CONTINENT_FR: Record<Continent, string> = {
  afrique: 'Afrique',
  'amerique-nord': 'Amérique du Nord',
  'amerique-sud': 'Amérique du Sud',
  asie: 'Asie',
  europe: 'Europe',
  oceanie: 'Océanie',
  antarctique: 'Antarctique',
}

const KEY = 'geo-atlas.v1'

export function defaultState(): SaveState {
  return {
    version: 1,
    cards: {},
    facts: {},
    settings: { mode: 'carte', answer: 'choix', continents: [...ALL_CONTINENTS], territories: false },
  }
}

export function loadState(): SaveState {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return defaultState()
    const s = JSON.parse(raw) as Partial<SaveState>
    const d = defaultState()
    return {
      version: 1,
      cards: s.cards ?? d.cards,
      facts: s.facts ?? d.facts,
      settings: { ...d.settings, ...(s.settings ?? {}) },
    }
  } catch {
    return defaultState()
  }
}

export function saveState(s: SaveState): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(s))
  } catch {
    /* stockage indisponible : on continue sans */
  }
}
