<script lang="ts">
  // Carton (petite carte en médaillon) : le pays et ses voisins au crayon. Aucun nom.
  import { geoAzimuthalEqualArea, geoCentroid, geoPath } from 'd3-geo'
  import type { Dataset } from '../lib/data'
  import type { WorldGeo } from '../lib/geo'

  interface Props {
    ds: Dataset
    world: WorldGeo
    id: string
    width?: number
    height?: number
  }
  let { ds, world, id, width = 260, height = 180 }: Props = $props()

  const view = $derived.by(() => {
    const f = world.byId.get(id)
    const c = ds.byId.get(id)
    const center: [number, number] | null = c?.label
      ? [c.label.lon, c.label.lat]
      : f
        ? (geoCentroid(f) as [number, number])
        : null
    if (!center) return null
    const proj = geoAzimuthalEqualArea().rotate([-center[0], -center[1]])
    const pad = 26
    if (f && !c?.small) {
      proj.fitExtent(
        [
          [pad, pad],
          [width - pad, height - pad],
        ],
        f,
      )
      // pays immenses : on garde un minimum de voisinage
      proj.scale(proj.scale() * 0.62)
    } else {
      proj.scale(1600).translate([width / 2, height / 2])
    }
    proj.clipAngle(80)
    const path = geoPath(proj)
    const others = world.countries.filter((g) => g.properties.id !== id).map((g) => path(g) ?? '')
    const target = f && !c?.small ? (path(f) ?? '') : ''
    const dot = proj(center)
    return { others, target, dot: c?.small || !f ? dot : null }
  })
</script>

<svg {width} {height} viewBox="0 0 {width} {height}" class="medaillon" aria-hidden="true">
  <defs>
    <clipPath id="clip-medaillon">
      <ellipse cx={width / 2} cy={height / 2} rx={width / 2 - 5} ry={height / 2 - 5} />
    </clipPath>
    <pattern id="hachure-med" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <line x1="0" y1="0" x2="0" y2="5" class="trait" />
    </pattern>
  </defs>
  <ellipse cx={width / 2} cy={height / 2} rx={width / 2 - 5} ry={height / 2 - 5} class="fond" />
  {#if view}
    <g clip-path="url(#clip-medaillon)">
      {#each view.others as d, i (i)}
        <path {d} class="voisin" />
      {/each}
      {#if view.target}<path d={view.target} class="cible" />{/if}
      {#if view.dot}
        <circle cx={view.dot[0]} cy={view.dot[1]} r="6" class="point" />
      {/if}
    </g>
  {/if}
  <ellipse cx={width / 2} cy={height / 2} rx={width / 2 - 5} ry={height / 2 - 5} class="cadre" />
  <ellipse cx={width / 2} cy={height / 2} rx={width / 2 - 1.5} ry={height / 2 - 1.5} class="cadre fin" />
</svg>

<style>
  .medaillon {
    display: block;
    flex: none;
  }
  .fond {
    fill: var(--velin-clair);
  }
  .voisin {
    fill: var(--velin-feuille);
    stroke: var(--crayon);
    stroke-width: 0.8;
  }
  .cible {
    fill: url(#hachure-med);
    stroke: var(--prusse);
    stroke-width: 1.8;
    stroke-linejoin: round;
  }
  .trait {
    stroke: var(--prusse);
    stroke-width: 1.6;
  }
  .point {
    fill: var(--prusse);
    stroke: var(--encre);
  }
  .cadre {
    fill: none;
    stroke: var(--encre);
    stroke-width: 2;
  }
  .cadre.fin {
    stroke-width: 0.8;
  }
</style>
