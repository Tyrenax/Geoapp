import { describe, expect, it } from 'vitest'
import {
  DAY,
  RELEARN,
  freshness,
  isDue,
  isMastered,
  newCard,
  pickSession,
  review,
} from '../../src/lib/scheduler'

const T0 = Date.UTC(2026, 9, 12)

describe('review', () => {
  it('juste : 1 j, puis 3 j, puis × facilité', () => {
    let c = review(newCard('carte:BOL'), 'juste', T0)
    expect(c.interval).toBe(1)
    expect(c.due).toBe(T0 + DAY)
    expect(isMastered(c)).toBe(true)
    c = review(c, 'juste', T0 + DAY)
    expect(c.interval).toBe(3)
    c = review(c, 'juste', T0 + 4 * DAY)
    expect(c.interval).toBe(8) // round(3 × 2,5)
    expect(c.reps).toBe(3)
  })
  it('faux : retour à zéro, revue dans 10 min, facilité réduite, pas en dessous de 1,3', () => {
    let c = review(review(newCard('k'), 'juste', T0), 'faux', T0 + DAY)
    expect(c.reps).toBe(0)
    expect(c.lapses).toBe(1)
    expect(c.due).toBe(T0 + DAY + RELEARN)
    expect(c.ease).toBeCloseTo(2.3)
    expect(isMastered(c)).toBe(false)
    for (let i = 0; i < 10; i++) c = review(c, 'faux', T0)
    expect(c.ease).toBe(1.3)
  })
  it('difficile : intervalle plus court que juste', () => {
    const base = review(review(newCard('k'), 'juste', T0), 'juste', T0)
    const good = review(base, 'juste', T0)
    const hard = review(base, 'difficile', T0)
    expect(hard.interval).toBeLessThan(good.interval)
    expect(hard.ease).toBeLessThan(good.ease)
  })
  it("l'intervalle croît toujours", () => {
    let c = newCard('k')
    let last = 0
    for (let i = 0; i < 8; i++) {
      c = review(c, 'difficile', T0)
      expect(c.interval).toBeGreaterThan(last)
      last = c.interval
    }
  })
})

describe('freshness', () => {
  it("1 avant l'échéance, décroît après, plancher 0,3", () => {
    const c = review(newCard('k'), 'juste', T0) // intervalle 1 j
    expect(freshness(c, T0 + DAY / 2)).toBe(1)
    const f1 = freshness(c, T0 + 2 * DAY)
    expect(f1).toBeLessThan(1)
    expect(f1).toBeGreaterThan(0.3)
    expect(freshness(c, T0 + 100 * DAY)).toBe(0.3)
    expect(isDue(c, T0 + 2 * DAY)).toBe(true)
  })
})

describe('pickSession', () => {
  it('dues (les plus en retard) puis nouvelles, taille bornée', () => {
    const cards = {
      a: { ...newCard('a'), seen: 1, due: T0 - 5 * DAY },
      b: { ...newCard('b'), seen: 1, due: T0 - DAY },
      c: { ...newCard('c'), seen: 1, due: T0 + DAY },
    }
    const keys = ['c', 'b', 'a', 'n1', 'n2', 'n3']
    const p = pickSession(keys, cards, T0, 4)
    expect(p.map((x) => x.key)).toEqual(['a', 'b', 'n1', 'n2'])
    expect(p.filter((x) => x.isNew).length).toBe(2)
  })
  it('complète avec les cartes vues si les nouvelles manquent', () => {
    const cards = { c: { ...newCard('c'), seen: 1, due: T0 + DAY } }
    expect(pickSession(['c', 'n'], cards, T0, 15).map((x) => x.key)).toEqual(['n', 'c'])
  })
  it('au plus maxDue dues avant les nouvelles', () => {
    const cards = Object.fromEntries(
      Array.from({ length: 20 }, (_, i) => [`d${i}`, { ...newCard(`d${i}`), seen: 1, due: T0 - i }]),
    )
    const keys = [...Object.keys(cards), 'n1', 'n2']
    const p = pickSession(keys, cards, T0, 15, 10)
    expect(p.length).toBe(15)
    expect(p.filter((x) => x.isNew).length).toBe(2)
  })
  it('une seule carte par entité', () => {
    const cards = { 'carte:FRA': { ...newCard('carte:FRA'), seen: 1, due: T0 - DAY } }
    const keys = ['carte:FRA', 'capitale:FRA', 'drapeau:FRA', 'capitale:ITA']
    const p = pickSession(keys, cards, T0, 15, 10, (k) => k.split(':')[1])
    expect(p.map((x) => x.key)).toEqual(['carte:FRA', 'capitale:ITA'])
  })
  it('bouche-trou : les cartes vues il y a peu passent en dernier', () => {
    const cards = {
      r: { ...newCard('r'), seen: 1, due: T0 + DAY, last: T0 - 60_000 },
      v: { ...newCard('v'), seen: 1, due: T0 + 3 * DAY, last: T0 - 2 * DAY },
    }
    expect(pickSession(['r', 'v'], cards, T0, 15).map((x) => x.key)).toEqual(['v', 'r'])
  })
})
