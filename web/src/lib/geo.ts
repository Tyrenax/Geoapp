// Projection d'atlas, géométries, pigments, distances.
import { geoDistance, geoGraticule, geoPath, type GeoProjection } from 'd3-geo'
import { geoHammer } from 'd3-geo-projection'
import { feature, neighbors as topoNeighbors } from 'topojson-client'
import type { Feature, FeatureCollection, Geometry, MultiPolygon, Polygon } from 'geojson'
import type { GeometryCollection, Topology } from 'topojson-specification'
import type { Dataset } from './data'

export type CountryFeature = Feature<Polygon | MultiPolygon, { id: string }>

export const SPHERE = { type: 'Sphere' } as const

/** Le monde dans l'ovale (Hammer), centré à 10° E : la Tchoukotka n'est pas coupée. */
export function makeProjection(): GeoProjection {
  return (geoHammer() as GeoProjection).rotate([-10, 0]).precision(0.2)
}

/** Ajuste l'ovale à la zone donnée (pixels). */
export function fitProjection(p: GeoProjection, x0: number, y0: number, x1: number, y1: number) {
  p.fitExtent(
    [
      [x0, y0],
      [x1, y1],
    ],
    SPHERE as never,
  )
}

export interface WorldGeo {
  countries: CountryFeature[]
  byId: Map<string, CountryFeature>
  land: Feature<Geometry>
  /** id → voisins (par arcs partagés + contrat) */
  adjacency: Map<string, Set<string>>
  /** zones neutres, non quizzables (objet `other` du TopoJSON) : tracées, jamais posées */
  neutral: Feature<Polygon | MultiPolygon, { name_fr?: string }>[]
}

export function buildWorld(ds: Dataset): WorldGeo {
  const topo = ds.world as Topology
  const obj = topo.objects.countries as GeometryCollection<{ id?: string }>
  const fc = feature(topo, obj) as unknown as FeatureCollection<Polygon | MultiPolygon, { id?: string }>
  const countries: CountryFeature[] = fc.features
    .map((f) => ({ ...f, properties: { id: String(f.properties?.id ?? f.id ?? '') } }))
    .filter((f) => f.properties.id && f.geometry) as CountryFeature[]
  const byId = new Map(countries.map((f) => [f.properties.id, f]))
  const landObj = topo.objects.land
  const land = (
    landObj
      ? (feature(topo, landObj as never) as unknown as Feature<Geometry> | FeatureCollection)
      : { type: 'FeatureCollection', features: countries }
  ) as Feature<Geometry>

  const adjacency = new Map<string, Set<string>>()
  const add = (a: string, b: string) => {
    if (a === b) return
    ;(adjacency.get(a) ?? adjacency.set(a, new Set()).get(a)!).add(b)
    ;(adjacency.get(b) ?? adjacency.set(b, new Set()).get(b)!).add(a)
  }
  const ids = obj.geometries.map((g) => String((g.properties as { id?: string } | undefined)?.id ?? g.id ?? ''))
  topoNeighbors(obj.geometries as never).forEach((ns, i) => ns.forEach((j) => add(ids[i], ids[j])))
  for (const c of ds.countries) for (const n of c.neighbors ?? []) add(c.id, n)
  const otherObj = topo.objects.other as GeometryCollection | undefined
  const neutral = otherObj
    ? (feature(topo, otherObj) as unknown as FeatureCollection<Polygon | MultiPolygon, { name_fr?: string }>).features
    : []
  return { countries, byId, land, adjacency, neutral }
}

/** Les quatre pinceaux du coloriage à la main. */
export const PIGMENTS = ['vert', 'carmin', 'gutte', 'prusse'] as const
export type Pigment = (typeof PIGMENTS)[number]

/**
 * Coloriage glouton (les plus grands degrés d'abord) : deux voisins n'ont pas le même pinceau
 * tant que quatre suffisent ; sinon on prend le moins utilisé par les voisins.
 */
export function assignPigments(ids: string[], adjacency: Map<string, Set<string>>): Map<string, Pigment> {
  const order = [...ids].sort(
    (a, b) => (adjacency.get(b)?.size ?? 0) - (adjacency.get(a)?.size ?? 0) || a.localeCompare(b),
  )
  const out = new Map<string, Pigment>()
  for (const id of order) {
    const used = new Map<Pigment, number>()
    for (const n of adjacency.get(id) ?? []) {
      const p = out.get(n)
      if (p) used.set(p, (used.get(p) ?? 0) + 1)
    }
    // Départ décalé par l'id pour ne pas peindre tout le monde en vert.
    const h = [...id].reduce((s, ch) => s + ch.charCodeAt(0), 0)
    const ring = PIGMENTS.map((_, i) => PIGMENTS[(i + h) % PIGMENTS.length])
    const free = ring.find((p) => !used.has(p))
    out.set(id, free ?? ring.reduce((a, b) => ((used.get(a) ?? 0) <= (used.get(b) ?? 0) ? a : b)))
  }
  return out
}

const EARTH_KM = 6371

export function distanceKm(a: [number, number], b: [number, number]): number {
  return geoDistance(a, b) * EARTH_KM
}

export const graticule = geoGraticule().step([30, 30])

/** Équateur, tropiques, cercles polaires : lignes de latitude complètes. */
export function parallel(lat: number) {
  const coords: [number, number][] = []
  for (let lon = -180; lon <= 180; lon += 2) coords.push([lon, lat])
  return { type: 'LineString' as const, coordinates: coords }
}

export const PARALLELS = [
  { lat: 0, name: 'Équateur' },
  { lat: 23.44, name: 'Tropique du Cancer' },
  { lat: -23.44, name: 'Tropique du Capricorne' },
  { lat: 66.56, name: 'Cercle arctique' },
  { lat: -66.56, name: 'Cercle antarctique' },
]

export const OCEANS: { name: string; lon: number; lat: number }[] = [
  { name: 'Océan Pacifique', lon: -128, lat: -12 },
  { name: 'Océan Atlantique', lon: -38, lat: 28 },
  { name: 'Océan Indien', lon: 76, lat: -28 },
  { name: 'Océan Pacifique', lon: 162, lat: 22 },
  { name: 'Océan Austral', lon: 60, lat: -58 },
]

export { geoPath }
