<script lang="ts">
  // Carnet relié gravé : ouvre le Carnet de l'explorateur.
  let { count, onopen }: { count: number; onopen: () => void } = $props()
</script>

<button class="carnet" onclick={onopen} aria-label="Ouvrir le carnet de l'explorateur ({count} faits découverts)">
  <svg viewBox="0 0 64 80" width="52" height="65" aria-hidden="true">
    <rect x="10" y="4" width="48" height="70" rx="2" class="pages" />
    <rect x="6" y="6" width="48" height="70" rx="2" class="couverture" />
    <rect x="6" y="6" width="9" height="70" class="dos" />
    <line x1="6" y1="18" x2="15" y2="18" class="nerf" />
    <line x1="6" y1="64" x2="15" y2="64" class="nerf" />
    <rect x="22" y="22" width="24" height="16" class="etiquette" />
    <line x1="25" y1="28" x2="43" y2="28" class="ligne" />
    <line x1="25" y1="33" x2="39" y2="33" class="ligne" />
    <rect x="50" y="36" width="12" height="9" rx="1" class="fermoir" />
  </svg>
  <span class="texte">
    <span class="titre">Carnet de l'explorateur</span>
    <span class="compte">{count} {count === 1 ? 'fait découvert' : 'faits découverts'}</span>
  </span>
</button>

<style>
  .carnet {
    display: flex;
    align-items: center;
    gap: 12px;
    border: 0;
    background: none;
    padding: 4px 8px 4px 2px;
    cursor: pointer;
    text-align: left;
    pointer-events: auto;
  }
  .carnet:hover .couverture {
    fill: var(--prusse-fonce);
  }
  .carnet:hover .titre {
    text-decoration: underline;
    text-underline-offset: 3px;
  }
  .pages {
    fill: var(--velin-feuille);
    stroke: var(--encre);
    stroke-width: 1;
  }
  .couverture {
    fill: var(--prusse);
    stroke: var(--encre);
    stroke-width: 1.2;
  }
  .dos {
    fill: var(--encre);
  }
  .nerf {
    stroke: var(--gutte);
    stroke-width: 1.4;
  }
  .etiquette {
    fill: var(--velin-feuille);
    stroke: var(--gutte);
    stroke-width: 0.8;
  }
  .ligne {
    stroke: var(--encre);
    stroke-width: 1;
  }
  .fermoir {
    fill: var(--gutte);
    stroke: var(--encre);
    stroke-width: 0.8;
  }
  .texte {
    display: flex;
    flex-direction: column;
    line-height: 1.25;
  }
  .titre {
    font-family: var(--fell);
    font-style: italic;
    font-size: var(--t-21);
  }
  .compte {
    font-size: var(--t-16);
    color: var(--encre-2);
  }
</style>
