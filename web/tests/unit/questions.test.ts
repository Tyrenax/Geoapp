import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'
import type { Topology } from 'topojson-specification'
import { normalizeSimilar, type Dataset } from '../../src/lib/data'
import {
  answerPool,
  buildSession,
  distractors,
  eligible,
  judgeText,
  placeToleranceKm,
  type Question,
} from '../../src/lib/questions'
import { newCard } from '../../src/lib/scheduler'
import { defaultState } from '../../src/lib/store'
import type { Country } from '../../src/lib/types'

const fx = (p: string) => JSON.parse(readFileSync(new URL(`../../fixtures/${p}`, import.meta.url), 'utf8'))
const countries: Country[] = fx('countries.json')
const ds: Dataset = {
  base: 'fixtures/',
  isFixture: true,
  countries,
  byId: new Map(countries.map((c) => [c.id, c])),
  world: fx('world.topo.json') as Topology,
  similar: normalizeSimilar(fx('flag_similar.json')),
}
const seq = (...xs: number[]) => {
  let i = 0
  return () => xs[i++ % xs.length]
}

describe('distracteurs', () => {
  it('même sous-région en priorité', () => {
    const bol = ds.byId.get('BOL')!
    const d = distractors(ds, bol, 'carte', answerPool(ds, 'carte', false), seq(0.3, 0.7, 0.1))
    expect(d).toHaveLength(3)
    expect(d.every((c) => c.subregion_fr === 'Amérique du Sud')).toBe(true)
    expect(d.map((c) => c.id)).not.toContain('BOL')
  })
  it('usage : les entités déjà proposées dans la session cèdent la place', () => {
    const bol = ds.byId.get('BOL')!
    const pool = answerPool(ds, 'carte', false)
    const first = distractors(ds, bol, 'carte', pool, seq(0.3, 0.7, 0.1))
    const usage = new Map(first.map((c) => [c.id, 1]))
    const sameTier = pool.filter((c) => c.id !== 'BOL' && c.subregion_fr === 'Amérique du Sud').length
    const second = distractors(ds, bol, 'carte', pool, seq(0.3, 0.7, 0.1), 3, usage)
    const reused = second.filter((c) => usage.has(c.id)).length
    expect(reused).toBe(Math.max(0, 3 - (sameTier - 3)))
  })
  it('drapeaux : les sosies passent avant la région', () => {
    const extra: Country = {
      ...ds.byId.get('ITA')!,
      id: 'MEX',
      name_fr: 'Mexique',
      continent: 'amerique-nord',
      subregion_fr: 'Amérique centrale',
    }
    const pool = [...answerPool(ds, 'drapeau', false), extra]
    const d = distractors(ds, ds.byId.get('ITA')!, 'drapeau', pool, seq(0.5))
    expect(d[0].id).toBe('MEX')
  })
  it('territoires exclus par défaut, inclus sur demande', () => {
    expect(answerPool(ds, 'carte', false).some((c) => c.id === 'GRL')).toBe(false)
    expect(answerPool(ds, 'carte', true).some((c) => c.id === 'GRL')).toBe(true)
  })
  it('capitales : pas deux fois le même nom', () => {
    const d = distractors(ds, ds.byId.get('BOL')!, 'capitale', answerPool(ds, 'capitale', false))
    const names = d.map((c) => c.quiz_capital)
    expect(new Set(names).size).toBe(names.length)
    expect(names).not.toContain('Sucre')
  })
})

describe('éligibilité', () => {
  it('quizzable:false jamais posé, flag_quizzable:false jamais en drapeau', () => {
    const ata = { ...ds.byId.get('FRA')!, id: 'ATA', quizzable: false }
    const hmd = { ...ds.byId.get('FRA')!, id: 'HMD', flag_quizzable: false }
    expect(eligible(ds, ata, 'carte')).toBe(false)
    expect(eligible(ds, hmd, 'drapeau')).toBe(false)
    expect(eligible(ds, hmd, 'carte')).toBe(true)
  })
  it('le Vatican (sans géométrie 110m) reste posable en carte grâce à son label', () => {
    expect(eligible(ds, ds.byId.get('VAT')!, 'carte')).toBe(true)
  })
})

describe('session', () => {
  it('15 questions au plus, filtres respectés, pas de territoire par défaut', () => {
    const s = { ...defaultState().settings, mode: 'tout' as const }
    const qs = buildSession(ds, s, {}, Date.now())
    // un pays par question : le jeu de test n'a que 13 États
    const states = ds.countries.filter((c) => c.kind === 'etat' && c.quizzable !== false).length
    expect(qs.length).toBe(Math.min(15, states))
    expect(qs.some((q) => q.target.id === 'GRL')).toBe(false)
    expect(new Set(qs.map((q) => q.key)).size).toBe(qs.length)
    expect(new Set(qs.map((q) => q.target.id)).size).toBe(qs.length) // jamais deux fois le même pays
    for (const q of qs) expect(q.choices.map((c) => c.id)).toContain(q.target.id)
  })
  it('jamais deux fois le même pays, même quand toutes ses cartes sont dues', () => {
    const s = { ...defaultState().settings, mode: 'tout' as const }
    const t = Date.now()
    const cards = Object.fromEntries(
      ds.countries.flatMap((c) =>
        ['carte', 'drapeau', 'capitale'].map((m) => [`${m}:${c.id}`, { ...newCard(`${m}:${c.id}`), seen: 1, due: t - 1000 }]),
      ),
    )
    for (let i = 0; i < 50; i++) {
      const qs = buildSession(ds, s, cards, t)
      expect(new Set(qs.map((q) => q.target.id)).size).toBe(qs.length)
    }
  })
  it('filtre de continent', () => {
    const s = { ...defaultState().settings, continents: ['europe' as const] }
    const qs = buildSession(ds, s, {}, Date.now())
    expect(qs.length).toBeGreaterThan(0)
    expect(qs.every((q) => q.target.continent === 'europe')).toBe(true)
  })
})

describe('réponses', () => {
  const q = (variant: Question['variant'], id: string): Question => ({
    key: 'x',
    mode: 'capitale',
    variant,
    target: ds.byId.get(id)!,
    answer: 'saisie',
    choices: [],
  })
  const pool = answerPool(ds, 'capitale', true)
  it('Bolivie : les deux capitales sont justes', () => {
    expect(judgeText(ds, q('pays-capitale', 'BOL'), 'sucre', pool)).toBe('exact')
    expect(judgeText(ds, q('pays-capitale', 'BOL'), 'la paz', pool)).toBe('exact')
    expect(judgeText(ds, q('pays-capitale', 'BOL'), 'Lima', pool)).toBe('faux')
  })
  it('alias et fautes', () => {
    expect(judgeText(ds, q('pays-capitale', 'LKA'), 'Sri Jayawardenapura Kotte', pool)).toBe('proche')
    expect(judgeText(ds, q('pays-capitale', 'PRY'), 'Asunción', pool)).toBe('exact')
    expect(judgeText(ds, q('capitale-pays', 'KNA'), 'Saint-Kitts-et-Nevis', pool)).toBe('exact')
  })
  it('tolérance de placement bornée', () => {
    expect(placeToleranceKm(ds.byId.get('VAT')!)).toBe(100)
    expect(placeToleranceKm(ds.byId.get('BRA')!)).toBe(500)
  })
})
