// Formats du contrat (docs/ARCHITECTURE.md). Les champs absents du contrat sont optionnels.

export type Continent =
  | 'afrique'
  | 'amerique-nord'
  | 'amerique-sud'
  | 'asie'
  | 'europe'
  | 'oceanie'
  | 'antarctique'

export interface Capital {
  name_fr: string
  role_fr?: string | null
  qid?: string
  lat: number
  lon: number
  aliases_fr?: string[]
  wiki_fr?: string
}

export interface Country {
  id: string
  iso2?: string
  qid?: string
  kind: 'etat' | 'territoire'
  sovereign?: string | null
  status_fr?: string | null
  name_fr: string
  name_official_fr?: string
  article_fr?: string
  aliases_fr?: string[]
  continent: Continent
  subregion_fr?: string
  capitals: Capital[]
  quiz_capital?: string | null
  /** quand il n'y a pas de capitale (Antarctique, Hong Kong…) */
  capital_note_fr?: string | null
  population?: number | null
  population_year?: number | null
  area_km2?: number | null
  label?: { lat: number; lon: number } | null
  small?: boolean
  neighbors?: string[]
  wiki_fr?: string
  wiki_en?: string
  flag?: string | null
  flag_wiki_fr?: string
  flag_quizzable?: boolean
  flag_shared_with?: string | null
  /** note à afficher sous le drapeau dans la fiche (drapeau partagé, disputé…) */
  flag_note_fr?: string | null
  quizzable?: boolean
  // Carte d'identité (tous facultatifs : null = inconnu ou sans objet)
  /** code international des véhicules (ovale de la Convention de Vienne) */
  plate_code?: string | string[] | null
  driving_side?: 'droite' | 'gauche' | null
  currencies?: { code?: string | null; name_fr: string; symbol?: string | null }[] | null
  languages_fr?: string[] | null
  demonym_fr?: string | null
  calling_code?: string | string[] | null
  tld?: string | string[] | null
  highest_point?: { name_fr: string; elevation_m?: number | null } | null
  motto_fr?: string | null
}

export interface Source {
  url: string
  quote?: string
}

export interface Fact {
  id: string
  topic?: string
  era?: string
  title: string
  short: string
  long?: string
  sources: Source[]
}

export interface FactsFile {
  id: string
  facts: Fact[]
  capital_facts?: Fact[]
  tips?: { position?: string; flag?: string; capital?: string }
}

/** Drapeaux non rectangulaires : affichés sans filet d'encre autour. */
export const NON_RECT = new Set(['NPL'])

/** Les trois modes de révision : une carte de révision par couple (entité, mode). */
export type Mode = 'carte' | 'drapeau' | 'capitale'
export const MODES: Mode[] = ['carte', 'drapeau', 'capitale']

export type Variant =
  | 'carte-ou' // « Où est la Bolivie ? » → clic
  | 'carte-nommer' // pays surligné → le nommer
  | 'drapeau-nom' // drapeau → nom
  | 'nom-drapeau' // nom → choisir parmi 4 drapeaux
  | 'pays-capitale'
  | 'capitale-pays'
  | 'placer-capitale'

export type AnswerStyle = 'choix' | 'saisie'

/** Cible d'une question. Phase 2 : `{ kind: 'ville', id }`. */
export interface Target {
  kind: 'pays'
  id: string
}
