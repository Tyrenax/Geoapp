// Carnet de l'explorateur (demande explicite de Josca) : profil où tous les faits sont découverts.
// Performances, filtres région et thème, recherche d'un pays, renvoi vers la fiche, liens Wikipédia,
// rendu des faits longs, aux trois tailles.
import { expect, test, type Page } from '@playwright/test'
import { check } from './audit-lib'
import { boot, byId, facts, idsWithFacts, watchConsole } from './helpers'
import type { Fact } from '../../src/lib/types'

interface Item {
  fact: Fact
  id: string
  capital: boolean
}
const items: Item[] = idsWithFacts().flatMap((id) => {
  const f = facts(id)!
  return [
    ...f.facts.map((fact) => ({ fact, id, capital: false })),
    ...(f.capital_facts ?? []).map((fact) => ({ fact, id, capital: true })),
  ]
})
const longest = [...items].sort(
  (a, b) => (b.fact.long ?? '').length + b.fact.title.length - ((a.fact.long ?? '').length + a.fact.title.length),
)[0]
const longestTitle = [...items].sort((a, b) => b.fact.title.length - a.fact.title.length)[0]

/** Tous les faits découverts ; le plus long est le plus récent (affiché d'emblée). */
async function seedAll(page: Page) {
  const now = Date.now()
  const found: Record<string, number> = {}
  items.forEach((it, i) => (found[it.fact.id] = now - (i + 1) * 1000))
  if (longest) found[longest.fact.id] = now
  const state = {
    version: 1,
    cards: {},
    facts: found,
    settings: { mode: 'carte', answer: 'choix', continents: ['afrique', 'amerique-nord', 'amerique-sud', 'asie', 'europe', 'oceanie'], territories: false },
  }
  await page.addInitScript((s) => {
    if (!sessionStorage.getItem('seeded')) {
      localStorage.setItem('geo-atlas.v1', JSON.stringify(s))
      sessionStorage.setItem('seeded', '1')
    }
  }, state)
}

async function openCarnet(page: Page) {
  await page.getByRole('button', { name: /Ouvrir le carnet/ }).click()
  await page.locator('.entree').first().waitFor()
}

for (const vp of [
  { width: 1280, height: 720 },
  { width: 1600, height: 900 },
  { width: 1920, height: 1080 },
]) {
  test.describe(`carnet ${vp.width}×${vp.height}`, () => {
    test.use({ viewport: vp })
    test.skip(items.length === 0, 'aucun fait dans les données')

    test('ouverture et défilement fluides, tout est là', async ({ page }) => {
      await seedAll(page)
      await boot(page)
      const t0 = Date.now()
      await openCarnet(page)
      const openMs = Date.now() - t0
      await expect(page.locator('.entree')).toHaveCount(items.length)
      await expect(page.locator('.carnet[role=dialog] .compte')).toContainText(`${items.length} faits découverts`)
      const worst = await page.evaluate(async () => {
        const l = document.querySelector('.liste') as HTMLElement
        let last = performance.now()
        let w = 0
        for (let i = 0; i < 60; i++) {
          l.scrollTop += 500
          await new Promise((r) => requestAnimationFrame(r))
          const t = performance.now()
          w = Math.max(w, t - last)
          last = t
        }
        return w
      })
      const t1 = Date.now()
      await page.locator('.recherche').pressSequentially('royaume', { delay: 0 })
      await expect(page.locator('.compte-filtre')).toBeVisible()
      const typeMs = Date.now() - t1
      console.log(`carnet ${vp.width} : ${items.length} faits, ouverture ${openMs} ms, pire image ${Math.round(worst)} ms, frappe ${typeMs} ms`)
      expect(openMs, 'ouverture').toBeLessThan(2000)
      expect(worst, 'pire image de défilement').toBeLessThan(120)
      expect(typeMs, 'recherche (7 lettres)').toBeLessThan(1500)
    })

    test('filtres région et thème, recherche d’un pays', async ({ page }) => {
      const errs = watchConsole(page)
      await seedAll(page)
      await boot(page)
      await openCarnet(page)
      const count = () => page.locator('.entree').count()

      // continent entier
      const continent = byId.get(items[0].id)!.continent
      await page.locator('select[aria-label="Filtrer par région"]').selectOption(`c:${continent}`)
      expect(await count()).toBe(items.filter((it) => byId.get(it.id)!.continent === continent).length)
      await check(page, `carnet-filtre-continent`)
      // sous-région
      const sub = byId.get(items[0].id)!.subregion_fr
      if (sub) {
        await page.locator('select[aria-label="Filtrer par région"]').selectOption(`r:${sub}`)
        expect(await count()).toBe(items.filter((it) => byId.get(it.id)!.subregion_fr === sub).length)
      }
      await page.locator('select[aria-label="Filtrer par région"]').selectOption('tout')

      // thèmes : histoire, drapeau, capitales
      for (const th of ['histoire', 'drapeau', 'capitale']) {
        const want = items.filter((it) => (th === 'capitale' ? it.capital : it.fact.topic === th)).length
        if (!want) continue
        await page.locator('select[aria-label="Filtrer par thème"]').selectOption(th)
        expect(await count(), `thème ${th}`).toBe(want)
      }
      await check(page, 'carnet-filtre-theme')
      await page.locator('select[aria-label="Filtrer par thème"]').selectOption('tout')

      // chercher un pays (par son nom, sans accent) : tous ses faits sont là, et le premier en fait partie
      const target = byId.get(items.find((it) => /[éèêç]/.test(byId.get(it.id)!.name_fr))?.id ?? items[0].id)!
      const plain = target.name_fr.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
      await page.locator('.recherche').fill(plain)
      const own = items.filter((it) => it.id === target.id).length
      expect(await count()).toBeGreaterThanOrEqual(own)
      // ses propres faits d'abord, avant ceux des pays qui le mentionnent
      const firsts = await page.locator('.entree-pays').evaluateAll((els, k) => els.slice(0, k).map((e) => e.textContent ?? ''), own)
      expect(firsts.every((t) => t.startsWith(target.name_fr))).toBe(true)
      await page.getByRole('radio', { name: 'Pays' }).click()
      await expect(page.locator('.liste h3').first()).toHaveText(target.name_fr)
      await expect(page.locator('.liste h3', { hasText: target.name_fr }).first()).toBeVisible()
      await check(page, 'carnet-recherche-pays')

      // rien ne correspond
      await page.locator('.recherche').fill('zzzzqqq')
      await expect(page.locator('.liste')).toContainText('Rien ne correspond')
      await check(page, 'carnet-vide-recherche')
      expect(errs).toEqual([])
    })

    test('chaque fait renvoie vers sa fiche ; liens Wikipédia et sources', async ({ page, context }) => {
      const errs = watchConsole(page)
      await context.route(/wikipedia\.org/, (r) => r.fulfill({ status: 200, body: 'ok', contentType: 'text/html' }))
      await seedAll(page)
      await boot(page)
      await openCarnet(page)
      // quelques faits répartis dans la liste (premier, milieu, dernier)
      const n = await page.locator('.entree').count()
      for (const i of [0, Math.floor(n / 2), n - 1]) {
        await page.locator('.entree').nth(i).click()
        const country = (await page.locator('.detail .sujet').textContent())!.split(',')[0].trim()
        const [popup] = await Promise.all([
          context.waitForEvent('page'),
          page.locator('.detail').getByRole('link', { name: 'Article Wikipédia' }).click(),
        ])
        expect(popup.url()).toContain('wikipedia.org')
        await popup.close()
        await page.locator('.detail').getByRole('button', { name: 'Approfondir' }).click()
        const src = page.locator('.detail .sources a').first()
        await expect(src).toBeVisible()
        const [popup2] = await Promise.all([context.waitForEvent('page'), src.click()])
        expect(popup2.url()).toContain('wikipedia.org')
        await popup2.close()
        await page.locator('.detail').getByRole('button', { name: /Voir la fiche/ }).click()
        await expect(page.locator('.fiche h2')).toHaveText(country)
        await page.getByRole('button', { name: /Ouvrir le carnet/ }).click()
        await page.locator('.entree').first().waitFor()
      }
      expect(errs).toEqual([])
    })

    test('faits longs : plusieurs paragraphes, titres longs', async ({ page }) => {
      const errs = watchConsole(page)
      await seedAll(page)
      await boot(page)
      await openCarnet(page)
      // le plus long est le plus récent : affiché d'emblée
      await expect(page.locator('.detail .titre')).toHaveText(longest.fact.title)
      await page.locator('.detail').getByRole('button', { name: 'Approfondir' }).click()
      await check(page, 'carnet-fait-long')
      await page.locator('.detail').evaluate((el) => (el.scrollTop = el.scrollHeight))
      await check(page, 'carnet-fait-long-bas')
      // titre le plus long, dans la liste et dans le détail
      await page.locator('.recherche').fill(longestTitle.fact.title.slice(0, 40))
      await page.locator('.entree').first().click()
      await expect(page.locator('.detail .titre')).toHaveText(longestTitle.fact.title)
      await check(page, 'carnet-titre-long')

      // citations avec titres de section wiki ou « [réf. nécessaire] » : titres retirés, rien ne déborde
      const odd = items
        .filter((it) => it.fact.sources.some((s) => /^\s*=+[^=].*=+\s*$/m.test(s.quote ?? '') || /\[[^\]]*\]/.test(s.quote ?? '')))
        .slice(0, 4)
      for (const it of odd) {
        await page.locator('.recherche').fill(it.fact.title.slice(0, 40))
        await page.locator('.entree').first().click()
        await page.locator('.detail').getByRole('button', { name: 'Approfondir' }).click()
        const quotes = await page.locator('.detail blockquote').allTextContents()
        expect(quotes.join(' '), `${it.fact.id} : pas de « == »`).not.toMatch(/==/)
        expect(quotes.every((q) => q.replace(/[«»\s]/g, '').length > 0), `${it.fact.id} : citation non vide`).toBe(true)
        await check(page, `carnet-citation-${it.fact.id}`)
      }
      expect(errs).toEqual([])
    })
  })
}
