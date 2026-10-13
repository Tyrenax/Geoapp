<script lang="ts">
  // Sceau de cire : marque l'erreur, toujours accompagné du mot.
  let { size = 46 }: { size?: number } = $props()
  const blob = Array.from({ length: 18 }, (_, i) => {
    const a = (i / 18) * Math.PI * 2
    const r = 20 + (i % 3 === 0 ? 2.2 : i % 2 ? -0.8 : 1)
    return `${(Math.cos(a) * r).toFixed(2)},${(Math.sin(a) * r).toFixed(2)}`
  }).join(' ')
</script>

<svg viewBox="-24 -24 48 48" width={size} height={size} aria-hidden="true" class="sceau">
  <polygon points={blob} class="cire" />
  <circle r="14.5" class="anneau" />
  <path d="M-6 -6 L6 6 M6 -6 L-6 6" class="croix" />
</svg>

<style>
  .sceau {
    flex: none;
  }
  .cire {
    fill: var(--carmin);
    stroke: #6d1826;
    stroke-width: 1.2;
    stroke-linejoin: round;
  }
  .anneau {
    fill: none;
    stroke: #f0c9c0;
    stroke-opacity: 0.55;
    stroke-width: 1.2;
  }
  .croix {
    stroke: #f6dcd4;
    stroke-width: 2.6;
    stroke-linecap: round;
  }
</style>
