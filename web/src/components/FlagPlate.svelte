<script lang="ts">
  // Planche de pavillons : un drapeau à nommer, ou quatre drapeaux parmi lesquels choisir.
  import { flagUrl, type Dataset } from '../lib/data'
  import { NON_RECT, type Country } from '../lib/types'

  interface Props {
    ds: Dataset
    flags: Country[]
    /** un seul drapeau : rien à cliquer */
    pickable: boolean
    result: { chosen: string | null; correct: string } | null
    onpick?: (id: string) => void
  }
  let { ds, flags, pickable, result, onpick }: Props = $props()

  function onWindowKey(e: KeyboardEvent) {
    if (!pickable || result) return
    if ((e.target as HTMLElement)?.tagName === 'INPUT') return
    const n = Number(e.key)
    if (n >= 1 && n <= flags.length) {
      e.preventDefault()
      onpick?.(flags[n - 1].id)
    }
  }

  /** drapeau absent (données en cours de génération) : on n'affiche pas d'image cassée */
  function hideBroken(e: Event) {
    ;(e.currentTarget as HTMLImageElement).style.visibility = 'hidden'
  }

  function state(c: Country) {
    if (!result) return ''
    if (c.id === result.correct) return 'juste'
    if (c.id === result.chosen) return 'faux'
    return 'eteint'
  }
</script>

<svelte:window onkeydown={onWindowKey} />

{#if !pickable}
  <figure class="seul">
    <img
      src={flagUrl(ds, flags[0])}
      alt="Drapeau à reconnaître"
      class:sans-filet={NON_RECT.has(flags[0].id)}
      onerror={hideBroken}
    />
  </figure>
{:else}
  <div class="planche" role="group" aria-label="Quatre drapeaux">
    {#each flags as c, i (c.id)}
      {@const st = state(c)}
      <button
        class="pavillon {st}"
        disabled={!!result}
        onclick={() => onpick?.(c.id)}
        aria-label={result ? `Drapeau ${i + 1} : ${c.name_fr}` : `Drapeau ${i + 1}`}
        aria-keyshortcuts={String(i + 1)}
      >
        <span class="cadre"><img src={flagUrl(ds, c)} alt="" class:sans-filet={NON_RECT.has(c.id)} onerror={hideBroken} /></span>
        <span class="legende">
          <span class="touche" aria-hidden="true">{i + 1}</span>
          {#if result}
            <span class="nom">{c.name_fr}</span>
            {#if st === 'juste'}<span class="signe" aria-hidden="true">✓</span>{/if}
            {#if st === 'faux'}<span class="signe" aria-hidden="true">✗</span>{/if}
          {/if}
        </span>
      </button>
    {/each}
  </div>
{/if}

<style>
  .seul {
    margin: 0;
    padding: 14px;
    background: var(--velin-feuille);
    border: 4px double var(--encre);
    pointer-events: auto;
    line-height: 0;
  }
  .seul img {
    display: block;
    width: auto;
    height: auto;
    max-width: min(440px, 40vw);
    max-height: min(290px, 36vh);
    min-width: 160px;
    border: 1px solid var(--encre);
  }
  .planche {
    display: grid;
    grid-template-columns: repeat(2, auto);
    gap: 14px 18px;
    pointer-events: auto;
  }
  .pavillon {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    padding: 10px 10px 6px;
    background: var(--velin-feuille);
    border: 1.5px solid var(--encre);
    border-radius: 2px;
    cursor: pointer;
    width: clamp(200px, 18vw, 270px);
  }
  .pavillon:hover:not(:disabled) {
    border-color: var(--prusse);
    box-shadow: 0 0 0 2px var(--prusse);
  }
  .pavillon:disabled {
    cursor: default;
  }
  .cadre {
    height: clamp(110px, 17vh, 160px);
    width: 100%;
    display: grid;
    place-items: center;
  }
  .cadre img {
    display: block;
    width: auto;
    height: auto;
    max-width: 100%;
    max-height: clamp(110px, 17vh, 160px);
    border: 1px solid var(--encre);
  }
  .legende {
    display: flex;
    align-items: center;
    gap: 8px;
    min-height: 26px;
    max-width: 100%;
  }
  .nom {
    font-size: var(--t-16);
    overflow-wrap: anywhere;
    line-height: 1.2;
    text-align: center;
  }
  .touche {
    flex: none;
    font-size: var(--t-14);
    color: var(--encre-2);
    border: 1px solid rgba(43, 31, 23, 0.45);
    width: 22px;
    height: 22px;
    display: inline-grid;
    place-items: center;
    border-radius: 2px;
  }
  .signe {
    font-size: var(--t-21);
    line-height: 1;
  }
  .pavillon.juste {
    border-color: var(--vert);
    border-width: 3px;
    background: color-mix(in srgb, var(--vert) 16%, var(--velin-feuille));
  }
  .pavillon.faux {
    border-color: var(--carmin);
    border-style: dashed;
    border-width: 2px;
  }
  /* éteint sans transparence : la carte ne doit pas se voir à travers un drapeau */
  .pavillon.eteint img {
    filter: saturate(0.5) contrast(0.85) brightness(1.08);
  }
  .pavillon.eteint .legende {
    opacity: 0.7;
  }
  /* le Népal n'est pas rectangulaire : pas de filet autour */
  img.sans-filet {
    border: 0 !important;
  }
</style>
