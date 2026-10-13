<script lang="ts" module>
  export type MapView = 'atlas' | 'quiz' | 'voile'
  export type MapPick = 'fiche' | 'pays' | 'point' | 'aucun'
  export interface Highlight {
    id: string
    tone: 'question' | 'juste' | 'faux'
  }
  export interface Mark {
    lon: number
    lat: number
    kind: 'clic' | 'vrai'
  }
  export interface PickEvent {
    id: string | null
    lonlat: [number, number] | null
    /** nom d'une zone neutre cliquée (Bir Tawil…) */
    neutral?: string
  }
</script>

<script lang="ts">
  import { onMount, tick } from 'svelte'
  import { select, type Selection } from 'd3-selection'
  import { zoom, zoomIdentity, type ZoomBehavior, type ZoomTransform } from 'd3-zoom'
  import 'd3-transition'
  import { easeCubicInOut } from 'd3-ease'
  import type { GeoPath, GeoProjection } from 'd3-geo'
  import type { Dataset } from '../lib/data'
  import {
    OCEANS,
    PARALLELS,
    SPHERE,
    fitProjection,
    geoPath,
    makeProjection,
    type CountryFeature,
    type Pigment,
    type WorldGeo,
  } from '../lib/geo'
  import type { Ink } from '../lib/progress'
  import { reducedMotion } from '../lib/motion'
  import { BaseMap } from '../lib/basemap'

  interface Props {
    ds: Dataset
    world: WorldGeo
    inks: Map<string, Ink>
    pigments: Map<string, Pigment>
    view: MapView
    pick: MapPick
    highlights?: Highlight[]
    marks?: Mark[]
    /** entités « petites » à montrer en marqueur pendant un quiz */
    quizSmall?: string[]
    /** pays dont tous les faits sont découverts */
    complete?: Set<string>
    /** change quand un ornement apparaît ou disparaît (fiche, écran) : les noms se replacent */
    layoutKey?: string
    onpick?: (e: PickEvent) => void
  }

  let {
    ds,
    world,
    inks,
    pigments,
    view,
    pick,
    highlights = [],
    marks = [],
    quizSmall = [],
    complete = new Set(),
    layoutKey = '',
    onpick,
  }: Props = $props()

  let host: HTMLDivElement
  let svgEl: SVGSVGElement
  let canvasEl: HTMLCanvasElement
  let base: BaseMap | null = null
  let frame = 0
  let width = $state(1280)
  let height = $state(720)
  let transform = $state<ZoomTransform>(zoomIdentity)
  let zooming = $state(false)
  let hover = $state<{ name: string; x: number; y: number; neutral?: boolean } | null>(null)
  let drawn = $state(0) // incrémenté à chaque recalcul des chemins
  let relayout = $state(0)
  /** dernière transformation au repos : les noms sont placés pour elle */
  let stable = $state<ZoomTransform>(zoomIdentity)
  $effect(() => {
    void layoutKey
    tick().then(() => relayout++)
  })

  const projection: GeoProjection = makeProjection()
  let path: GeoPath = geoPath(projection)
  let zoomer: ZoomBehavior<SVGSVGElement, unknown>
  let zoomSel: Selection<SVGSVGElement, unknown, null, undefined>
  let pending = $state(new Set<string>())

  // Chemins précalculés (recalculés au redimensionnement)
  let dCountry = $state(new Map<string, string>())
  let dNeutral = $state<{ d: string; name: string }[]>([])
  let dSphere = $state('')

  /** Formes projetées des pays et zones neutres, pour tester où tombe un nom. */
  let shapes: { id: string; p: Path2D; b: [[number, number], [number, number]] }[] = []
  let shapeById = new Map<string, (typeof shapes)[number]>()
  let probe: CanvasRenderingContext2D | null = null

  /** Largeur réelle d'un nom calligraphié (IM FELL italique). */
  const widths = new Map<string, number>()
  function textWidth(text: string, size: number): number {
    const key = text + '|' + size.toFixed(1)
    const known = widths.get(key)
    if (known !== undefined) return known
    probe ??= document.createElement('canvas').getContext('2d')
    if (!probe) return text.length * size * 0.42
    probe.font = `italic ${size}px 'IM Fell English', serif`
    const w = probe.measureText(text).width
    widths.set(key, w)
    return w
  }

  /**
   * Un nom ne s'écrit que s'il ne déborde sur aucun autre pays (ni zone neutre) : on teste une grille de
   * points dans sa boîte. La mer est permise (noms d'îles), et le centre doit tomber dans le pays.
   */
  function labelFits(
    id: string,
    box: [number, number, number, number],
    t: ZoomTransform,
    discs: { id: string; x: number; y: number }[],
  ): boolean {
    probe ??= document.createElement('canvas').getContext('2d')
    if (!probe) return true
    const own = shapeById.get(id)
    // marge de 4 px (halo du texte, approximation de la mesure)
    const [x0, y0, x1, y1] = [box[0] - 4, box[1], box[2] + 4, box[3]]
    // marqueurs ronds des petites entités : un nom ne passe pas dessus
    for (const d of discs)
      if (d.id !== id && d.x > x0 - 9 && d.x < x1 + 9 && d.y > y0 - 9 && d.y < y1 + 9) return false
    const h = y1 - y0
    if (own) {
      // le centre du nom doit tomber dans le pays
      const [cx, cy] = t.invert([(x0 + x1) / 2, y0 + h * 0.6])
      if (!probe.isPointInPath(own.p, cx, cy)) return false
    }
    // seuls les voisins dont la boîte touche celle du nom sont testés
    const [[qx0, qy0], [qx1, qy1]] = [t.invert([x0, y0]), t.invert([x1, y1])]
    const near = shapes.filter(
      (sh) => sh.id !== id && !(sh.b[1][0] < qx0 || sh.b[0][0] > qx1 || sh.b[1][1] < qy0 || sh.b[0][1] > qy1),
    )
    // grille de 3 px sur la bande des lettres : même une mince pointe d'un voisin est vue
    const cols = Math.max(2, Math.ceil((x1 - x0) / 3))
    const rows = Math.max(2, Math.ceil((h * 0.65) / 3))
    for (let gy = 0; gy <= rows; gy++)
      for (let gx = 0; gx <= cols; gx++) {
        const sx = x0 + ((x1 - x0) * gx) / cols
        const sy = y0 + h * 0.2 + (h * 0.65 * gy) / rows
        const [px, py] = t.invert([sx, sy])
        if (own && probe.isPointInPath(own.p, px, py)) continue
        for (const sh of near) {
          const [[bx0, by0], [bx1, by1]] = sh.b
          if (px < bx0 || px > bx1 || py < by0 || py > by1) continue
          if (probe.isPointInPath(sh.p, px, py)) return false
        }
      }
    return true
  }

  function recompute() {
    const m = 12
    fitProjection(projection, m + 8, m, width - m - 8, height - m)
    path = geoPath(projection)
    const map = new Map<string, string>()
    for (const f of world.countries) map.set(f.properties.id, path(f) ?? '')
    dCountry = map
    dNeutral = world.neutral.map((f) => ({ d: path(f) ?? '', name: f.properties?.name_fr ?? 'zone sans État' }))
    shapes = [
      ...world.countries.map((f) => ({ id: f.properties.id, p: new Path2D(map.get(f.properties.id) ?? ''), b: path.bounds(f) })),
      ...world.neutral.map((f, i) => ({ id: 'neutre-' + i, p: new Path2D(path(f) ?? ''), b: path.bounds(f) })),
    ]
    shapeById = new Map(shapes.map((sh) => [sh.id, sh]))
    dSphere = path(SPHERE as never) ?? ''
    base?.resize(width, height)
    base?.draw(transform)
    drawn++
  }

  /** Point écran (px dans la carte) d'une coordonnée, transform courante incluse. */
  function screen(lon: number, lat: number, t: ZoomTransform = transform): [number, number] | null {
    const p = projection([lon, lat])
    if (!p) return null
    return t.apply(p)
  }

  function labelPoint(id: string): [number, number] | null {
    const c = ds.byId.get(id)
    if (c?.label) return [c.label.lon, c.label.lat]
    const f = world.byId.get(id)
    if (!f) return null
    const p = path.centroid(f)
    const ll = projection.invert?.(p)
    return ll ? [ll[0], ll[1]] : null
  }

  // ---------- états visuels ----------

  function countryClass(id: string): string {
    const known = ds.byId.has(id)
    if (view !== 'atlas') return 'pays crayon' + (known ? '' : ' muet')
    const ink = inks.get(id)
    if (!ink || pending.has(id)) return 'pays inconnu'
    if (ink.level === 0) return ink.ghost ? 'pays efface' : 'pays inconnu'
    return `pays encre-${ink.level}`
  }

  function countryOpacity(id: string): number {
    if (view !== 'atlas') return 1
    const ink = inks.get(id)
    return ink && ink.level > 0 ? ink.fade : 1
  }

  const washIds = $derived(
    view === 'atlas'
      ? world.countries
          .map((f) => f.properties.id)
          .filter((id) => (inks.get(id)?.level ?? 0) >= 2 && !pending.has(id))
      : [],
  )

  const highlightMap = $derived(new Map(highlights.map((h) => [h.id, h.tone])))

  interface Label {
    id: string
    name: string
    /** ancre géographique : pendant un geste, le nom suit la carte sans être replacé */
    lon: number
    lat: number
    size: number
    fade: number
    complete: boolean
  }

  /** Noms calligraphiés (3 modes) ; gloutons par taille, sans chevauchement. */
  const labels = $derived.by((): Label[] => {
    void drawn
    void relayout
    if (view !== 'atlas') return []
    const t = stable
    const out: Label[] = []
    const boxes: [number, number, number, number][] = []
    const blocked = obstacles()
    // marqueurs ronds visibles (petites entités encrées)
    const discs = ds.countries
      .filter((c) => c.small && c.label && ((inks.get(c.id)?.level ?? 0) > 0 || inks.get(c.id)?.ghost))
      .map((c) => {
        const q = screen(c.label!.lon, c.label!.lat, t)
        return q ? { id: c.id, x: q[0], y: q[1] } : null
      })
      .filter((d): d is { id: string; x: number; y: number } => !!d)
    const cands = ds.countries
      .filter((c) => (inks.get(c.id)?.level ?? 0) >= 3 && !pending.has(c.id))
      .map((c) => {
        const f = world.byId.get(c.id)
        const area = f ? path.area(f) * t.k * t.k : 0
        return { c, area }
      })
      .sort((a, b) => b.area - a.area)
    for (const { c, area } of cands) {
      const lp = labelPoint(c.id)
      if (!lp) continue
      const p = screen(lp[0], lp[1], t)
      if (!p) continue
      // les petites entités ne sont nommées qu'une fois zoomé
      if (c.small && t.k < 3) continue
      // du plus grand corps au plus petit (14 px au moins) : le premier qui tient dans le pays
      const start = Math.max(14, Math.min(26, Math.sqrt(area) / 5))
      for (let size = start; size >= 14; size -= 2) {
        const w = textWidth(c.name_fr, size) + (complete.has(c.id) ? size * 0.5 : 0)
        const box: [number, number, number, number] = [p[0] - w / 2, p[1] - size * 0.95, p[0] + w / 2, p[1] + size * 0.3]
        // entièrement visible, dans l'ovale, hors des ornements posés sur la carte
        if (box[0] < 8 || box[2] > width - 8 || box[1] < 8 || box[3] > height - 8) break
        if (!inSphere(box[0], box[1], t) || !inSphere(box[2], box[3], t) || !inSphere(box[0], box[3], t) || !inSphere(box[2], box[1], t)) break
        if (blocked.some((b) => !(box[2] < b[0] || box[0] > b[2] || box[3] < b[1] || box[1] > b[3]))) break
        if (boxes.some((b) => !(box[2] < b[0] || box[0] > b[2] || box[3] < b[1] || box[1] > b[3]))) continue
        if (!labelFits(c.id, box, t, discs)) continue
        boxes.push(box)
        const ink = inks.get(c.id)!
        out.push({ id: c.id, name: c.name_fr, lon: lp[0], lat: lp[1], size, fade: ink.fade, complete: complete.has(c.id) })
        break
      }
    }
    return out
  })

  /** Le point écran est-il dans l'ovale du monde ? */
  function inSphere(x: number, y: number, t: ZoomTransform): boolean {
    const [px, py] = t.invert([x, y])
    const ll = projection.invert?.([px, py])
    if (!ll || !isFinite(ll[0]) || !isFinite(ll[1])) return false
    const back = projection(ll)
    return !!back && Math.hypot(back[0] - px, back[1] - py) < 1
  }

  /** Rectangles (repère carte) des ornements posés sur la carte : cartouche, rose, carnet, panneaux. */
  function obstacles(): [number, number, number, number][] {
    if (!host) return []
    const r0 = host.getBoundingClientRect()
    return [...document.querySelectorAll('[data-evite-carte]')].map((el) => {
      const r = el.getBoundingClientRect()
      return [r.left - r0.left - 6, r.top - r0.top - 6, r.right - r0.left + 6, r.bottom - r0.top + 6]
    })
  }

  interface Marker {
    id: string
    x: number
    y: number
    cls: string
    opacity: number
  }

  const markers = $derived.by((): Marker[] => {
    void drawn
    const t = transform
    const ids =
      view === 'atlas'
        ? ds.countries.filter((c) => c.small && ((inks.get(c.id)?.level ?? 0) > 0 || inks.get(c.id)?.ghost)).map((c) => c.id)
        : quizSmall
    const out: Marker[] = []
    for (const id of ids) {
      if (pending.has(id)) continue
      const c = ds.byId.get(id)
      if (!c?.label) continue
      const p = screen(c.label.lon, c.label.lat, t)
      if (!p) continue
      const tone = highlightMap.get(id)
      let cls = view === 'atlas' ? countryClass(id).replace('pays', 'marqueur') : 'marqueur crayon'
      if (tone) cls += ' surligne-' + tone
      out.push({ id, x: p[0], y: p[1], cls, opacity: countryOpacity(id) })
    }
    return out
  })

  const markPoints = $derived(
    marks
      .map((m) => ({ ...m, p: screen(m.lon, m.lat, transform) }))
      .filter((m): m is Mark & { p: [number, number] } => !!m.p),
  )

  /** Pointillé du grand cercle entre le clic et la vraie position. */
  const markLine = $derived.by(() => {
    const a = marks.find((m) => m.kind === 'clic')
    const b = marks.find((m) => m.kind === 'vrai')
    if (!a || !b) return ''
    const line = { type: 'LineString' as const, coordinates: [[a.lon, a.lat], [b.lon, b.lat]] }
    return path(line as never) ?? ''
  })

  /** Une étiquette fixe (océan, parallèle) n'est montrée que si elle est libre et visible. */
  function freeSpot(p: [number, number] | null, w: number, h: number): boolean {
    if (!p) return false
    const box = [p[0] - w / 2, p[1] - h, p[0] + w / 2, p[1] + 4]
    if (box[0] < 4 || box[2] > width - 4 || box[1] < 4 || box[3] > height - 4) return false
    return !obstacles().some((b) => !(box[2] < b[0] || box[0] > b[2] || box[3] < b[1] || box[1] > b[3]))
  }

  const oceanLabels = $derived.by(() => {
    void drawn
    void relayout
    return OCEANS.map((o) => ({ ...o, p: screen(o.lon, o.lat, transform) })).filter((o) =>
      freeSpot(o.p, o.name.length * 11, 16),
    )
  })

  const parallelLabels = $derived.by(() => {
    void drawn
    void relayout
    return PARALLELS.filter((p) => Math.abs(p.lat) < 60)
      .map((p) => ({ name: p.name, p: screen(-138, p.lat + 0.9, transform) }))
      .filter((p) => freeSpot(p.p, p.name.length * 6, 13))
  })

  // ---------- interaction ----------

  function eventPoint(ev: MouseEvent): [number, number] {
    const r = svgEl.getBoundingClientRect()
    return [ev.clientX - r.left, ev.clientY - r.top]
  }

  function lonlatAt(ev: MouseEvent): [number, number] | null {
    const [x, y] = transform.invert(eventPoint(ev))
    const ll = projection.invert?.([x, y])
    if (!ll || !isFinite(ll[0]) || !isFinite(ll[1])) return null
    // hors de l'ovale : l'inverse de Hammer renvoie des valeurs, on vérifie l'aller-retour
    const back = projection(ll)
    if (!back || Math.hypot(back[0] - x, back[1] - y) > 1) return null
    return [ll[0], ll[1]]
  }

  function clickable(id: string): boolean {
    if (pick === 'pays') return true
    if (pick === 'fiche') {
      const ink = inks.get(id)
      return ds.byId.has(id) && !!ink && (ink.level > 0 || ink.ghost)
    }
    return false
  }

  function onSvgClick(ev: MouseEvent) {
    if (pick === 'aucun' || pick === 'fiche') return
    const target = (ev.target as Element).closest('[data-id]') as SVGElement | null
    const id = target?.dataset.id ?? null
    const neutral = ((ev.target as Element).closest('[data-neutre]') as SVGElement | null)?.dataset.neutre
    const lonlat = lonlatAt(ev)
    if (pick === 'point') {
      if (lonlat) onpick?.({ id: null, lonlat })
      return
    }
    if (id || lonlat) onpick?.({ id, lonlat, neutral })
  }

  function onCountryClick(ev: MouseEvent, id: string) {
    if (pick !== 'fiche') return
    if (!clickable(id)) return
    ev.stopPropagation()
    onpick?.({ id, lonlat: lonlatAt(ev) })
  }

  function onMove(ev: MouseEvent) {
    if (zooming) {
      hover = null
      return
    }
    const [x, y] = eventPoint(ev)
    // zone neutre : son nom, sans jugement, dans tous les écrans (sauf pendant « nommer »)
    const neutral = ((ev.target as Element).closest('[data-neutre]') as SVGElement | null)?.dataset.neutre
    if (neutral) {
      hover = { name: neutral, x, y, neutral: true }
      return
    }
    if (view !== 'atlas') {
      hover = null
      return
    }
    const el = (ev.target as Element).closest('[data-id]') as SVGElement | null
    const id = el?.dataset.id
    const c = id ? ds.byId.get(id) : null
    if (id && c && clickable(id)) hover = { name: c.name_fr, x, y }
    else hover = null
  }

  function onKeyMarker(ev: KeyboardEvent, id: string) {
    if (ev.key === 'Enter' || ev.key === ' ') {
      ev.preventDefault()
      const c = ds.byId.get(id)
      onpick?.({ id, lonlat: c?.label ? [c.label.lon, c.label.lat] : null })
    }
  }

  // ---------- zoom ----------

  function duration(ms: number) {
    return reducedMotion() ? 0 : ms
  }

  export function reset(ms = 650) {
    zoomSel.transition().duration(duration(ms)).ease(easeCubicInOut).call(zoomer.transform, zoomIdentity)
  }

  export function zoomBy(f: number) {
    zoomSel.transition().duration(duration(250)).call(zoomer.scaleBy, f)
  }

  /**
   * Zoom animé sur un pays, dans la zone libre (sans les panneaux).
   * `context` > 1 garde du voisinage autour du pays.
   */
  export function zoomTo(
    id: string,
    opts: { right?: number; top?: number; bottom?: number; context?: number; maxK?: number } = {},
  ): Promise<void> {
    const { right = 0, top = 0, bottom = 0, context = 3, maxK = 12 } = opts
    const f = world.byId.get(id)
    let x0: number, y0: number, x1: number, y1: number
    if (f && !ds.byId.get(id)?.small) {
      ;[[x0, y0], [x1, y1]] = path.bounds(f)
      // Pays coupés par le bord (Russie, Fidji) : on garde les bornes du point d'étiquette.
      if (x1 - x0 > width * 0.6) {
        const lp = labelPoint(id)
        const p = lp && projection(lp)
        if (p) [x0, y0, x1, y1] = [p[0] - 60, p[1] - 40, p[0] + 60, p[1] + 40]
      }
    } else {
      const lp = labelPoint(id)
      const p = lp && projection(lp)
      if (!p) return Promise.resolve()
      ;[x0, y0, x1, y1] = [p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6]
    }
    const aw = width - right
    const ah = height - top - bottom
    const bw = Math.max(x1 - x0, 4) * context
    const bh = Math.max(y1 - y0, 4) * context
    const k = Math.max(1, Math.min(maxK, Math.min(aw / bw, ah / bh)))
    const cx = (x0 + x1) / 2
    const cy = (y0 + y1) / 2
    const centered = (kk: number) =>
      zoomIdentity
        .translate(aw / 2, top + ah / 2)
        .scale(kk)
        .translate(-cx, -cy)
    // La transition de d3 n'applique pas les bornes de déplacement : on contraint nous-mêmes, puis on
    // zoome davantage tant que le pays ne tient pas dans la zone libre (bord de l'ovale, cartouche).
    const constrain = zoomer.constrain()
    const ext: [[number, number], [number, number]] = [
      [0, 0],
      [width, height],
    ]
    const fits = (tt: ZoomTransform) => {
      const [ax, ay] = tt.apply([x0, y0])
      const [bx, by] = tt.apply([x1, y1])
      return ay >= top + 4 && by <= height - bottom - 4 && ax >= 4 && bx <= aw - 4
    }
    let t = constrain(centered(k), ext, zoomer.translateExtent())
    for (let kk = k; !fits(t) && kk < maxK; ) {
      kk = Math.min(maxK, kk * 1.15)
      t = constrain(centered(kk), ext, zoomer.translateExtent())
    }
    return new Promise((resolve) => {
      zoomSel
        .transition()
        .duration(duration(900))
        .ease(easeCubicInOut)
        .call(zoomer.transform, t)
        .on('end interrupt', () => resolve())
    })
  }

  /**
   * À l'échelle du monde, le pays est-il visible sans être caché par un ornement de la question ?
   * `covers` : rectangles (coordonnées de page) du cartouche, des réponses, etc.
   */
  export function fitsFree(id: string, covers: { left: number; top: number; right: number; bottom: number }[]): boolean {
    const f = world.byId.get(id)
    if (!f) return false
    const r0 = host.getBoundingClientRect()
    const [[x0, y0], [x1, y1]] = path.bounds(f)
    const b = [x0 + r0.left, y0 + r0.top, x1 + r0.left, y1 + r0.top]
    if (b[0] < 4 || b[2] > r0.width - 4) return x1 - x0 > width * 0.6 // coupé par le bord de l'ovale
    return !covers.some((c) => !(b[2] < c.left || b[0] > c.right || b[3] < c.top || b[1] > c.bottom))
  }

  /** Le pays est-il trop petit pour être vu à l'échelle du monde ? */
  export function needsZoom(id: string): boolean {
    const f = world.byId.get(id)
    if (!f || ds.byId.get(id)?.small) return true
    const [[x0, y0], [x1, y1]] = path.bounds(f)
    return Math.max(x1 - x0, y1 - y0) < 28
  }

  /**
   * Bornes de déplacement : l'ovale plus 20 % de papier autour (le canvas en dessine 25 %), pour qu'un
   * pays collé au bord puisse être amené hors du cartouche de la question.
   */
  function panExtent(): [[number, number], [number, number]] {
    return [
      [-width * 0.2, -height * 0.2],
      [width * 1.2, height * 1.2],
    ]
  }

  /** Le geste mémorable : les pays gagnés se tracent un à un, puis le lavis se dépose. */
  export async function animateInk(ids: string[], onstroke?: () => void): Promise<void> {
    const todo = ids.filter((id) => world.byId.has(id) || ds.byId.get(id)?.label)
    if (!todo.length) return
    if (reducedMotion()) return
    pending = new Set(todo)
    const layer = select(svgEl).select<SVGGElement>('g.trace')
    const stagger = Math.max(120, Math.min(420, 2400 / todo.length))
    await new Promise((r) => setTimeout(r, 350))
    const runs = todo.map(
      (id, i) =>
        new Promise<void>((resolve) => {
          setTimeout(() => {
            const d = dCountry.get(id)
            if (!d) {
              const next = new Set(pending)
              next.delete(id)
              pending = next
              resolve()
              return
            }
            const p = layer.append('path').attr('d', d).attr('class', 'trace-encre').node()!
            if (i < 8) onstroke?.() // au-delà, le grattement deviendrait un bruit de fond
            const len = p.getTotalLength()
            const anim = p.animate(
              [
                { strokeDasharray: `${len} ${len}`, strokeDashoffset: len },
                { strokeDasharray: `${len} ${len}`, strokeDashoffset: 0 },
              ],
              { duration: Math.min(1400, 500 + len * 2), easing: 'ease-in-out', fill: 'forwards' },
            )
            anim.onfinish = () => {
              const next = new Set(pending)
              next.delete(id)
              pending = next
              setTimeout(() => p.remove(), 900)
              resolve()
            }
          }, i * stagger)
        }),
    )
    await Promise.all(runs)
  }

  /** Pour les tests de bout en bout : position écran (page) d'un pays ou d'un point. */
  function exposeForTests() {
    const page = (p: [number, number] | null) => {
      if (!p) return null
      const r = svgEl.getBoundingClientRect()
      return [r.left + p[0], r.top + p[1]]
    }
    ;(window as unknown as Record<string, unknown>).__atlas = {
      point: (lon: number, lat: number) => page(screen(lon, lat)),
      country: (id: string) => {
        const lp = labelPoint(id)
        return lp ? page(screen(lp[0], lp[1])) : null
      },
      transform: () => ({ k: transform.k, x: transform.x, y: transform.y }),
      zoomTo: (id: string, context = 4, maxK = 12) => zoomTo(id, { context, maxK }),
      timeDraw: () => {
        const t0 = performance.now()
        base?.draw(transform)
        canvasEl.getContext('2d')!.getImageData(0, 0, 1, 1)
        return performance.now() - t0
      },
    }
  }

  onMount(() => {
    const ro = new ResizeObserver(() => {
      const r = host.getBoundingClientRect()
      if (Math.abs(r.width - width) > 0.5 || Math.abs(r.height - height) > 0.5 || !dSphere) {
        width = r.width
        height = r.height
        recompute()
        zoomer?.translateExtent(panExtent())
        zoomer?.extent([
          [0, 0],
          [width, height],
        ])
      }
    })
    const r = host.getBoundingClientRect()
    width = r.width
    height = r.height
    base = new BaseMap(canvasEl, ds.world, projection)
    recompute()
    zoomSel = select(svgEl)
    zoomer = zoom<SVGSVGElement, unknown>()
      .scaleExtent([1, 60])
      .extent([
        [0, 0],
        [width, height],
      ])
      .translateExtent(panExtent())
      .on('start', () => (zooming = true))
      .on('zoom', (e) => {
        transform = e.transform
        // l'image suivie ne couvre plus l'écran : un redessin, au plus un par image
        if (base && !base.follow(transform) && !frame)
          frame = requestAnimationFrame(() => {
            frame = 0
            base?.draw(transform)
          })
      })
      .on('end', () => {
        zooming = false
        stable = transform
        if (!frame)
          frame = requestAnimationFrame(() => {
            frame = 0
            base?.draw(transform)
          })
      })
    zoomSel.call(zoomer).on('dblclick.zoom', null)
    ro.observe(host)
    exposeForTests()
    document.fonts?.ready.then(() => {
      widths.clear() // mesures prises avant le chargement de la fonte
      relayout++
    })
    return () => ro.disconnect()
  })

  function featureD(f: CountryFeature) {
    return dCountry.get(f.properties.id) ?? ''
  }

</script>

<div class="carte" class:voile={view === 'voile'} class:quiz={view === 'quiz'} bind:this={host}>
  <canvas bind:this={canvasEl} class="fond" aria-hidden="true"></canvas>
  <!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_noninteractive_element_interactions -->
  <svg
    bind:this={svgEl}
    viewBox="0 0 {width} {height}"
    width={width}
    height={height}
    class:zooming
    class:viser={pick === 'point' || pick === 'pays'}
    role="img"
    aria-label="Carte du monde"
    onclick={onSvgClick}
    onmousemove={onMove}
    onmouseleave={() => (hover = null)}
  >
    <defs>
      <clipPath id="clip-sphere"><path d={dSphere} /></clipPath>
      {#each washIds as id (id)}
        <clipPath id="clip-{id}"><path d={dCountry.get(id)} /></clipPath>
      {/each}
      <pattern id="hachure-neutre" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)">
        <line x1="0" y1="0" x2="0" y2="4" class="hachure-neutre-trait" />
      </pattern>
      <pattern id="hachure" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
        <line x1="0" y1="0" x2="0" y2="5" class="hachure-trait" />
      </pattern>
    </defs>

    <g transform={transform.toString()}>
      <!-- mer, lignes d'eau, graticule et terres : canvas dessous (lib/basemap.ts) ; ici, une
           surface invisible pour les clics en mer -->
      <path d={dSphere} class="mer" />

      <g class="pays-calque">
        {#each world.countries as f (f.properties.id)}
          {@const id = f.properties.id}
          {@const tone = highlightMap.get(id)}
          <!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
          <path
            d={featureD(f)}
            data-id={id}
            class={countryClass(id) + (tone ? ' surligne-' + tone : '') + (clickable(id) ? ' cliquable' : '')}
            style:opacity={countryOpacity(id)}
            onclick={(e) => onCountryClick(e, id)}
          />
        {/each}
      </g>

      <!-- zones neutres (Crimée, Golan, Bir Tawil…) : hachures grises, jamais une couleur de pays -->
      {#each dNeutral as n, i (i)}
        <path d={n.d} class="neutre" data-neutre={n.name} />
      {/each}

      <g class="lavis-calque">
        {#each washIds as id (id)}
          <g class="lavis pigment-{pigments.get(id) ?? 'vert'}" style:opacity={countryOpacity(id)}>
            <path d={dCountry.get(id)} class="lavis-fond" />
            <path d={dCountry.get(id)} class="lavis-bord" clip-path="url(#clip-{id})" />
          </g>
        {/each}
      </g>

      {#each highlights as h (h.id)}
        {#if dCountry.get(h.id) && !ds.byId.get(h.id)?.small}
          <path d={dCountry.get(h.id)} class="surlignage ton-{h.tone}" />
        {/if}
      {/each}

      {#if markLine}
        <path d={markLine} class="ligne-distance" />
      {/if}

      <g class="trace"></g>
      <path d={dSphere} class="cadre-ovale" />
      <path d={dSphere} class="cadre-ovale-fin" />
    </g>

    <!-- calque écran : textes et marqueurs à taille constante -->
    <g class="ecran">
      {#if view !== 'quiz'}
        {#each oceanLabels as o (o.name + o.lon)}
          <text x={o.p![0]} y={o.p![1]} class="ocean">{o.name}</text>
        {/each}
        {#each parallelLabels as p (p.name)}
          {#if p.p}<text x={p.p[0]} y={p.p[1]} class="nom-parallele">{p.name}</text>{/if}
        {/each}
      {/if}
      {#each markers as m (m.id)}
        <!-- svelte-ignore a11y_no_noninteractive_tabindex -->
        <g
          class={m.cls}
          data-id={m.id}
          style:opacity={m.opacity}
          transform="translate({m.x},{m.y})"
          role={pick === 'pays' || (pick === 'fiche' && clickable(m.id)) ? 'button' : undefined}
          tabindex={pick === 'pays' || (pick === 'fiche' && clickable(m.id)) ? 0 : undefined}
          aria-label={pick === 'fiche' ? ds.byId.get(m.id)?.name_fr : 'Petite entité'}
          onkeydown={(e) => onKeyMarker(e, m.id)}
          onclick={(e) => onCountryClick(e, m.id)}
        >
          <circle r={transform.k < 3 ? 7 : 11} class="marqueur-zone" />
          {#if highlightMap.get(m.id)}<circle r="13" class="marqueur-anneau" />{/if}
          <circle r="4.5" class="marqueur-point" />
        </g>
      {/each}
      {#each labels as l (l.id)}
        {@const lp = screen(l.lon, l.lat) ?? [-999, -999]}
        <text x={lp[0]} y={lp[1]} class="nom-pays" data-pays={l.id} style:font-size="{l.size}px" style:opacity={l.fade}>
          {l.name}{#if l.complete}<tspan class="asterisque" dx="2" dy={-l.size * 0.35}>*</tspan>{/if}
        </text>
      {/each}
      {#each markPoints as m (m.kind)}
        <g class="repere repere-{m.kind}" transform="translate({m.p[0]},{m.p[1]})">
          {#if m.kind === 'vrai'}
            <path d="M0 -9 L2.2 -2.2 L9 0 L2.2 2.2 L0 9 L-2.2 2.2 L-9 0 L-2.2 -2.2 Z" />
          {:else}
            <path d="M-5 -5 L5 5 M5 -5 L-5 5" />
          {/if}
        </g>
      {/each}
    </g>
  </svg>

  {#if hover}
    <div class="bulle" class:neutre-bulle={hover.neutral} style:left="{hover.x}px" style:top="{hover.y}px">
      {hover.name}{#if hover.neutral}<span class="neutre-note"> : zone sans État</span>{/if}
    </div>
  {/if}
</div>

<style>
  .carte {
    position: absolute;
    inset: 0;
    overflow: hidden;
  }
  svg {
    display: block;
    cursor: grab;
    user-select: none;
  }
  svg:active {
    cursor: grabbing;
  }
  svg.viser {
    cursor: crosshair;
  }
  .voile svg {
    opacity: 0.38;
    filter: saturate(0.5);
  }

  .fond {
    position: absolute;
    left: 0;
    top: 0;
    pointer-events: none;
  }
  svg {
    position: relative;
  }
  .voile .fond {
    opacity: 0.38;
    filter: saturate(0.5);
  }
  .mer {
    fill: transparent;
  }
  .pays {
    vector-effect: non-scaling-stroke;
    stroke-linejoin: round;
    transition: opacity 600ms;
  }
  .pays.inconnu {
    fill: none;
    stroke: none;
    pointer-events: none;
  }
  .pays.efface {
    fill: none;
    stroke: var(--encre);
    stroke-opacity: 0.32;
    stroke-width: 0.8;
    stroke-dasharray: 3 3;
  }
  .pays.encre-1,
  .pays.encre-2,
  .pays.encre-3 {
    fill: var(--encre);
    fill-opacity: 0.035;
    stroke: var(--encre);
    stroke-width: 1.1;
  }
  .pays.encre-3 {
    stroke-width: 1.3;
  }
  .pays.cliquable {
    cursor: pointer;
  }
  .pays.cliquable:hover {
    fill-opacity: 0.1;
  }
  .pays.crayon {
    fill: var(--velin-clair);
    fill-opacity: 0.01;
    stroke: var(--crayon);
    stroke-width: 0.7;
    cursor: crosshair;
  }
  .viser .pays.crayon:hover {
    fill: var(--prusse);
    fill-opacity: 0.12;
  }
  .pays.crayon.muet {
    stroke-opacity: 0.7;
  }

  .neutre {
    fill: url(#hachure-neutre);
    stroke: var(--crayon);
    stroke-width: 0.6;
    stroke-dasharray: 2 2;
    vector-effect: non-scaling-stroke;
  }
  .lavis {
    pointer-events: none;
    animation: depot 900ms ease-out both;
  }
  @keyframes depot {
    from {
      opacity: 0;
    }
  }
  .lavis-fond {
    fill-opacity: 0.13;
    stroke: none;
  }
  .lavis-bord {
    fill: none;
    stroke-width: 9;
    stroke-opacity: 0.5;
    vector-effect: non-scaling-stroke;
    stroke-linejoin: round;
  }
  .pigment-vert {
    fill: var(--vert);
    stroke: var(--vert);
  }
  .pigment-carmin {
    fill: var(--carmin);
    stroke: var(--carmin);
  }
  .pigment-gutte {
    fill: var(--gutte);
    stroke: var(--gutte);
  }
  .pigment-prusse {
    fill: var(--prusse);
    stroke: var(--prusse);
  }

  .surlignage {
    pointer-events: none;
    vector-effect: non-scaling-stroke;
    stroke-width: 2;
    stroke-linejoin: round;
  }
  .surlignage.ton-question {
    fill: url(#hachure);
    stroke: var(--prusse);
  }
  .surlignage.ton-juste {
    fill: var(--vert);
    fill-opacity: 0.35;
    stroke: var(--vert);
  }
  .surlignage.ton-faux {
    fill: var(--carmin);
    fill-opacity: 0.18;
    stroke: var(--carmin);
    stroke-dasharray: 4 3;
  }
  :global(.hachure-neutre-trait) {
    stroke: var(--crayon);
    stroke-width: 0.8;
    stroke-opacity: 0.7;
  }
  .neutre-note {
    font-family: var(--texte);
    font-size: var(--t-14);
    font-style: normal;
    color: var(--encre-2);
  }
  :global(.hachure-trait) {
    stroke: var(--prusse);
    stroke-width: 1.6;
  }

  .ligne-distance {
    fill: none;
    stroke: var(--encre);
    stroke-width: 1.2;
    stroke-dasharray: 2 4;
    stroke-linecap: round;
    vector-effect: non-scaling-stroke;
  }

  .cadre-ovale {
    fill: none;
    stroke: var(--encre);
    stroke-width: 2.4;
    vector-effect: non-scaling-stroke;
    pointer-events: none;
  }
  .cadre-ovale-fin {
    fill: none;
    stroke: var(--velin-clair);
    stroke-width: 0.9;
    vector-effect: non-scaling-stroke;
    pointer-events: none;
  }

  :global(.trace-encre) {
    fill: none;
    stroke: var(--encre);
    stroke-width: 1.6;
    vector-effect: non-scaling-stroke;
    stroke-linejoin: round;
    pointer-events: none;
  }

  .ecran text {
    pointer-events: none;
  }
  .ocean {
    font-family: 'Alegreya SC', serif;
    font-size: 15px;
    letter-spacing: 0.32em;
    fill: var(--prusse);
    fill-opacity: 0.62;
    text-anchor: middle;
  }
  .nom-parallele {
    font-family: 'Alegreya', serif;
    font-style: italic;
    font-size: 12px;
    fill: var(--encre);
    fill-opacity: 0.5;
    text-anchor: middle;
  }
  .nom-pays {
    font-family: 'IM Fell English', serif;
    font-style: italic;
    fill: var(--encre);
    text-anchor: middle;
    paint-order: stroke;
    stroke: var(--velin-clair);
    stroke-width: 3px;
    stroke-opacity: 0.8;
  }
  .asterisque {
    font-style: normal;
    fill: var(--carmin);
  }

  .marqueur-zone {
    fill: transparent;
    stroke: none;
  }
  .marqueur-anneau {
    fill: none;
    stroke: var(--prusse);
    stroke-width: 1.5;
    stroke-dasharray: 3 2;
  }
  .marqueur-point {
    fill: var(--velin-clair);
    stroke: var(--encre);
    stroke-width: 1.4;
  }
  :global(.marqueur) {
    cursor: pointer;
  }
  :global(.marqueur.crayon) .marqueur-point {
    stroke: var(--crayon);
  }
  :global(.marqueur.crayon:hover) .marqueur-point {
    fill: var(--prusse);
    fill-opacity: 0.25;
    stroke: var(--prusse);
  }
  :global(.marqueur.efface) .marqueur-point {
    stroke-dasharray: 2 2;
    stroke-opacity: 0.4;
  }
  :global(.marqueur.encre-2) .marqueur-point,
  :global(.marqueur.encre-3) .marqueur-point {
    fill: var(--vert);
    fill-opacity: 0.5;
  }
  :global(.marqueur.surligne-question) .marqueur-point {
    fill: var(--prusse);
    stroke: var(--prusse);
    r: 6;
  }
  :global(.marqueur.surligne-juste) .marqueur-point {
    fill: var(--vert);
    stroke: var(--vert);
    r: 6;
  }
  :global(.marqueur.surligne-faux) .marqueur-point {
    fill: var(--carmin);
    stroke: var(--carmin);
  }
  :global(.marqueur:focus-visible) {
    outline: none;
  }
  :global(.marqueur:focus-visible) .marqueur-zone {
    stroke: var(--prusse);
    stroke-width: 2;
  }

  .repere path {
    fill: var(--encre);
    stroke: var(--encre);
    stroke-width: 2;
    stroke-linecap: round;
  }
  .repere-vrai path {
    fill: var(--vert);
    stroke: var(--encre);
    stroke-width: 1;
  }
  .repere-clic path {
    stroke: var(--carmin);
    stroke-width: 2.4;
  }

  .bulle {
    position: absolute;
    transform: translate(12px, -130%);
    pointer-events: none;
    font-family: 'IM Fell English', serif;
    font-style: italic;
    font-size: 19px;
    color: var(--encre);
    background: var(--velin-clair);
    border: 1px solid var(--encre);
    padding: 1px 8px 2px;
    white-space: nowrap;
  }
</style>
