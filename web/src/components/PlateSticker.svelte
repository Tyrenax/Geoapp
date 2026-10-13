<script lang="ts">
  // Autocollant ovale blanc des plaques (signe distinctif de la Convention de Vienne) : « F », « CH », « RCA ».
  let { code }: { code: string } = $props()

  // Corps de lettre selon la longueur : jusqu'à 3 lettres tiennent dans l'ovale sans déborder.
  const size = $derived(code.length <= 1 ? 30 : code.length === 2 ? 26 : code.length === 3 ? 21 : 16)
</script>

<svg class="plaque" viewBox="0 0 84 52" width="84" height="52" role="img" aria-label="Lettres de plaque : {code}">
  <ellipse cx="42" cy="26" rx="39" ry="23" class="fond" />
  <ellipse cx="42" cy="26" rx="35.5" ry="19.5" class="filet" />
  <text
    x="42"
    y="26"
    font-size={size}
    textLength={code.length >= 3 ? 52 : undefined}
    lengthAdjust="spacingAndGlyphs"
    dominant-baseline="central"
    text-anchor="middle">{code}</text
  >
</svg>

<style>
  .plaque {
    display: block;
    flex: none;
  }
  .fond {
    fill: #fbfaf6;
    stroke: var(--encre);
    stroke-width: 2;
  }
  .filet {
    fill: none;
    stroke: var(--encre);
    stroke-width: 0.8;
    opacity: 0.55;
  }
  text {
    font-family: Arial, 'Helvetica Neue', Helvetica, sans-serif;
    font-weight: 700;
    fill: #111;
    letter-spacing: 0.5px;
  }
</style>
