// Contrôle indépendant : chaque fiche des 250 entités, aux 3 tailles.
// Usage : node verif_fiches.mjs <url> <dossier captures>
import { chromium } from 'file:///C:/Users/Josca/Documents/geo-atlas/web/node_modules/playwright/index.mjs'
import { readFileSync, mkdirSync } from 'node:fs'

const URL = process.argv[2]
const OUT = process.argv[3]
mkdirSync(OUT, { recursive: true })
const countries = JSON.parse(readFileSync('C:/Users/Josca/Documents/geo-atlas/web/public/data/countries.json', 'utf8'))
const ids = countries.map((c) => c.id)
const SIZES = [[1280, 720], [1600, 900], [1920, 1080]]
const SHOTS = new Set(['GBR', 'COD', 'VCT', 'SGS', 'ATA', 'PSE', 'ISR', 'UMI', 'BOL', 'CAF'])

const browser = await chromium.launch()
const report = { console: [], http: [], fiches: [] }
for (const [w, h] of SIZES) {
  const page = await browser.newPage({ viewport: { width: w, height: h } })
  page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') report.console.push(`${w}: ${m.type()} ${m.text()}`) })
  page.on('pageerror', (e) => report.console.push(`${w}: pageerror ${e.message}`))
  page.on('response', (r) => { if (r.status() >= 400) report.http.push(`${w}: ${r.status()} ${r.url()}`) })
  await page.goto(URL)
  await page.waitForFunction(() => window.__geoTest?.ready?.(), null, { timeout: 30000 })
  await page.waitForTimeout(800)
  await page.screenshot({ path: `${OUT}/${w}x${h}-accueil.png` })
  for (const id of ids) {
    await page.evaluate((i) => window.__geoTest.fiche(i), id)
    const sel = 'aside.fiche'
    await page.waitForSelector(sel, { timeout: 5000 })
    await page.waitForTimeout(60)
    // Déplier tous les « Approfondir »
    for (let pass = 0; pass < 2; pass++) {
      for (const b of await page.$$(`${sel} button`)) {
        const t = (await b.innerText()).trim()
        if (t === 'Révéler' || t === 'Approfondir') await b.click().catch(() => {})
      }
      await page.waitForTimeout(60)
    }
    await page.waitForTimeout(80)
    const res = await page.evaluate(({ sel, id }) => {
      const aside = document.querySelector(sel)
      const ar = aside.getBoundingClientRect()
      const out = []
      if (ar.left < -1 || ar.right > innerWidth + 1 || ar.top < -1 || ar.bottom > innerHeight + 1) out.push(`fiche hors écran ${JSON.stringify(ar)}`)
      const name = aside.querySelector('h1,h2')
      if (!name || !name.textContent.trim()) out.push('pas de titre')
      for (const img of aside.querySelectorAll('img')) {
        if (!img.complete || img.naturalWidth === 0) out.push(`image non chargée ${img.getAttribute('src')}`)
        const r = img.getBoundingClientRect()
        if (r.width && img.naturalWidth) {
          const ratioShown = r.width / r.height, ratioNat = img.naturalWidth / img.naturalHeight
          if (Math.abs(ratioShown / ratioNat - 1) > 0.04 && getComputedStyle(img).objectFit !== 'contain') out.push(`image déformée ${ratioShown.toFixed(2)} vs ${ratioNat.toFixed(2)}`)
        }
      }
      for (const el of aside.querySelectorAll('*')) {
        const cs = getComputedStyle(el)
        if (cs.display === 'none' || cs.visibility === 'hidden') continue
        if (el.scrollWidth > el.clientWidth + 2 && !['auto', 'scroll'].includes(cs.overflowX) && el.clientWidth > 0 && el.children.length === 0)
          out.push(`débordement horizontal <${el.tagName.toLowerCase()} class="${el.className}"> « ${el.textContent.slice(0, 50)} »`)
        const r = el.getBoundingClientRect()
        if (r.width > 0 && (r.right > ar.right + 2 || r.left < ar.left - 2)) out.push(`sort de la fiche <${el.tagName.toLowerCase()}> « ${el.textContent.slice(0, 40)} »`)
      }
      const text = aside.innerText
      // Parenthèse collée à un mot, hors notations d'étymologie (« Gorj(i) », « Alo(ti)mé ») : lettres
      // entre parenthèses suivies d'une lettre, d'un crochet ou d'une ponctuation.
      const glued = text.match(/[a-zà-ÿ]\((?![a-zà-ÿ]{1,3}\)[a-zà-ÿ\]\s,.])(?!s\))/i)
      if (glued) out.push('espace manquante avant parenthèse : ' + text.slice(Math.max(0, glued.index - 20), glued.index + 20))
      if (!/faits? découverts? sur/.test(text)) out.push('compteur de faits absent')
      if (/Révéler/.test(text)) out.push('fait resté masqué')
      const nFaits = aside.querySelectorAll('ol.faits > li').length
      const nReplier = [...aside.querySelectorAll('button')].filter((b) => b.innerText.trim() === 'Replier').length
      if (nFaits && nReplier !== nFaits) out.push(`faits dépliés ${nReplier}/${nFaits}`)
      window.__depli = (window.__depli || 0) + nReplier
      if (/==|\[réf|undefined|NaN|\bnull\b/.test(text)) out.push('texte suspect : ' + (text.match(/.{0,30}(==|\[réf|undefined|NaN|\bnull\b).{0,30}/) || [''])[0])
      return out
    }, { sel, id })
    if (res.length) report.fiches.push(`${w}x${h} ${id}: ${[...new Set(res)].slice(0, 6).join(' | ')}`)
    if (SHOTS.has(id)) await page.screenshot({ path: `${OUT}/${w}x${h}-fiche-${id}.png` })
  }
  report.deplies = (report.deplies || 0) + (await page.evaluate(() => window.__depli || 0))
  await page.close()
}
await browser.close()
console.log(`console: ${report.console.length}`); for (const l of [...new Set(report.console)].slice(0, 30)) console.log('  ' + l)
console.log(`http >= 400: ${report.http.length}`); for (const l of [...new Set(report.http)].slice(0, 30)) console.log('  ' + l)
console.log(`faits dépliés et contrôlés (3 tailles) : ${report.deplies}`); console.log(`fiches avec défaut: ${report.fiches.length}`); for (const l of report.fiches.slice(0, 80)) console.log('  ' + l)
