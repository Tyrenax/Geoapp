// Contrôle visuel final (exigence de Josca) : aucun texte qui dépasse de sa case, aucun élément
// interactif hors de l'écran ou recouvert, rien de mal centré ; sur les noms, capitales et faits les
// plus longs des données, en 1280×720, 1600×900 et 1920×1080. Les captures vont dans captures/audit-*.
import { expect, test } from '@playwright/test'
import { centered, check } from './audit-lib'
import { IS_FIXTURE, boot, byId, capitalOf, countries, facts, idsWithFacts, watchConsole } from './helpers'

// ---------- les cas extrêmes des données ----------

const quizzable = countries.filter((c) => c.quizzable !== false)
const byLen = <T>(xs: T[], f: (x: T) => number) => [...xs].sort((a, b) => f(b) - f(a))
const longestNames = byLen(quizzable, (c) => c.name_fr.length).slice(0, 4)
const withCapital = quizzable.filter((c) => c.capitals.length && c.quiz_capital)
const longestCapitals = byLen(withCapital, (c) => capitalOf(c).name_fr.length).slice(0, 4)
const longestQuestion = byLen(withCapital, (c) => capitalOf(c).name_fr.length + c.name_fr.length)[0]
const longestOfficial = byLen(countries, (c) => (c.name_official_fr ?? c.name_fr).length)[0]
const mostCapitals = byLen(countries, (c) => c.capitals.length)[0]
const longestFlagNote = byLen(countries, (c) => (c.flag_note_fr ?? '').length)[0]
const factIds = idsWithFacts()
const longestFacts = byLen(factIds, (id) => {
  const f = facts(id)!
  return Math.max(...[...f.facts, ...(f.capital_facts ?? [])].map((x) => (x.long ?? '').length + x.short.length + x.title.length))
})[0]
const longestTips = byLen(factIds, (id) => {
  const t = facts(id)!.tips ?? {}
  return Math.max((t.position ?? '').length, (t.flag ?? '').length, (t.capital ?? '').length)
})[0]
const withFlag = quizzable.filter((c) => c.flag && c.flag_quizzable !== false)
const longestFlagNames = byLen(withFlag, (c) => c.name_fr.length).slice(0, 4)

/** Progression simulée : beaucoup de pays encrés (noms calligraphiés) et tous les faits découverts. */
function seededState() {
  const now = Date.now()
  const cards: Record<string, unknown> = {}
  quizzable.forEach((c, i) => {
    const level = i % 4 // 0 à 3 modes maîtrisés
    ;(['carte', 'drapeau', 'capitale'] as const).slice(0, level).forEach((m) => {
      cards[`${m}:${c.id}`] = { key: `${m}:${c.id}`, ease: 2.5, interval: 3, reps: 2, lapses: 0, due: now + (i % 7 === 0 ? -5 : 2) * 86400000, last: now, seen: 2 }
    })
  })
  const found: Record<string, number> = {}
  for (const id of factIds) {
    const f = facts(id)!
    ;[...f.facts, ...(f.capital_facts ?? [])].forEach((x, i) => (found[x.id] = now - i * 1000))
  }
  return { version: 1, cards, facts: found, settings: { mode: 'tout', answer: 'choix', continents: ['afrique', 'amerique-nord', 'amerique-sud', 'asie', 'europe', 'oceanie'], territories: true } }
}

for (const vp of [
  { width: 1280, height: 720 },
  { width: 1600, height: 900 },
  { width: 1920, height: 1080 },
]) {
  test.describe(`contrôle ${vp.width}×${vp.height}`, () => {
    test.use({ viewport: vp })

    test('accueil vierge, lancement, carnet vide', async ({ page }) => {
      const errs = watchConsole(page)
      await boot(page)
      await check(page, 'accueil-vierge')
      await page.getByRole('button', { name: 'Commencer une session' }).click()
      await centered(page, '.lancement')
      await check(page, 'lancement')
      await page.locator('label.case', { hasText: 'Inclure les territoires' }).click()
      await page.locator('label.segment', { hasText: 'Saisie libre' }).click()
      await check(page, 'lancement-saisie')
      await page.getByRole('button', { name: 'Annuler' }).click()
      await page.getByRole('button', { name: /Ouvrir le carnet/ }).click()
      await check(page, 'carnet-vide')
      await page.getByRole('button', { name: 'Fermer le carnet' }).click()
      await expect(page.locator('.carnet[role=dialog]')).toHaveCount(0)
      expect(errs).toEqual([])
    })

    test('questions aux noms et capitales les plus longs', async ({ page }) => {
      const errs = watchConsole(page)
      await boot(page)
      const ids = (cs: { id: string }[]) => cs.map((c) => c.id)
      const items = [
        { key: `carte:${longestNames[0].id}`, variant: 'carte-nommer', choices: ids(longestNames) },
        { key: `carte:${longestNames[0].id}`, variant: 'carte-ou' },
        // grand pays tout en haut de l'ovale : ne doit pas passer sous le cartouche
        ...(byId.has('GRL') ? [{ key: 'carte:GRL', variant: 'carte-nommer' }] : []),
        ...(byId.has('RUS') ? [{ key: 'carte:RUS', variant: 'carte-nommer' }] : []),
        { key: `capitale:${longestCapitals[0].id}`, variant: 'pays-capitale', choices: ids(longestCapitals) },
        { key: `capitale:${longestQuestion.id}`, variant: 'capitale-pays', choices: ids(longestNames) },
        { key: `capitale:${longestQuestion.id}`, variant: 'placer-capitale' },
        { key: `drapeau:${longestFlagNames[0].id}`, variant: 'nom-drapeau', choices: ids(longestFlagNames) },
        { key: `drapeau:${longestFlagNames[0].id}`, variant: 'drapeau-nom', choices: ids(longestFlagNames) },
      ]
      await page.evaluate((it) => (window as any).__geoTest.session(it, 'choix'), items)
      for (const it of items) {
        await page.waitForTimeout(700)
        const q = await page.evaluate(() => (window as any).__quiz)
        expect(q.variant).toBe(it.variant)
        await centered(page, '.question', '.colonne-principale')
        if (it.variant === 'carte-nommer') {
          // le pays à nommer n'est caché ni par le cartouche ni par les réponses
          const hidden = await page.evaluate(() => {
            const h = document.querySelector('.surlignage, .marqueur.surligne-question') as Element | null
            if (!h) return 'pas de surlignage'
            const r = h.getBoundingClientRect()
            const top = document.querySelector('.barre')!.getBoundingClientRect().bottom
            const bas = document.querySelector('.quiz .bas')!.getBoundingClientRect().top
            return r.top >= top - 1 && r.bottom <= bas + 1 && r.left >= 0 && r.right <= innerWidth ? '' : `[${Math.round(r.top)}→${Math.round(r.bottom)}] hors de [${Math.round(top)}→${Math.round(bas)}]`
          })
          expect(hidden, 'pays à nommer visible').toBe('')
        }
        await check(page, `q-${it.variant}`)
        // mauvaise réponse : verdict, astuce, bonne réponse montrée
        if (it.variant === 'carte-ou' || it.variant === 'placer-capitale') {
          const pos = await page.evaluate(() => (window as any).__atlas.point(-30, -40))
          await page.mouse.click(pos[0], pos[1])
        } else if (it.variant === 'nom-drapeau') {
          await page.locator('.pavillon').nth(q.choices.findIndex((c: string) => c !== q.id)).click()
        } else {
          await page.locator('.option').nth(q.choices.findIndex((c: string) => c !== q.id)).click()
        }
        await expect(page.locator('.panneau')).toBeVisible()
        await page.waitForTimeout(1100)
        await check(page, `r-${it.variant}`)
        await page.getByRole('button', { name: /Question suivante|Voir le bilan/ }).click()
      }
      await expect(page.locator('.bilan')).toBeVisible()
      expect(errs).toEqual([])
    })

    test('saisie : longue capitale dans le cartouche, complétion ouverte', async ({ page }) => {
      const errs = watchConsole(page)
      await boot(page)
      await page.evaluate(
        (id) => (window as any).__geoTest.session([{ key: `capitale:${id}`, variant: 'pays-capitale' }], 'saisie'),
        longestCapitals[0].id,
      )
      await page.waitForTimeout(500)
      const input = page.locator('input[role=combobox]')
      await input.click()
      await input.pressSequentially('sa', { delay: 20 })
      await expect(page.locator('.completion li').first()).toBeVisible()
      await check(page, 'completion')
      await input.fill('')
      await input.pressSequentially('Zzzzzz', { delay: 5 })
      await page.keyboard.press('Enter')
      await expect(page.locator('.panneau')).toBeVisible()
      await check(page, 'saisie-faux')
      expect(errs).toEqual([])
    })

    test('faits et astuces les plus longs, Approfondir ouvert', async ({ page }) => {
      test.skip(!longestFacts, 'aucun fait dans les données')
      const errs = watchConsole(page)
      await boot(page)
      for (const [id, label] of [
        [longestFacts, 'fait-long'],
        [longestTips, 'astuce-longue'],
      ] as const) {
        await page.evaluate((i) => (window as any).__geoTest.session([{ key: `carte:${i}`, variant: 'carte-nommer' }], 'choix'), id)
        await page.waitForTimeout(600)
        const q = await page.evaluate(() => (window as any).__quiz)
        await page.locator('.option').nth(q.choices.findIndex((c: string) => c !== q.id)).click()
        await expect(page.locator('.fait-bloc .titre')).toBeVisible()
        await check(page, `${label}-court`)
        await page.getByRole('button', { name: 'Approfondir' }).click()
        await check(page, `${label}-approfondi`)
        // le bas du panneau se lit en défilant
        await page.locator('.panneau .corps').evaluate((el) => (el.scrollTop = el.scrollHeight))
        await check(page, `${label}-approfondi-bas`)
      }
      expect(errs).toEqual([])
    })

    test('atlas très encré, fiches extrêmes, carnet plein, bilan', async ({ page }) => {
      const errs = watchConsole(page)
      const state = seededState()
      await page.addInitScript((s) => {
        if (!sessionStorage.getItem('seeded')) {
          localStorage.setItem('geo-atlas.v1', JSON.stringify(s))
          sessionStorage.setItem('seeded', '1')
        }
      }, state)
      await boot(page)
      await page.waitForTimeout(800)
      await check(page, 'atlas-encre')
      for (const c of [longestNames[0], longestOfficial, mostCapitals, ...(longestFlagNote?.flag_note_fr ? [longestFlagNote] : []), ...(factIds.length ? [byId.get(longestFacts)!] : [])]) {
        await page.evaluate((id) => (window as any).__geoTest.fiche(id), c.id)
        await expect(page.locator('.fiche h2')).toHaveText(c.name_fr)
        await check(page, `fiche-${c.id}`)
        const more = page.locator('.fiche').getByRole('button', { name: 'Approfondir' })
        if (await more.count()) {
          await more.first().click()
          await check(page, `fiche-${c.id}-approfondi`)
        }
      }
      await page.getByRole('button', { name: 'Fermer la fiche' }).click()
      await page.getByRole('button', { name: /Ouvrir le carnet/ }).click()
      await check(page, 'carnet-plein')
      for (const o of ['Pays', 'Continent', 'Thème']) {
        await page.getByRole('radio', { name: o }).click()
        await check(page, `carnet-${o}`)
      }
      if (await page.locator('.entree').count()) {
        await page.locator('.detail').getByRole('button', { name: 'Approfondir' }).click()
        await check(page, 'carnet-approfondi')
      }
      await page.getByRole('button', { name: 'Fermer le carnet' }).click()

      // bilan avec beaucoup de pays encrés d'un coup
      const items = longestNames.map((c) => ({ key: `carte:${c.id}`, variant: 'carte-nommer', choices: [c.id, ...longestNames.filter((x) => x.id !== c.id).map((x) => x.id)] }))
      await page.evaluate((it) => (window as any).__geoTest.session(it, 'choix'), items)
      for (let i = 0; i < items.length; i++) {
        await page.waitForTimeout(500)
        const q = await page.evaluate(() => (window as any).__quiz)
        await page.locator('.option').nth(q.choices.indexOf(q.id)).click()
        await page.getByRole('button', { name: /Question suivante|Voir le bilan/ }).click()
      }
      await expect(page.locator('.bilan')).toBeVisible()
      await centered(page, '.bilan')
      await check(page, 'bilan')
      await page.getByRole('button', { name: "Retour à l'atlas" }).click()
      await page.waitForTimeout(4000)
      await check(page, 'atlas-apres-bilan')
      expect(errs).toEqual([])
    })

    test('drapeaux extrêmes (NPL, QAT, CHE, VAT) : QCM, question et fiche', async ({ page }) => {
      const errs = watchConsole(page)
      await boot(page)
      const ids = ['NPL', 'QAT', 'CHE', 'VAT'].filter((i) => byId.get(i)?.flag)
      test.skip(ids.length < 4, 'drapeaux extrêmes absents des données')
      const items = [
        { key: `drapeau:${ids[0]}`, variant: 'nom-drapeau', choices: ids },
        ...ids.map((i) => ({ key: `drapeau:${i}`, variant: 'drapeau-nom', choices: ids })),
      ]
      await page.evaluate((it) => (window as any).__geoTest.session(it, 'choix'), items)
      for (let n = 0; n < items.length; n++) {
        await page.waitForTimeout(600)
        await check(page, `drapeaux-extremes-q${n}`)
        const q = await page.evaluate(() => (window as any).__quiz)
        if (q.variant === 'nom-drapeau') await page.locator('.pavillon').nth(q.choices.indexOf(q.id)).click()
        else await page.locator('.option').nth(q.choices.indexOf(q.id)).click()
        await expect(page.locator('.panneau')).toBeVisible()
        await check(page, `drapeaux-extremes-r${n}`)
        await page.getByRole('button', { name: /Question suivante|Voir le bilan/ }).click()
      }
      for (const i of ids) {
        await page.evaluate((id) => (window as any).__geoTest.fiche(id), i)
        await expect(page.locator('.fiche .drapeau')).toBeVisible()
        await check(page, `drapeaux-extremes-fiche-${i}`)
      }
      expect(errs).toEqual([])
    })

    test('chaque drapeau posable se charge', async ({ page }) => {
      await boot(page)
      const broken = await page.evaluate(async (list) => {
        const bad: string[] = []
        await Promise.all(
          list.map(
            (src) =>
              new Promise<void>((res) => {
                const im = new Image()
                im.onload = () => {
                  if (!im.naturalWidth) bad.push(src)
                  res()
                }
                im.onerror = () => {
                  bad.push(src)
                  res()
                }
                im.src = src
              }),
          ),
        )
        return bad
      }, countries.filter((c) => c.flag && c.flag_quizzable !== false && c.quizzable !== false).map((c) => (IS_FIXTURE ? 'fixtures/' : 'data/') + c.flag))
      expect(broken).toEqual([])
    })

    test('noms calligraphiés : aucun ne déborde sur un autre pays, à plusieurs zooms', async ({ page }) => {
      const errs = watchConsole(page)
      // atlas entièrement encré (3 modes partout) : tous les noms sont candidats
      const now = Date.now()
      const cards: Record<string, unknown> = {}
      for (const c of countries.filter((x) => x.quizzable !== false))
        for (const m of ['carte', 'drapeau', 'capitale'])
          cards[`${m}:${c.id}`] = { key: `${m}:${c.id}`, ease: 2.5, interval: 3, reps: 2, lapses: 0, due: now + 2 * 86400000, last: now, seen: 2 }
      const state = { version: 1, cards, facts: {}, settings: { mode: 'carte', answer: 'choix', continents: ['afrique', 'amerique-nord', 'amerique-sud', 'asie', 'europe', 'oceanie'], territories: true } }
      await page.addInitScript((s) => {
        if (!sessionStorage.getItem('seeded')) {
          localStorage.setItem('geo-atlas.v1', JSON.stringify(s))
          sessionStorage.setItem('seeded', '1')
        }
      }, state)
      await boot(page)
      await page.waitForTimeout(600)

      /** Grille de points dans chaque nom : seul son pays, la mer ou rien peuvent être dessous. */
      const overlaps = () =>
        page.evaluate(() => {
          const bad: string[] = []
          for (const tx of document.querySelectorAll('text.nom-pays[data-pays]')) {
            const own = (tx as SVGElement).dataset.pays
            const r = tx.getBoundingClientRect()
            const hits = new Set<string>()
            for (let gy = 0; gy <= 2; gy++)
              for (let gx = 0; gx <= 6; gx++) {
                const x = r.left + 2 + ((r.width - 4) * gx) / 6
                const y = r.top + r.height * 0.3 + (r.height * 0.4 * gy) / 2
                const el = document.elementFromPoint(x, y)
                const other = (el?.closest('[data-id]') as HTMLElement | null)?.dataset.id ?? (el?.closest('[data-neutre]') ? 'zone neutre' : null)
                if (other && other !== own) hits.add(other)
              }
            if (hits.size) bad.push(`${own} (« ${tx.textContent?.trim()} ») sur ${[...hits].join(', ')}`)
          }
          return { bad, n: document.querySelectorAll('text.nom-pays').length }
        })

      const views: [string, string | null, number][] = [
        ['monde', null, 1],
        ['golfe', 'QAT', 10],
        ['levant', 'LBN', 10],
        ['amerique-centrale', 'GTM', 4],
        ['balkans', 'MKD', 6],
        ['benelux', 'BEL', 6],
        ['afrique-ouest', 'GMB', 8],
      ]
      for (const [label, id, context] of views) {
        if (id && !byId.has(id)) continue
        if (id) await page.evaluate(([i, c]) => (window as any).__atlas.zoomTo(i, c, 16), [id, context] as const)
        await page.waitForTimeout(1300)
        const { bad, n } = await overlaps()
        await check(page, `noms-${label}`)
        expect(n, `${label} : des noms sont écrits`).toBeGreaterThan(0)
        expect(bad, `${label} : noms qui débordent`).toEqual([])
        if (id) {
          await page.getByRole('button', { name: 'Recentrer la carte' }).click()
          await page.waitForTimeout(900)
        }
      }
      expect(errs).toEqual([])
    })

    test('fiche : chaque lien et bouton', async ({ page, context }) => {
      const errs = watchConsole(page)
      await context.route(/wikipedia\.org/, (r) => r.fulfill({ status: 200, body: 'ok', contentType: 'text/html' }))
      await boot(page)
      const c = byId.get(factIds[0] ?? mostCapitals.id)!
      await page.evaluate((id) => (window as any).__geoTest.fiche(id), c.id)
      const links = page.locator('.fiche a[href]')
      const n = await links.count()
      expect(n).toBeGreaterThan(0)
      for (let i = 0; i < n; i++) {
        const [popup] = await Promise.all([context.waitForEvent('page'), links.nth(i).click()])
        expect(popup.url()).toContain('wikipedia.org')
        await popup.close()
      }
      for (let i = 0; i < 20; i++) {
        const reveal = page.locator('.fiche').getByRole('button', { name: 'Révéler' }).first()
        if (!(await reveal.count())) break
        await reveal.click()
      }
      const more = page.locator('.fiche').getByRole('button', { name: 'Approfondir' })
      if (await more.count()) {
        await more.first().click()
        await page.locator('.fiche').getByRole('button', { name: 'Replier' }).first().click()
      }
      await page.keyboard.press('Escape')
      await expect(page.locator('.fiche')).toHaveCount(0)
      expect(errs).toEqual([])
    })

    test("fiche : carte d'identité et plaque (cas extrêmes)", async ({ page }) => {
      const errs = watchConsole(page)
      await boot(page)
      const plates = (c: (typeof countries)[number]) => (Array.isArray(c.plate_code) ? c.plate_code : c.plate_code ? [c.plate_code] : [])
      const cases: [string, string | undefined][] = [
        ['langues', byLen(countries, (c) => (c.languages_fr ?? []).join(', ').length)[0]?.id],
        ['monnaies', byLen(countries, (c) => JSON.stringify(c.currencies ?? []).length)[0]?.id],
        ['plaque-longue', byLen(countries, (c) => Math.max(0, ...plates(c).map((p) => p.length)))[0]?.id],
        ['plaques-multiples', byLen(countries, (c) => plates(c).length)[0]?.id],
        ['territoire-sans-code', countries.find((c) => c.kind === 'territoire' && !plates(c).length)?.id],
      ]
      for (const [label, id] of cases) {
        if (!id) continue
        await page.evaluate((i) => (window as any).__geoTest.fiche(i), id)
        const sec = page.locator('.fiche section.identite')
        await expect(sec).toHaveCount(1)
        await sec.scrollIntoViewIfNeeded()
        await check(page, `identite-${label}-${id}`)
        // Les lettres tiennent dans l'ovale.
        const bad = await page.evaluate(() =>
          [...document.querySelectorAll('.fiche svg.plaque')].flatMap((svg) => {
            const t = svg.querySelector('text')!.getBBox()
            const e = svg.querySelector('ellipse.filet')!.getBBox()
            return t.x < e.x || t.x + t.width > e.x + e.width || t.y < e.y || t.y + t.height > e.y + e.height ? [svg.getAttribute('aria-label')] : []
          }),
        )
        expect(bad, `${label} : lettres hors de l'ovale`).toEqual([])
      }
      expect(errs).toEqual([])
    })
  })
}
