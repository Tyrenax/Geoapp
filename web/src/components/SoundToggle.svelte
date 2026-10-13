<script lang="ts">
  // Bouton muet, mémorisé avec les réglages. Coupé par défaut.
  let { on, ontoggle }: { on: boolean; ontoggle: () => void } = $props()
</script>

<button class="son" aria-pressed={on} onclick={ontoggle} title={on ? 'Couper les sons' : 'Activer les sons'}>
  <svg viewBox="0 0 20 16" width="20" height="16" aria-hidden="true">
    <path d="M2 5.5h3.5L10 2v12L5.5 10.5H2z" class="haut-parleur" />
    {#if on}
      <path d="M13 5.2a4 4 0 0 1 0 5.6M15.3 3a7 7 0 0 1 0 10" class="onde" />
    {:else}
      <path d="M13 5.5l5 5M18 5.5l-5 5" class="onde" />
    {/if}
  </svg>
  <span>{on ? 'Sons actifs' : 'Sons coupés'}</span>
</button>

<style>
  .son {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    min-height: 32px;
    padding: 2px 6px;
    border: 0;
    background: none;
    cursor: pointer;
    font-size: var(--t-16);
    color: var(--encre-2);
    pointer-events: auto;
  }
  .son:hover span {
    text-decoration: underline;
    text-underline-offset: 3px;
  }
  .haut-parleur {
    fill: var(--encre);
  }
  .onde {
    fill: none;
    stroke: var(--encre);
    stroke-width: 1.5;
    stroke-linecap: round;
  }
</style>
