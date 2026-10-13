// Parcours de jeu à vrais clics : chaque mode, une bonne et une mauvaise réponse, Approfondir,
// fiche Atlas, carnet, et l'atlas qui s'encre après des réussites.
import { expect, test } from '@playwright/test'
import {
  answer,
  boot,
  byId,
  countryPoint,
  idsWithFacts,
  nextQuestion,
  playThrough,
  quiz,
  shot,
  startSession,
  watchConsole,
} from './helpers'

for (const vp of [
  { width: 1600, height: 900 },
  { width: 1280, height: 720 },
]) {
  test.describe(`${vp.width}×${vp.height}`, () => {
    test.use({ viewport: vp })

    test('premier lancement : atlas vierge, une invitation, un bouton', async ({ page }) => {
      const errs = watchConsole(page)
      await boot(page)
      await expect(page.getByText('Le monde est encore à tracer.')).toBeVisible()
      await expect(page.locator('.accueil button')).toHaveCount(1)
      expect(await page.locator('path.pays.encre-1, path.pays.encre-2, path.pays.encre-3').count()).toBe(0)
      await shot(page, '01-atlas-vierge')
      expect(errs).toEqual([])
    })

    for (const mode of ['Sur la carte', 'Drapeaux', 'Capitales'] as const) {
      test(`session ${mode} : juste puis faux`, async ({ page }) => {
        const errs = watchConsole(page)
        await boot(page)
        await startSession(page, mode, mode === 'Capitales' ? 'Saisie libre' : 'Quatre choix')
        const slug = mode === 'Sur la carte' ? 'carte' : mode === 'Drapeaux' ? 'drapeau' : 'capitale'
        await shot(page, `02-${slug}-question`)
        await answer(page, true)
        await shot(page, `03-${slug}-juste`)
        await nextQuestion(page)
        await page.waitForTimeout(500)
        await answer(page, false)
        await page.waitForTimeout(1100) // zoom animé vers la bonne réponse
        await shot(page, `04-${slug}-faux`)
        await expect(page.locator('.sceau')).toBeVisible()
        expect(errs).toEqual([])
      })
    }

    test('les sept variantes de question, juste et faux', async ({ page }) => {
      const errs = watchConsole(page)
      await boot(page)
      const id = 'BOL' in Object.fromEntries(byId) ? 'BOL' : [...byId.keys()][0]
      const variants = [
        ['carte', 'carte-ou'],
        ['carte', 'carte-nommer'],
        ['drapeau', 'drapeau-nom'],
        ['drapeau', 'nom-drapeau'],
        ['capitale', 'pays-capitale'],
        ['capitale', 'capitale-pays'],
        ['capitale', 'placer-capitale'],
      ] as const
      for (const style of ['choix', 'saisie'] as const) {
        const items = variants.flatMap(([m, v]) => [
          { key: `${m}:${id}`, variant: v },
          { key: `${m}:${id}`, variant: v },
        ])
        await page.evaluate(([it, st]) => (window as any).__geoTest.session(it, st), [items, style] as const)
        // pas de reprise des erreurs : la série se déroule exactement dans l'ordre donné
        let i = 0
        while (!(await page.locator('.bilan').isVisible())) {
          await page.waitForTimeout(500)
          const q = (await quiz(page))!
          expect(q.variant).toBe(items[i].variant)
          await answer(page, i % 2 === 0)
          if (style === 'choix') await shot(page, `05-variante-${q.variant}-${i % 2 === 0 ? 'juste' : 'faux'}`)
          i++
          await nextQuestion(page)
          await page.waitForTimeout(200)
        }
        expect(i).toBe(items.length)
        await expect(page.locator('.bilan')).toBeVisible()
        await page.getByRole('button', { name: "Retour à l'atlas" }).click()
      }
      expect(errs).toEqual([])
    })

    test('Approfondir, Wikipédia et sources', async ({ page, context }) => {
      const errs = watchConsole(page)
      await boot(page)
      const id = idsWithFacts().find((i) => !byId.get(i)?.small)
      test.skip(!id, 'aucun fait dans les données')
      await page.evaluate((i) => (window as any).__geoTest.session([{ key: `carte:${i}`, variant: 'carte-ou' }]), id)
      await page.waitForTimeout(500)
      await answer(page, true)
      await expect(page.locator('.fait-bloc .titre')).toBeVisible()
      await page.getByRole('button', { name: 'Approfondir' }).click()
      await expect(page.locator('.fait-bloc .sources a').first()).toBeVisible()
      await shot(page, '06-approfondir')
      // un lien de source ouvre bien un nouvel onglet vers Wikipédia (on ne charge pas la page)
      await context.route(/wikipedia\.org/, (r) => r.fulfill({ status: 200, body: 'ok' }))
      const [popup] = await Promise.all([
        context.waitForEvent('page'),
        page.locator('.fait-bloc .sources a').first().click(),
      ])
      expect(popup.url()).toContain('wikipedia.org')
      await popup.close()
      const [popup2] = await Promise.all([
        context.waitForEvent('page'),
        page.locator('.fait-bloc .liens a').click(),
      ])
      expect(popup2.url()).toContain('wikipedia.org')
      await popup2.close()
      await page.getByRole('button', { name: 'Replier' }).click()
      await expect(page.locator('.fait-bloc .sources')).toHaveCount(0)
      expect(errs).toEqual([])
    })

    test("l'atlas s'encre après des réussites, fiche et carnet", async ({ page }) => {
      const errs = watchConsole(page)
      await boot(page)
      await startSession(page, 'Tout mêler')
      await playThrough(page, true)
      await shot(page, '07-bilan')
      await expect(page.locator('.bilan')).toContainText('Encré')
      await page.getByRole('button', { name: "Retour à l'atlas" }).click()
      await page.waitForTimeout(400)
      await shot(page, '08-atlas-encrage-en-cours')
      await page.waitForTimeout(4500)
      await shot(page, '09-atlas-encre')
      const inked = await page.locator('path.pays.encre-1, path.pays.encre-2, path.pays.encre-3').count()
      expect(inked).toBeGreaterThan(0)
      await expect(page.locator('.compteur')).toContainText('encré')

      // clic réel sur un pays encré → sa fiche
      const id = await page.evaluate(() => {
        const el = document.querySelector('path.pays.encre-1, path.pays.encre-2, path.pays.encre-3') as SVGElement
        return el?.dataset.id
      })
      const pos = (await countryPoint(page, id!))!
      await page.mouse.click(pos[0], pos[1])
      await expect(page.locator('.fiche h2')).toHaveText(byId.get(id!)!.name_fr)
      await shot(page, '10-fiche')
      const reveal = page.getByRole('button', { name: 'Révéler' }).first()
      if (await reveal.count()) {
        await reveal.click()
        await expect(page.locator('.fiche .faits .titre').first()).toBeVisible()
      }
      await page.getByRole('button', { name: 'Fermer la fiche' }).click()
      await expect(page.locator('.fiche')).toHaveCount(0)

      // carnet
      await page.getByRole('button', { name: /Ouvrir le carnet/ }).click()
      await expect(page.locator('.carnet h2')).toHaveText("Carnet de l'explorateur")
      await shot(page, '11-carnet')
      for (const o of ['Pays', 'Continent', 'Thème', 'Ordre de découverte']) {
        await page.getByRole('radio', { name: o }).click()
        await expect(page.getByRole('radio', { name: o })).toHaveAttribute('aria-checked', 'true')
      }
      if (await page.locator('.entree').count()) {
        await page.locator('.entree').first().click()
        await page.locator('.detail').getByRole('button', { name: 'Approfondir' }).click()
        await expect(page.locator('.detail .sources')).toBeVisible()
        await page.locator('.recherche').fill('zzzzzz')
        await expect(page.locator('.liste')).toContainText('Rien ne correspond')
        await page.locator('.recherche').fill('')
        await page.locator('.entree').first().click()
        await page.locator('.detail').getByRole('button', { name: /Voir la fiche/ }).click()
        await expect(page.locator('.fiche')).toBeVisible()
      } else {
        await page.getByRole('button', { name: 'Fermer le carnet' }).click()
      }
      expect(errs).toEqual([])
    })

    test('ornements : rose des vents, zoom, Échap', async ({ page }) => {
      const errs = watchConsole(page)
      await boot(page)
      const k = () => page.evaluate(() => (window as any).__atlas.transform().k)
      await page.getByRole('button', { name: 'Zoomer', exact: true }).click()
      await page.waitForTimeout(400)
      expect(await k()).toBeGreaterThan(1.5)
      await page.getByRole('button', { name: 'Dézoomer' }).click()
      await page.waitForTimeout(400)
      expect(await k()).toBeLessThan(1.1)
      await page.mouse.move(800, 450)
      await page.mouse.wheel(0, -600)
      await page.waitForTimeout(500)
      expect(await k()).toBeGreaterThan(1.2)
      await page.getByRole('button', { name: 'Recentrer la carte' }).click()
      await page.waitForTimeout(900)
      expect(await k()).toBeCloseTo(1, 2)
      await page.getByRole('button', { name: 'Commencer une session' }).click()
      await page.keyboard.press('Escape')
      await expect(page.locator('.lancement')).toHaveCount(0)
      await page.getByRole('button', { name: 'Commencer une session' }).click()
      await page.getByRole('button', { name: 'Annuler' }).click()
      await expect(page.locator('.lancement')).toHaveCount(0)
      expect(errs).toEqual([])
    })

    test('saisie : complétion au clavier et à la souris, accents et fautes', async ({ page }) => {
      const errs = watchConsole(page)
      await boot(page)
      const id = [...byId.values()].find((c) => /[éèêç]/.test(c.name_fr) && c.quizzable !== false)?.id ?? [...byId.keys()][0]
      const c = byId.get(id)!
      const items = [
        { key: `drapeau:${id}`, variant: 'drapeau-nom' },
        { key: `drapeau:${id}`, variant: 'drapeau-nom' },
        { key: `drapeau:${id}`, variant: 'drapeau-nom' },
      ]
      await page.evaluate((it) => (window as any).__geoTest.session(it, 'saisie'), items)
      const input = page.locator('input[role=combobox]')
      // 1) flèches + Entrée dans la complétion
      await input.click()
      const plain = c.name_fr.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
      await input.pressSequentially(plain.slice(0, 3), { delay: 20 })
      await expect(page.locator('.completion li').first()).toBeVisible()
      await shot(page, '12-completion')
      const idx = await page.locator('.completion li').evaluateAll((els, n) => els.findIndex((e) => e.textContent!.trim() === n), c.name_fr)
      for (let i = 0; i <= Math.max(0, idx); i++) await page.keyboard.press('ArrowDown')
      await page.keyboard.press('Enter')
      await expect(page.locator('.titre-verdict')).toContainText('Juste')
      await nextQuestion(page)
      // 2) sans accents, avec une faute, bouton Valider
      await page.waitForTimeout(300)
      await input.click()
      const typo = plain.length >= 5 ? plain.slice(0, 2) + (plain[2] === 'x' ? 'z' : 'x') + plain.slice(3) : plain
      await input.pressSequentially(typo, { delay: 10 })
      await page.keyboard.press('Escape')
      await expect(page.locator('.completion')).toHaveCount(0)
      await page.getByRole('button', { name: 'Valider' }).click()
      await expect(page.locator('.titre-verdict')).toContainText('Juste')
      await nextQuestion(page)
      // 3) clic souris dans la liste
      await page.waitForTimeout(300)
      await input.click()
      await input.pressSequentially(plain.slice(0, 4), { delay: 10 })
      await page.locator('.completion li', { hasText: c.name_fr }).first().click()
      await expect(page.locator('.titre-verdict')).toContainText('Juste')
      expect(errs).toEqual([])
    })

    test('sons : coupés par défaut, bouton muet mémorisé', async ({ page }) => {
      const errs = watchConsole(page)
      await boot(page)
      const toggle = page.locator('button.son').first()
      await expect(toggle).toHaveAttribute('aria-pressed', 'false')
      await expect(toggle).toContainText('Sons coupés')
      await toggle.click()
      await expect(toggle).toHaveAttribute('aria-pressed', 'true')
      await expect(toggle).toContainText('Sons actifs')
      await page.reload()
      await boot(page)
      await expect(page.locator('button.son').first()).toHaveAttribute('aria-pressed', 'true')
      // pendant une session aussi, et une réponse joue son son sans erreur
      await startSession(page, 'Sur la carte')
      await expect(page.locator('.progression button.son')).toBeVisible()
      await answer(page, true)
      await page.locator('.progression button.son').click()
      await expect(page.locator('.progression button.son')).toHaveAttribute('aria-pressed', 'false')
      expect(errs).toEqual([])
    })

    test('zone neutre : un clic ne compte jamais comme une réponse', async ({ page }) => {
      const errs = watchConsole(page)
      await boot(page)
      const has = await page.locator('path.neutre').count()
      test.skip(!has, 'pas de zone neutre dans ces données')
      const id = byId.has('UKR') ? 'UKR' : [...byId.keys()][0]
      await page.evaluate((i) => (window as any).__geoTest.session([{ key: `carte:${i}`, variant: 'carte-ou' }]), id)
      await page.waitForTimeout(600)
      // point réellement cliquable de la plus grande zone neutre
      const pos = await page.evaluate(() => {
        const zones = [...document.querySelectorAll('path.neutre')].map((e) => ({ e, r: e.getBoundingClientRect() }))
        zones.sort((a, b) => b.r.width * b.r.height - a.r.width * a.r.height)
        for (const { e, r } of zones)
          for (let gy = 1; gy < 8; gy++)
            for (let gx = 1; gx < 8; gx++) {
              const x = r.left + (r.width * gx) / 8
              const y = r.top + (r.height * gy) / 8
              if (document.elementFromPoint(x, y)?.closest('[data-neutre]') === e) return [x, y]
            }
        return null
      })
      expect(pos, 'zone neutre cliquable').not.toBeNull()
      await page.mouse.move(pos![0], pos![1])
      await expect(page.locator('.bulle')).toContainText('zone sans État')
      await page.mouse.click(pos![0], pos![1])
      await page.waitForTimeout(500)
      await expect(page.locator('.panneau')).toHaveCount(0)
      await answer(page, true)
      expect(errs).toEqual([])
    })

        test('quitter une session en cours puis en relancer une', async ({ page }) => {
      const errs = watchConsole(page)
      await boot(page)
      await startSession(page, 'Sur la carte')
      await answer(page, true)
      await page.getByRole('button', { name: 'Quitter la session' }).click()
      await expect(page.locator('.bilan')).toBeVisible()
      await page.getByRole('button', { name: 'Nouvelle session' }).click()
      await expect(page.locator('.lancement')).toBeVisible()
      // filtres : décocher toutes les régions désactive « Commencer »
      for (const r of ['Afrique', 'Amérique du Nord', 'Amérique du Sud', 'Asie', 'Europe', 'Océanie'])
        await page.locator('label.case', { hasText: r }).click()
      await expect(page.getByRole('button', { name: 'Commencer', exact: true })).toBeDisabled()
      await page.locator('label.case', { hasText: 'Europe' }).click()
      await page.locator('label.case', { hasText: 'Inclure les territoires' }).click()
      await page.getByRole('button', { name: 'Commencer', exact: true }).click()
      const q = (await quiz(page))!
      expect(byId.get(q.id)!.continent).toBe('europe')
      expect(errs).toEqual([])
    })
  })
}
