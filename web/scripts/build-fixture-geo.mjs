// Construit web/fixtures/world.topo.json depuis Natural Earth 110m (géométrie de dev uniquement).
// Usage : node scripts/build-fixture-geo.mjs <ne_110m_admin_0_countries.geojson>
import { readFileSync, writeFileSync } from 'node:fs'
import { topology } from 'topojson-server'
import { mergeArcs } from 'topojson-client'

const src = process.argv[2]
if (!src) throw new Error('chemin du GeoJSON Natural Earth attendu')
const fc = JSON.parse(readFileSync(src, 'utf8'))
const fix = { KOS: 'XKX' }
const features = fc.features.map((f) => {
  const p = f.properties
  let id = p.ISO_A3 && p.ISO_A3 !== '-99' ? p.ISO_A3 : p.ADM0_A3
  id = fix[id] ?? id
  return { type: 'Feature', properties: { id }, geometry: f.geometry }
})
const topo = topology({ countries: { type: 'FeatureCollection', features } }, 1e5)
const geoms = topo.objects.countries.geometries
topo.objects.land = { type: 'GeometryCollection', geometries: [mergeArcs(topo, geoms)] }
const out = new URL('../fixtures/world.topo.json', import.meta.url)
writeFileSync(out, JSON.stringify(topo))
console.log(features.length, 'pays,', readFileSync(out).length, 'octets')
