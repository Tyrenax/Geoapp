// Contrôle visuel partagé : débordements, éléments recouverts, centrage (voir audit.spec.ts).
import { expect, type Page } from '@playwright/test'
import { mkdirSync } from 'node:fs'
import { CAPTURES, shot } from './helpers'

interface Issue {
  kind: string
  what: string
  detail: string
}

/** Inspecte la page : débordements, sorties d'écran, éléments interactifs recouverts. */
export async function audit(page: Page): Promise<Issue[]> {
  return page.evaluate(() => {
    const issues: { kind: string; what: string; detail: string }[] = []
    const vw = innerWidth
    const vh = innerHeight
    const name = (el: Element) => {
      const cls = [...el.classList].filter((c) => !c.startsWith('svelte-')).join('.')
      const txt = (el.textContent ?? '').trim().replace(/\s+/g, ' ').slice(0, 50)
      return `${el.tagName.toLowerCase()}${cls ? '.' + cls : ''} « ${txt} »`
    }
    const scroller = (el: Element) => el.closest('[data-defilant], .completion, .lancement, .bilan') as HTMLElement | null
    const skip = (el: Element) =>
      el.closest('svg, canvas, .grain, .bulle, .carte') !== null || ['HTML', 'BODY', 'SCRIPT', 'STYLE'].includes(el.tagName)

    const seen = new Set<string>()
    function check(box: Element, inner: Node, q: DOMRect) {
      if (q.width === 0 && q.height === 0) return
      const b = box.getBoundingClientRect()
      const out = q.left < b.left - 1 || q.right > b.right + 1 || q.top < b.top - 1 || q.bottom > b.bottom + 1
      if (!out) return
      const what = name(box)
      const key = what + '|' + (inner.textContent ?? '').slice(0, 30)
      if (seen.has(key)) return
      seen.add(key)
      const inn = inner.nodeType === Node.TEXT_NODE ? `texte « ${(inner.textContent ?? '').trim().slice(0, 40)} »` : name(inner as Element)
      issues.push({
        kind: 'dépasse de sa case',
        what,
        detail: `${inn} [${Math.round(q.left)},${Math.round(q.top)} → ${Math.round(q.right)},${Math.round(q.bottom)}] hors de [${Math.round(b.left)},${Math.round(b.top)} → ${Math.round(b.right)},${Math.round(b.bottom)}]`,
      })
    }
    function nextOutside(w: TreeWalker, e: Element): Node | null {
      // saute les descendants de e
      let n: Node | null = e
      while (n && !n.nextSibling && n.parentNode) {
        n = n.parentNode
        if (!w.root.contains(n) || n === w.root) return null
      }
      if (!n || !n.nextSibling) return null
      w.currentNode = n.nextSibling
      return w.currentNode
    }
    for (const el of document.querySelectorAll('body *')) {
      if (skip(el) || el.id === 'app') continue
      const cs = getComputedStyle(el)
      if (cs.display === 'none' || cs.visibility === 'hidden' || cs.display === 'contents') continue
      const r = el.getBoundingClientRect()
      if (r.width === 0 && r.height === 0) continue
      const he = el as HTMLElement
      const scrolls = he.hasAttribute('data-defilant') || ['auto', 'scroll'].includes(cs.overflowY)
      // 1) contenu coupé : boîte qui masque (overflow hidden/clip) plus petite que son contenu
      if (cs.display !== 'inline' && he.clientWidth > 0 && !scrolls) {
        const hides = (v: string) => v === 'hidden' || v === 'clip'
        if (hides(cs.overflowX) && he.scrollWidth > he.clientWidth + 1)
          issues.push({ kind: 'texte coupé (largeur)', what: name(el), detail: `${he.scrollWidth} > ${he.clientWidth}` })
        if (hides(cs.overflowY) && he.scrollHeight > he.clientHeight + 1)
          issues.push({ kind: 'texte coupé (hauteur)', what: name(el), detail: `${he.scrollHeight} > ${he.clientHeight}` })
      }
      // 1 bis) « case » visible (bordure ou fond) : tout son contenu doit rester dedans
      const hasBox =
        parseFloat(cs.borderTopWidth) + parseFloat(cs.borderLeftWidth) > 0 ||
        (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && cs.backgroundColor !== 'transparent')
      if (hasBox && !scrolls && !el.closest('.calque > .fond, .fond-bilan')) {
        const walker = document.createTreeWalker(el, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT)
        let n: Node | null = walker.nextNode()
        while (n) {
          if (n.nodeType !== Node.TEXT_NODE && n.nodeType !== Node.ELEMENT_NODE) {
            n = walker.nextNode()
            continue
          }
          let rects: DOMRect[] = []
          if (n.nodeType === Node.TEXT_NODE) {
            if ((n.textContent ?? '').trim()) {
              const rg = document.createRange()
              rg.selectNodeContents(n)
              rects = [...rg.getClientRects()]
            }
          } else {
            const ce = n as Element
            const ccs = getComputedStyle(ce)
            if (ce.closest('svg') && ce.tagName !== 'svg') {
              n = walker.nextNode()
              continue
            }
            if (ccs.position === 'absolute' || ccs.position === 'fixed' || ccs.display === 'none') {
              // éléments sortis du flux (listes déroulantes, entrées masquées) : contrôlés pour eux-mêmes
              n = nextOutside(walker, ce)
              continue
            }
            if (ce.hasAttribute('data-defilant') || ['auto', 'scroll'].includes(ccs.overflowY)) {
              rects = [ce.getBoundingClientRect()]
              n = nextOutside(walker, ce)
              for (const q of rects) check(el, ce, q)
              continue
            }
            rects = [ce.getBoundingClientRect()]
          }
          for (const q of rects) check(el, n, q)
          n = walker.nextNode()
        }
      }
      // 2) hors de la fenêtre (sauf dans une zone qui défile)
      const inScroller = scroller(el.parentElement ?? el)
      if (!inScroller && (r.left < -1 || r.top < -1 || r.right > vw + 1 || r.bottom > vh + 1))
        issues.push({
          kind: 'hors écran',
          what: name(el),
          detail: `[${Math.round(r.left)},${Math.round(r.top)} → ${Math.round(r.right)},${Math.round(r.bottom)}]`,
        })
    }

    // 2 ter) images (drapeaux) : chargées, ni déformées, ni rognées par leur cadre
    for (const img of document.querySelectorAll('img')) {
      const cs = getComputedStyle(img)
      if (cs.display === 'none' || cs.visibility === 'hidden') continue
      const what = `image ${img.getAttribute('src')}`
      if (!img.complete || img.naturalWidth === 0) {
        issues.push({ kind: 'image absente', what, detail: 'non chargée' })
        continue
      }
      const r = img.getBoundingClientRect()
      const bw = parseFloat(cs.borderLeftWidth) + parseFloat(cs.borderRightWidth)
      const bh = parseFloat(cs.borderTopWidth) + parseFloat(cs.borderBottomWidth)
      const shown = (r.width - bw) / (r.height - bh)
      const natural = img.naturalWidth / img.naturalHeight
      if (Math.abs(shown / natural - 1) > 0.03 && cs.objectFit !== 'contain')
        issues.push({ kind: 'image déformée', what, detail: `affichée ${shown.toFixed(2)}, réelle ${natural.toFixed(2)}` })
      const box = img.parentElement!.getBoundingClientRect()
      if (r.left < box.left - 1 || r.right > box.right + 1 || r.top < box.top - 1 || r.bottom > box.bottom + 1)
        issues.push({ kind: 'image rognée ou sortie de son cadre', what, detail: `${Math.round(r.width)}×${Math.round(r.height)}` })
    }

    // 2 bis) noms écrits sur la carte : visibles en entier, pas sous un ornement
    const ornaments = [...document.querySelectorAll('[data-evite-carte]')].map((e) => e.getBoundingClientRect())
    for (const tx of document.querySelectorAll('svg text')) {
      if (tx.closest('[data-evite-carte]')) continue
      const r = tx.getBoundingClientRect()
      if (r.width === 0) continue
      const label = `texte de carte « ${(tx.textContent ?? '').trim()} »`
      if (r.left < 0 || r.top < 0 || r.right > vw || r.bottom > vh)
        issues.push({ kind: 'nom de carte hors écran', what: label, detail: `${Math.round(r.left)},${Math.round(r.top)}` })
      for (const o of ornaments)
        if (!(r.right < o.left || r.left > o.right || r.bottom < o.top || r.top > o.bottom))
          issues.push({ kind: 'nom de carte sous un ornement', what: label, detail: `${Math.round(r.left)},${Math.round(r.top)}` })
    }

    // 3) éléments interactifs : visibles et non recouverts (on fait défiler leur zone si besoin)
    const interactive = document.querySelectorAll(
      'button, a[href], input:not([type=radio]):not([type=checkbox]), label.segment, label.case, [role=button], [role=radio], li[role=option]',
    )
    for (const el of interactive) {
      const cs = getComputedStyle(el)
      if (cs.display === 'none' || cs.visibility === 'hidden') continue
      if (el.closest('svg')) continue // marqueurs de carte : contrôlés à part
      const sc = scroller(el)
      if (sc && sc !== el) (el as HTMLElement).scrollIntoView({ block: 'nearest' })
      const r = el.getBoundingClientRect()
      if (r.width === 0 || r.height === 0) continue
      const cx = r.left + r.width / 2
      const cy = r.top + r.height / 2
      if (cx < 0 || cy < 0 || cx > vw || cy > vh) {
        issues.push({ kind: 'interactif hors écran', what: name(el), detail: `${Math.round(cx)},${Math.round(cy)}` })
        continue
      }
      const hit = document.elementFromPoint(cx, cy)
      if (!hit || !(hit === el || el.contains(hit) || hit.contains(el) || hit.closest('label') === el.closest('label')))
        issues.push({ kind: 'interactif recouvert', what: name(el), detail: hit ? name(hit) : 'rien' })
    }
    return issues
  })
}

/** Le centre d'un élément est-il au centre de son conteneur (à 2 px près) ? */
export async function centered(page: Page, sel: string, within: string | null = null) {
  const d = await page.evaluate(
    ([s, w]) => {
      const el = document.querySelector(s)!.getBoundingClientRect()
      const c = w ? document.querySelector(w)!.getBoundingClientRect() : { left: 0, width: innerWidth }
      return el.left + el.width / 2 - (c.left + c.width / 2)
    },
    [sel, within] as const,
  )
  expect(Math.abs(d), `${sel} centré`).toBeLessThan(2.5)
}

export async function check(page: Page, label: string) {
  await page.waitForTimeout(250)
  mkdirSync(CAPTURES, { recursive: true })
  await shot(page, `audit-${label}`)
  const issues = await audit(page)
  expect(issues, `${label} :\n${issues.map((i) => `${i.kind} : ${i.what} (${i.detail})`).join('\n')}`).toEqual([])
}

