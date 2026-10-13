// Outils communs des recettes : données, réponses par vrais clics, erreurs console, captures.
import { expect, type Page } from '@playwright/test'
import { existsSync, mkdirSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import type { Country, FactsFile } from '../../src/lib/types'

const here = dirname(fileURLToPath(import.meta.url))
const WEB = resolve(here, '../..')
const REAL = resolve(WEB, 'public/data')
export const DATA_DIR = existsSync(resolve(REAL, 'countries.json')) ? REAL : resolve(WEB, 'fixtures')
export const IS_FIXTURE = DATA_DIR !== REAL
export const countries: Country[] = JSON.parse(readFileSync(resolve(DATA_DIR, 'countries.json'), 'utf8'))
export const byId = new Map(countries.map((c) => [c.id, c]))

export function facts(id: string): FactsFile | null {
  const f = resolve(DATA_DIR, 'facts', `${id}.json`)
  return existsSync(f) ? JSON.parse(readFileSync(f, 'utf8')) : null
}

export function idsWithFacts(): string[] {
  return countries.map((c) => c.id).filter((id) => facts(id)?.facts?.length)
}

export const CAPTURES = resolve(WEB, 'captures')

export async function shot(page: Page, name: string) {
  mkdirSync(CAPTURES, { recursive: true })
  const vp = page.viewportSize()!
  await page.screenshot({ path: resolve(CAPTURES, `${vp.width}x${vp.height}-${name}.png`) })
}

/** Collecte les erreurs et avertissements console ; à vérifier en fin de test. */
export function watchConsole(page: Page): string[] {
  const errs: string[] = []
  page.on('console', (m) => {
    if (m.type() === 'error' || m.type() === 'warning') errs.push(`${m.type()}: ${m.text()}`)
  })
  page.on('pageerror', (e) => errs.push('pageerror: ' + e.message))
  return errs
}

export async function boot(page: Page) {
  await page.goto('./')
  await page.waitForSelector('svg[aria-label="Carte du monde"] path.cadre-ovale')
  await page.waitForFunction(() => (window as any).__geoTest?.ready())
  await page.waitForTimeout(300)
}

export interface QuizState {
  variant: string
  id: string
  answer: 'choix' | 'saisie'
  choices: string[]
  answered: boolean
}

export const quiz = (page: Page) => page.evaluate(() => (window as any).__quiz as QuizState | null)

export function capitalOf(c: Country) {
  return c.capitals.find((k) => k.name_fr === c.quiz_capital) ?? c.capitals[0]
}

/** Un autre pays cliquable, loin de la cible, pour les mauvaises réponses. */
function otherCountry(id: string): Country {
  const target = byId.get(id)!
  return (
    countries.find((c) => c.id !== id && !c.small && c.label && c.continent !== target.continent && c.quizzable !== false) ??
    countries.find((c) => c.id !== id && c.label)!
  )
}

/**
 * Point réellement cliquable d'un pays : son point d'étiquette s'il touche bien le pays,
 * sinon le premier point d'une grille dans sa boîte où `elementFromPoint` renvoie ce pays.
 */
export async function countryPoint(page: Page, id: string): Promise<number[] | null> {
  return page.evaluate((i) => {
    const hits = (x: number, y: number) =>
      (document.elementFromPoint(x, y)?.closest('[data-id]') as HTMLElement | null)?.dataset.id === i
    const lp = (window as any).__atlas.country(i) as number[] | null
    if (lp && hits(lp[0], lp[1])) return lp
    const el = document.querySelector(`[data-id="${i}"]`)
    if (!el) return lp
    const r = el.getBoundingClientRect()
    const cx = r.left + r.width / 2
    const cy = r.top + r.height / 2
    const pts: number[][] = []
    for (let gy = 0; gy <= 12; gy++)
      for (let gx = 0; gx <= 12; gx++) pts.push([r.left + (r.width * gx) / 12, r.top + (r.height * gy) / 12])
    pts.sort((a, b) => Math.hypot(a[0] - cx, a[1] - cy) - Math.hypot(b[0] - cx, b[1] - cy))
    return pts.find(([x, y]) => hits(x, y)) ?? lp
  }, id)
}

async function clickMap(page: Page, pos: number[] | null) {
  expect(pos, 'position projetée').not.toBeNull()
  await page.mouse.move(pos![0], pos![1])
  await page.mouse.click(pos![0], pos![1])
}

/** Répond à la question en cours, juste ou faux, par de vrais clics / une vraie frappe. */
export async function answer(page: Page, correct: boolean) {
  const q = (await quiz(page))!
  expect(q).not.toBeNull()
  const target = byId.get(q.id)!
  const wrongId = q.choices.find((c) => c !== q.id) ?? otherCountry(q.id).id
  const wrong = byId.get(wrongId)!

  if (q.variant === 'carte-ou') {
    const id = correct ? q.id : otherCountry(q.id).id
    await clickMap(page, await countryPoint(page, id))
  } else if (q.variant === 'placer-capitale') {
    const cap = capitalOf(target)
    const lat = correct ? cap.lat : cap.lat > 0 ? cap.lat - 45 : cap.lat + 45
    const pos = await page.evaluate(([lo, la]) => (window as any).__atlas.point(lo, la), [cap.lon, lat])
    await clickMap(page, pos)
  } else if (q.variant === 'nom-drapeau') {
    const idx = q.choices.indexOf(correct ? q.id : wrongId)
    await page.locator('.pavillon').nth(idx).click()
  } else {
    const label = (c: Country) => (q.variant === 'pays-capitale' ? capitalOf(c).name_fr : c.name_fr)
    const want = label(correct ? target : wrong)
    if (q.answer === 'choix') {
      // libellé exact : « Russie » ne doit pas attraper « Biélorussie »
      const exact = new RegExp('^\\s*' + want.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\s*$')
      await page.locator('.option').filter({ has: page.locator('.libelle', { hasText: exact }) }).first().click()
    } else {
      const input = page.locator('input[role=combobox]')
      await input.click()
      await input.pressSequentially(correct ? want : 'Xyzzy', { delay: 10 })
      await page.keyboard.press('Enter')
    }
  }
  await expect(page.locator('.panneau')).toBeVisible()
  await expect(page.locator('.titre-verdict')).toContainText(correct ? 'Juste' : 'Non')
}

export async function nextQuestion(page: Page) {
  await page.getByRole('button', { name: /Question suivante|Voir le bilan/ }).click()
}

/** Lance une session par l'interface (vrais clics) avec un mode et une façon de répondre. */
export async function startSession(page: Page, mode: string, style: 'Quatre choix' | 'Saisie libre' = 'Quatre choix') {
  await page.getByRole('button', { name: 'Commencer une session' }).click()
  await page.locator('label.segment', { hasText: mode }).click()
  await page.locator('label.segment', { hasText: style }).click()
  await page.getByRole('button', { name: 'Commencer', exact: true }).click()
  await expect(page.locator('.question h1')).toBeVisible()
  await page.waitForTimeout(500)
}

/** Joue toute la session (bonnes réponses), jusqu'au bilan. */
export async function playThrough(page: Page, correct = true) {
  for (let i = 0; i < 40; i++) {
    if (await page.locator('.bilan').isVisible()) return
    await answer(page, correct)
    await nextQuestion(page)
    await page.waitForTimeout(450)
  }
  throw new Error('session sans fin')
}
