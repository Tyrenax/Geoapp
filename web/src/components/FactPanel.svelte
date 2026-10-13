<script lang="ts">
  // Feuille de droite après chaque réponse : verdict, bonne réponse, astuce si erreur, un fait, Approfondir.
  import FactView from './FactView.svelte'
  import Seal from './Seal.svelte'
  import { typo } from '../lib/text'
  import type { Fact } from '../lib/types'

  export interface Outcome {
    ok: boolean
    /** phrase de verdict, déjà rédigée */
    headline: string
    /** précisions : bonne réponse, distance, autres capitales */
    details: string[]
    tip: string | null
  }

  interface Props {
    outcome: Outcome
    fact: Fact | null
    others: Fact[]
    wiki: { url: string; label: string } | null
    loading: boolean
    last: boolean
    onnext: () => void
    ondeepen: (facts: Fact[]) => void
  }
  let { outcome, fact, others, wiki, loading, last, onnext, ondeepen }: Props = $props()

  let deep = $state(false)
  let nextBtn: HTMLButtonElement | undefined = $state()

  $effect(() => {
    nextBtn?.focus({ preventScroll: true })
  })

  function toggleDeep() {
    deep = !deep
    if (deep) ondeepen(others)
  }

  function onKey(e: KeyboardEvent) {
    if (e.key === 'Escape' && deep) {
      e.preventDefault()
      deep = false
    }
  }
</script>

<svelte:window onkeydown={onKey} />

<aside class="panneau feuille" aria-live="polite" aria-label="Résultat et fait">
  <div class="corps" data-defilant>
    <header class="verdict" class:ok={outcome.ok}>
      {#if !outcome.ok}<Seal size={44} />{/if}
      <div class="verdict-texte">
        <p class="titre-verdict">{outcome.headline}</p>
        {#each outcome.details as d, i (i)}
          <p class="detail">{d}</p>
        {/each}
      </div>
    </header>

    {#if outcome.tip}
      <section class="astuce">
        <h2>Pour retenir</h2>
        <p>{typo(outcome.tip)}</p>
      </section>
    {/if}

    <section class="fait-bloc">
      {#if loading}
        <p class="attente">Les faits arrivent…</p>
      {:else if fact}
        <FactView {fact} expanded={deep} headingLevel={2} />
        {#if deep && others.length}
          <div class="autres">
            <h2>Autres faits</h2>
            {#each others as f (f.id)}
              <FactView fact={f} expanded headingLevel={3} />
            {/each}
          </div>
        {/if}
      {:else}
        <p class="attente">Pas encore de fait rédigé pour ce pays.</p>
      {/if}
      <div class="liens">
        {#if fact}
          <button class="btn" onclick={toggleDeep} aria-expanded={deep}>
            {deep ? 'Replier' : 'Approfondir'}
          </button>
        {/if}
        {#if wiki}
          <a class="btn discret" href={wiki.url} target="_blank" rel="noopener noreferrer">{wiki.label}</a>
        {/if}
      </div>
    </section>
  </div>
  <footer class="pied">
    <button class="btn principal" bind:this={nextBtn} onclick={onnext}>
      {last ? 'Voir le bilan' : 'Question suivante'}
    </button>
    <span class="kbd" aria-hidden="true">Entrée</span>
  </footer>
</aside>

<style>
  .panneau {
    width: var(--panneau);
    height: 100%;
    display: flex;
    flex-direction: column;
    pointer-events: auto;
    border-right: 0;
    border-top: 0;
    border-bottom: 0;
  }
  .corps {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    padding: 24px 26px 16px;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  .verdict {
    display: flex;
    gap: 14px;
    align-items: flex-start;
  }
  .verdict-texte {
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .titre-verdict {
    font-family: var(--fell);
    font-size: var(--t-28);
    line-height: 1.15;
    color: var(--carmin);
    overflow-wrap: anywhere;
  }
  .verdict.ok .titre-verdict {
    color: var(--vert);
  }
  .detail {
    font-size: var(--t-18);
    overflow-wrap: anywhere;
  }
  .astuce {
    border-left: 3px solid var(--gutte);
    padding: 2px 0 2px 14px;
  }
  .astuce h2,
  .autres h2 {
    font-family: var(--texte);
    font-style: italic;
    font-size: var(--t-16);
    font-weight: 500;
    color: var(--encre-2);
    margin: 0 0 2px;
  }
  .astuce p {
    font-size: var(--t-18);
    overflow-wrap: break-word;
  }
  .fait-bloc {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding-top: 16px;
    border-top: 1px solid rgba(43, 31, 23, 0.3);
  }
  .autres {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding-top: 12px;
    border-top: 1px dashed rgba(43, 31, 23, 0.3);
  }
  .liens {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
  }
  .liens .btn {
    white-space: normal;
    text-align: left;
    max-width: 100%;
  }
  .attente {
    font-style: italic;
    color: var(--encre-2);
  }
  .pied {
    flex: none;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 26px 18px;
    border-top: 1px solid rgba(43, 31, 23, 0.3);
  }
</style>
