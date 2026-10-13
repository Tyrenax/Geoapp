<script lang="ts">
  // Rose des vents : un ornement qui travaille (recentre la carte), avec le zoom à côté.
  interface Props {
    onrecentre: () => void
    onzoom: (f: number) => void
  }
  let { onrecentre, onzoom }: Props = $props()

  const R = 54
  // Pointes : 4 cardinales longues, 4 intercardinales, 8 courtes ; chacune en deux moitiés (ombre / lumière).
  const points = Array.from({ length: 16 }, (_, i) => {
    const a = (i * Math.PI) / 8
    const len = i % 4 === 0 ? R : i % 2 === 0 ? R * 0.68 : R * 0.42
    const w = i % 4 === 0 ? 9 : i % 2 === 0 ? 7 : 5
    const tip = [Math.sin(a) * len, -Math.cos(a) * len]
    const l = [Math.sin(a - Math.PI / 2) * w, -Math.cos(a - Math.PI / 2) * w]
    const r = [Math.sin(a + Math.PI / 2) * w, -Math.cos(a + Math.PI / 2) * w]
    return {
      order: i % 4 === 0 ? 2 : i % 2 === 0 ? 1 : 0,
      dark: `M0 0L${l[0].toFixed(2)} ${l[1].toFixed(2)}L${tip[0].toFixed(2)} ${tip[1].toFixed(2)}Z`,
      light: `M0 0L${r[0].toFixed(2)} ${r[1].toFixed(2)}L${tip[0].toFixed(2)} ${tip[1].toFixed(2)}Z`,
    }
  }).sort((a, b) => a.order - b.order)
</script>

<div class="rose-bloc">
  <button class="rose" onclick={onrecentre} aria-label="Recentrer la carte" title="Recentrer la carte">
    <svg viewBox="-66 -74 132 140" width="118" height="125" aria-hidden="true">
      <circle r="44" class="cercle" />
      <circle r="40" class="cercle fin" />
      {#each Array.from({ length: 32 }) as _, i (i)}
        <line
          x1={Math.sin((i * Math.PI) / 16) * 40}
          y1={-Math.cos((i * Math.PI) / 16) * 40}
          x2={Math.sin((i * Math.PI) / 16) * 44}
          y2={-Math.cos((i * Math.PI) / 16) * 44}
          class="graduation"
        />
      {/each}
      {#each points as p, i (i)}
        <path d={p.dark} class="ombre" />
        <path d={p.light} class="lumiere" />
      {/each}
      <circle r="3.2" class="moyeu" />
      <text y="-60" class="n">N</text>
    </svg>
  </button>
  <div class="zoom">
    <button class="btn" onclick={() => onzoom(1.6)} aria-label="Zoomer" title="Zoomer">+</button>
    <button class="btn" onclick={() => onzoom(1 / 1.6)} aria-label="Dézoomer" title="Dézoomer">−</button>
  </div>
</div>

<style>
  .rose-bloc {
    display: flex;
    align-items: flex-end;
    gap: 10px;
    pointer-events: auto;
  }
  .rose {
    border: 0;
    background: none;
    padding: 0;
    cursor: pointer;
    border-radius: 50%;
    line-height: 0;
  }
  .rose:hover .ombre {
    fill: var(--prusse);
  }
  .rose svg {
    transition: transform 400ms ease;
  }
  .rose:active svg {
    transform: rotate(-11.25deg);
  }
  .cercle {
    fill: var(--velin-feuille);
    stroke: var(--encre);
    stroke-width: 1.2;
  }
  .cercle.fin {
    fill: none;
    stroke-width: 0.6;
  }
  .graduation {
    stroke: var(--encre);
    stroke-width: 0.6;
  }
  .ombre {
    fill: var(--encre);
    stroke: var(--encre);
    stroke-width: 0.6;
    stroke-linejoin: round;
  }
  .lumiere {
    fill: var(--velin-feuille);
    stroke: var(--encre);
    stroke-width: 0.6;
    stroke-linejoin: round;
  }
  .moyeu {
    fill: var(--carmin);
    stroke: var(--encre);
    stroke-width: 0.6;
  }
  .n {
    font-family: var(--fell);
    font-size: 17px;
    text-anchor: middle;
    fill: var(--encre);
  }
  .zoom {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 8px;
  }
  .zoom .btn {
    width: 38px;
    min-height: 38px;
    padding: 0;
    font-size: 22px;
    line-height: 1;
  }
</style>
