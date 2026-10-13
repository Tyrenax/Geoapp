import { describe, expect, it } from 'vitest'
import { complete, deArticle, formatKm, judge, levenshtein, normalize, withArticle } from '../../src/lib/text'

describe('normalize', () => {
  it('ignore accents, casse, tirets, apostrophes et article', () => {
    expect(normalize("L'Île-Maurice")).toBe('ile maurice')
    expect(normalize('  BRÉSIL ')).toBe('bresil')
    expect(normalize('Saint-Christophe-et-Niévès')).toBe('saint christophe et nieves')
    expect(normalize('les Comores')).toBe('comores')
    expect(normalize('Côte d’Ivoire')).toBe('cote d ivoire')
  })
})

describe('judge', () => {
  it('accepte la forme exacte et les alias', () => {
    expect(judge('bresil', ['Brésil'])).toBe('exact')
    expect(judge('Ceylan', ['Sri Lanka', 'Ceylan'])).toBe('exact')
    expect(judge('saint kitts et nevis', ['Saint-Christophe-et-Niévès', 'Saint-Kitts-et-Nevis'])).toBe('exact')
  })
  it('tolère une petite faute selon la longueur', () => {
    expect(levenshtein('bolivie', 'bolovie')).toBe(1)
    expect(judge('Bolovie', ['Bolivie'])).toBe('proche')
    expect(judge('Argentinne', ['Argentine'])).toBe('proche')
    expect(judge('Copenhagu', ['Copenhague'])).toBe('proche')
    expect(judge('Perou', ['Pérou'])).toBe('exact')
  })
  it('pas de tolérance pour les mots courts', () => {
    expect(judge('Lyma', ['Lima'])).toBe('faux')
    expect(judge('Iram', ['Iran'])).toBe('faux')
  })
  it("refuse le nom exact d'une autre réponse, même proche", () => {
    expect(judge('Niger', ['Nigeria'], ['Niger'])).toBe('faux')
    expect(judge('Nigeria', ['Niger'], ['Nigeria'])).toBe('faux')
    expect(judge('Autriche', ['Australie'], ['Autriche'])).toBe('faux')
    // une faute plus proche d'une autre réponse que de la bonne est fausse
    expect(judge('Slovenie', ['Slovaquie'], ['Slovénie'])).toBe('faux')
  })
  it('vide = faux', () => {
    expect(judge('  ', ['France'])).toBe('faux')
  })
})

describe('complete', () => {
  const items = [
    { label: 'Guinée', value: 'GIN' },
    { label: 'Guinée-Bissau', value: 'GNB' },
    { label: 'Guinée équatoriale', value: 'GNQ' },
    { label: 'Papouasie-Nouvelle-Guinée', value: 'PNG' },
    { label: 'Saint-Kitts-et-Nevis', value: 'KNA' },
    { label: 'Saint-Christophe-et-Niévès', value: 'KNA' },
  ]
  it('préfixe, puis début de mot, insensible aux accents', () => {
    expect(complete('guinee', items).map((s) => s.value)).toEqual(['GIN', 'GNB', 'GNQ', 'PNG'])
    expect(complete('equa', items).map((s) => s.value)).toEqual(['GNQ'])
  })
  it('une seule entrée par réponse', () => {
    expect(complete('saint', items).map((s) => s.value)).toEqual(['KNA'])
  })
  it('vide = rien', () => {
    expect(complete('', items)).toEqual([])
  })
})

describe('articles et nombres', () => {
  it('construit « la Bolivie », « du Pérou », « de l’Italie »', () => {
    expect(withArticle('la', 'Bolivie')).toBe('la Bolivie')
    expect(withArticle("l'", 'Italie')).toBe("l'Italie")
    expect(deArticle('le', 'Pérou')).toBe('du Pérou')
    expect(deArticle("l'", 'Italie')).toBe("de l'Italie")
    expect(deArticle('les', 'Fidji')).toBe('des Fidji')
    expect(deArticle('', 'Saint-Christophe-et-Niévès')).toBe('de Saint-Christophe-et-Niévès')
  })
  it('arrondit les distances', () => {
    expect(formatKm(2287).replace(/\s/g, ' ')).toBe('2 300 km')
    expect(formatKm(84.6).replace(/\s/g, ' ')).toBe('85 km')
  })
})

describe('typo', () => {
  it('insécables dans les guillemets et avant la ponctuation double', async () => {
    const { typo } = await import('../../src/lib/text')
    expect(typo('le mot « pays » : oui ; non ? ah !')).toBe('le mot «\u00a0pays\u00a0»\u00a0: oui\u00a0; non\u00a0? ah\u00a0!')
  })
})

describe('displayQuote', () => {
  it('retire les titres de section wiki et garde les paragraphes', async () => {
    const { displayQuote } = await import('../../src/lib/text')
    const q = 'Ce drapeau fut adopté le 25 novembre 1975.\n\n\n== Composition du drapeau ==\n\nAu centre du drapeau'
    expect(displayQuote(q)).toEqual(['Ce drapeau fut adopté le 25 novembre 1975.', 'Au centre du drapeau'])
  })
  it('titre en tête, saut de ligne simple → espace', async () => {
    const { displayQuote } = await import('../../src/lib/text')
    const q = '=== Présidence Ian Khama (2008-2018) ===\nIl laisse le pouvoir au vice-président,\nIan Khama'
    expect(displayQuote(q)).toEqual(['Il laisse le pouvoir au vice-président, Ian Khama'])
  })
  it("une citation qui n'est qu'un titre affiche le titre sans les =", async () => {
    const { displayQuote } = await import('../../src/lib/text')
    expect(displayQuote('==== Présidence de Sékou Touré (1958-1984) ====')).toEqual([
      'Présidence de Sékou Touré (1958-1984)',
    ])
    expect(
      displayQuote("=== L'indépendance et le régime de Houphouët-Boigny ===\n\n\n==== Miracle ivoirien ===="),
    ).toEqual(["L'indépendance et le régime de Houphouët-Boigny, Miracle ivoirien"])
  })
  it('laisse intacts les « = » dans le texte, retire les notes de maintenance wiki', async () => {
    const { displayQuote } = await import('../../src/lib/text')
    expect(displayQuote('E = mc2 [réf. nécessaire] et 1 = 1')).toEqual(['E = mc2 et 1 = 1'])
    expect(displayQuote('une présence juive se maintient[réf. nécessaire], tout comme [Quand ?] celle')).toEqual([
      'une présence juive se maintient, tout comme celle',
    ])
  })
  it('retire un titre coupé en fin de citation (sans les = de fermeture)', async () => {
    const { displayQuote } = await import('../../src/lib/text')
    expect(displayQuote("=== Présidence de Corazon Aquino (1986-1992)\nLe 25 février 1986, Aquino")).toEqual([
      'Le 25 février 1986, Aquino',
    ])
  })
})
