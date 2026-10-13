// Fond de carte en canvas : mer, lignes d'eau gravées, graticule, parallèles, terres en pointillé.
// Les traits très larges des lignes d'eau coûtent ~200 ms par dessin, même sur GPU : le canvas n'est
// redessiné qu'en fin de geste ; pendant le geste il suit le zoom par une transformation CSS
// (voir AtlasMap), et il déborde de l'écran d'une marge pour qu'un déplacement ne montre pas de vide.
import { geoPath, type GeoProjection } from 'd3-geo'
import { feature } from 'topojson-client'
import { presimplify, simplify } from 'topojson-simplify'
import type { Topology } from 'topojson-specification'
import { PARALLELS, SPHERE, graticule, parallel } from './geo'

export interface View {
  k: number
  x: number
  y: number
}

const RINGS = 6
const GAP = 3.6 // px entre deux lignes d'eau, constant à l'écran
/** marge du canvas autour de l'écran, en fraction de sa taille */
export const MARGIN = 0.25

function cssVar(name: string, fallback: string): string {
  try {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback
  } catch {
    return fallback
  }
}

export class BaseMap {
  private ctx: CanvasRenderingContext2D
  private topo: Topology
  private projection: GeoProjection
  private levels = new Map<string, Path2D>()
  /** transformation du dernier dessin */
  drawn: View = { k: 1, x: 0, y: 0 }
  private sphere!: Path2D
  private grat!: Path2D
  private parallels: { lat: number; p: Path2D }[] = []
  private colors = {
    paper: cssVar('--velin-clair', '#e9e2ce'),
    prusse: cssVar('--prusse', '#1d3a5a'),
    encre: cssVar('--encre', '#2b1f17'),
  }
  private width = 0
  private height = 0
  private dpr = 1

  constructor(
    private canvas: HTMLCanvasElement,
    topo: Topology,
    projection: GeoProjection,
  ) {
    this.ctx = canvas.getContext('2d')!
    // les poids sont calculés une fois ; chaque niveau de zoom filtre à sa propre finesse
    this.topo = presimplify(JSON.parse(JSON.stringify(topo)) as never) as Topology
    this.projection = projection
  }

  /** À appeler quand la projection a été réajustée (redimensionnement). */
  resize(width: number, height: number) {
    this.width = width
    this.height = height
    this.dpr = Math.min(2, window.devicePixelRatio || 1)
    const cw = width * (1 + 2 * MARGIN)
    const ch = height * (1 + 2 * MARGIN)
    this.canvas.width = Math.round(cw * this.dpr)
    this.canvas.height = Math.round(ch * this.dpr)
    this.canvas.style.width = cw + 'px'
    this.canvas.style.height = ch + 'px'
    this.canvas.style.left = -width * MARGIN + 'px'
    this.canvas.style.top = -height * MARGIN + 'px'
    this.canvas.style.transformOrigin = `${width * MARGIN}px ${height * MARGIN}px`
    const path = geoPath(this.projection)
    this.levels.clear()
    this.sphere = new Path2D(path(SPHERE as never) ?? '')
    this.grat = new Path2D(path(graticule()) ?? '')
    this.parallels = PARALLELS.map((p) => ({ lat: p.lat, p: new Path2D(path(parallel(p.lat)) ?? '') }))
  }

  /**
   * Côtes simplifiées pour ce zoom (niveaux par puissances de 2, mis en cache) ;
   * `tolPx` : finesse à l'écran (les anneaux du large n'ont pas besoin du détail de la côte).
   */
  private land(k: number, tolPx: number): Path2D {
    const level = Math.min(64, 2 ** Math.floor(Math.log2(Math.max(1, k))))
    const key = `${level}:${tolPx}`
    let p = this.levels.get(key)
    if (!p) {
      // 1 px ≈ 360° / largeur de l'ovale
      const degPerPx = 360 / Math.max(400, this.width) / level
      const minWeight = (degPerPx * tolPx) ** 2
      const simple = simplify(this.topo as never, minWeight) as Topology
      const obj = simple.objects.land ?? simple.objects.countries
      const d = geoPath(this.projection)(feature(simple, obj as never) as never) ?? ''
      p = new Path2D(d)
      this.levels.set(key, p)
    }
    return p
  }

  /**
   * Pendant un geste : déplace l'image déjà dessinée au lieu de la redessiner.
   * Renvoie `false` si l'image ne couvre plus l'écran (dézoom, grand déplacement) : il faut redessiner.
   */
  follow(t: View): boolean {
    const s = t.k / this.drawn.k
    const tx = t.x - s * this.drawn.x
    const ty = t.y - s * this.drawn.y
    this.canvas.style.transform = `translate(${tx}px, ${ty}px) scale(${s})`
    const w = this.width
    const h = this.height
    return (
      s * -w * MARGIN + tx <= 0 &&
      s * (1 + MARGIN) * w + tx >= w &&
      s * -h * MARGIN + ty <= 0 &&
      s * (1 + MARGIN) * h + ty >= h
    )
  }

  draw(t: View) {
    const g = this.ctx
    const { k } = t
    this.drawn = { k: t.k, x: t.x, y: t.y }
    const ox = this.width * MARGIN
    const oy = this.height * MARGIN
    g.setTransform(this.dpr, 0, 0, this.dpr, 0, 0)
    g.clearRect(0, 0, this.canvas.width, this.canvas.height)
    g.setTransform(this.dpr * k, 0, 0, this.dpr * k, this.dpr * (t.x + ox), this.dpr * (t.y + oy))
    this.canvas.style.transform = ''
    g.lineJoin = 'round'

    g.fillStyle = this.colors.paper
    g.fill(this.sphere)
    g.save()
    g.clip(this.sphere)

    const rings = this.land(k, 2)
    const land = this.land(k, 0.6)
    // lignes d'eau : du large vers la côte, un trait bleu puis un trait papier qui ne laisse qu'un anneau
    for (let i = RINGS; i >= 1; i--) {
      g.globalAlpha = 0.78 - i * 0.11
      g.strokeStyle = this.colors.prusse
      g.lineWidth = (2 * (i * GAP + 0.35)) / k
      g.stroke(rings)
      g.globalAlpha = 1
      g.strokeStyle = this.colors.paper
      g.lineWidth = (2 * (i * GAP - 0.35)) / k
      g.stroke(rings)
    }

    g.strokeStyle = this.colors.encre
    g.globalAlpha = 0.16
    g.lineWidth = 0.6 / k
    g.setLineDash([1 / k, 3 / k])
    g.stroke(this.grat)
    for (const p of this.parallels) {
      g.globalAlpha = p.lat === 0 ? 0.35 : 0.22
      g.lineWidth = 0.7 / k
      g.setLineDash(p.lat === 0 ? [10 / k, 2 / k, 2 / k, 2 / k] : [6 / k, 3 / k])
      g.stroke(p.p)
    }

    // terres : papier, côtes en pointillé (terra incognita)
    g.globalAlpha = 1
    g.setLineDash([])
    g.fillStyle = this.colors.paper
    g.fill(land)
    g.globalAlpha = 0.55
    g.lineWidth = 0.8 / k
    g.lineCap = 'round'
    g.setLineDash([1.2 / k, 2.2 / k])
    g.stroke(land)
    g.restore()
    g.globalAlpha = 1
    g.setLineDash([])
  }
}
