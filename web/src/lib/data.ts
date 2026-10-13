// Un seul point de chargement : `data/` (généré par le rôle Données) dès qu'il contient countries.json,
// sinon la fixture de dev `fixtures/`. Chemins relatifs : le jeu se sert depuis n'importe quel dossier.
import type { Topology } from 'topojson-specification'
import type { Country, FactsFile } from './types'

export interface Dataset {
  base: string // « data/ » ou « fixtures/ »
  isFixture: boolean
  countries: Country[]
  byId: Map<string, Country>
  world: Topology
  /** id → ids des drapeaux sosies */
  similar: Map<string, string[]>
}

async function fetchJson<T>(url: string): Promise<T | null> {
  try {
    const r = await fetch(url, { cache: 'no-cache' })
    if (!r.ok) return null
    const type = r.headers.get('content-type') ?? ''
    if (type.includes('text/html')) return null // repli SPA du serveur de dev
    return (await r.json()) as T
  } catch {
    return null
  }
}

/** Accepte `[[ids]]`, `[{ids:[…]}]`, `{ID: [ids]}` ou `{ID: [{id}]}`. */
export function normalizeSimilar(raw: unknown): Map<string, string[]> {
  const out = new Map<string, Set<string>>()
  const link = (group: string[]) => {
    for (const a of group)
      for (const b of group) if (a !== b) (out.get(a) ?? out.set(a, new Set()).get(a)!).add(b)
  }
  const ids = (x: unknown): string[] =>
    Array.isArray(x)
      ? x.map((v) => (typeof v === 'string' ? v : (v as { id?: string })?.id)).filter((v): v is string => !!v)
      : []
  if (Array.isArray(raw)) {
    for (const g of raw) {
      if (Array.isArray(g)) link(ids(g))
      else if (g && typeof g === 'object') {
        const o = g as Record<string, unknown>
        link(ids(o.ids ?? o.members ?? o.group ?? o.flags))
      }
    }
  } else if (raw && typeof raw === 'object') {
    for (const [k, v] of Object.entries(raw as Record<string, unknown>)) {
      const g = ids(Array.isArray(v) ? v : (v as Record<string, unknown>)?.similar)
      for (const b of g) {
        ;(out.get(k) ?? out.set(k, new Set()).get(k)!).add(b)
        ;(out.get(b) ?? out.set(b, new Set()).get(b)!).add(k)
      }
    }
  }
  return new Map([...out].map(([k, v]) => [k, [...v]]))
}

export async function loadDataset(): Promise<Dataset> {
  for (const base of ['data/', 'fixtures/']) {
    const countries = await fetchJson<Country[]>(base + 'countries.json')
    if (!Array.isArray(countries) || !countries.length) continue
    const world = await fetchJson<Topology>(base + 'world.topo.json')
    if (!world) throw new Error(`${base}world.topo.json introuvable`)
    const similar = normalizeSimilar(await fetchJson<unknown>(base + 'flag_similar.json'))
    for (const c of countries) {
      c.capitals ??= []
      c.aliases_fr ??= []
    }
    return {
      base,
      isFixture: base === 'fixtures/',
      countries,
      byId: new Map(countries.map((c) => [c.id, c])),
      world,
      similar,
    }
  }
  throw new Error('Aucune donnée : ni data/countries.json ni fixtures/countries.json')
}

const factsCache = new Map<string, Promise<FactsFile | null>>()
const indexCache = new Map<string, Promise<Set<string> | null>>()

/** `facts/index.json` (liste des id qui ont des faits) évite des 404 en console ; facultatif. */
function factsIndex(ds: Dataset): Promise<Set<string> | null> {
  let p = indexCache.get(ds.base)
  if (!p) {
    p = fetchJson<string[]>(`${ds.base}facts/index.json`).then((a) => (Array.isArray(a) ? new Set(a) : null))
    indexCache.set(ds.base, p)
  }
  return p
}

/** Faits d'une entité, chargés à la demande ; `null` si le fichier n'existe pas encore. */
export function loadFacts(ds: Dataset, id: string): Promise<FactsFile | null> {
  const key = ds.base + id
  let p = factsCache.get(key)
  if (!p) {
    p = factsIndex(ds).then((idx) => (idx && !idx.has(id) ? null : fetchJson<FactsFile>(`${ds.base}facts/${id}.json`)))
    factsCache.set(key, p)
  }
  return p
}

export function flagUrl(ds: Dataset, c: Country): string | null {
  if (c.flag) return ds.base + c.flag
  return null
}
