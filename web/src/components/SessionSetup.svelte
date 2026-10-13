<script lang="ts">
  // Lancement d'une session : mode, façon de répondre, régions, territoires.
  import { ALL_CONTINENTS, CONTINENT_FR, type SessionMode, type Settings } from '../lib/store'
  import type { SessionPreview } from '../lib/questions'
  import type { Continent } from '../lib/types'

  interface Props {
    settings: Settings
    preview: SessionPreview
    onchange: (s: Settings) => void
    onstart: () => void
    oncancel: () => void
  }
  let { settings, preview, onchange, onstart, oncancel }: Props = $props()

  const MODES: { v: SessionMode; label: string }[] = [
    { v: 'carte', label: 'Sur la carte' },
    { v: 'drapeau', label: 'Drapeaux' },
    { v: 'capitale', label: 'Capitales' },
    { v: 'tout', label: 'Tout mêler' },
  ]

  let startBtn: HTMLButtonElement | undefined = $state()
  $effect(() => {
    startBtn?.focus({ preventScroll: true })
  })

  function toggleContinent(c: Continent) {
    const has = settings.continents.includes(c)
    const continents = has ? settings.continents.filter((x) => x !== c) : [...settings.continents, c]
    onchange({ ...settings, continents })
  }

  function onKey(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      e.preventDefault()
      oncancel()
    }
  }

  const summary = $derived.by(() => {
    if (!preview.total) return 'Aucune question avec ces réglages : cochez au moins une région.'
    const parts: string[] = []
    if (preview.due) parts.push(`${preview.due} à revoir`)
    if (preview.fresh) parts.push(`${preview.fresh} ${preview.fresh > 1 ? 'nouvelles' : 'nouvelle'}`)
    const rest = preview.total - preview.due - preview.fresh
    if (rest > 0) parts.push(`${rest} déjà ${rest > 1 ? 'vues' : 'vue'}`)
    return `${preview.total} questions : ${parts.join(', ')}.`
  })
</script>

<svelte:window onkeydown={onKey} />

<div class="fond" role="presentation" onclick={oncancel}></div>
<div class="lancement feuille" role="dialog" aria-modal="true" aria-labelledby="titre-lancement">
  <h2 id="titre-lancement">Nouvelle session</h2>

  <fieldset>
    <legend>Que réviser ?</legend>
    <div class="segments">
      {#each MODES as m (m.v)}
        <label class="segment" class:choisi={settings.mode === m.v}>
          <input
            type="radio"
            name="mode"
            value={m.v}
            checked={settings.mode === m.v}
            onchange={() => onchange({ ...settings, mode: m.v })}
          />
          {m.label}
        </label>
      {/each}
    </div>
  </fieldset>

  <fieldset>
    <legend>Comment répondre ?</legend>
    <div class="segments">
      <label class="segment" class:choisi={settings.answer === 'choix'}>
        <input
          type="radio"
          name="reponse"
          checked={settings.answer === 'choix'}
          onchange={() => onchange({ ...settings, answer: 'choix' })}
        />
        Quatre choix
      </label>
      <label class="segment" class:choisi={settings.answer === 'saisie'}>
        <input
          type="radio"
          name="reponse"
          checked={settings.answer === 'saisie'}
          onchange={() => onchange({ ...settings, answer: 'saisie' })}
        />
        Saisie libre
      </label>
    </div>
    <p class="aide">
      {settings.answer === 'choix'
        ? 'Les drapeaux à choisir et les clics sur la carte restent identiques.'
        : 'Une liste se complète pendant la frappe ; accents et petites fautes sont tolérés.'}
    </p>
  </fieldset>

  <fieldset>
    <legend>Quelles régions ?</legend>
    <div class="regions">
      {#each ALL_CONTINENTS as c (c)}
        <label class="case">
          <input type="checkbox" checked={settings.continents.includes(c)} onchange={() => toggleContinent(c)} />
          {CONTINENT_FR[c]}
        </label>
      {/each}
    </div>
    <label class="case territoires">
      <input
        type="checkbox"
        checked={settings.territories}
        onchange={() => onchange({ ...settings, territories: !settings.territories })}
      />
      Inclure les territoires (Groenland, Nouvelle-Calédonie…)
    </label>
  </fieldset>

  <p class="resume" class:vide={!preview.total}>{summary}</p>

  <div class="actions">
    <button class="btn principal" bind:this={startBtn} disabled={!preview.total} onclick={onstart}>Commencer</button>
    <button class="btn" onclick={oncancel}>Annuler</button>
  </div>
</div>

<style>
  .fond {
    position: absolute;
    inset: 0;
    background: rgba(43, 31, 23, 0.18);
    pointer-events: auto;
  }
  .lancement {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    width: min(620px, calc(100vw - 32px));
    max-height: calc(100vh - 32px);
    overflow-y: auto;
    padding: 26px 30px 24px;
    display: flex;
    flex-direction: column;
    gap: 18px;
    pointer-events: auto;
  }
  h2 {
    font-size: var(--t-37);
  }
  fieldset {
    border: 0;
    margin: 0;
    padding: 0;
    min-width: 0;
  }
  legend {
    padding: 0;
    margin-bottom: 8px;
    font-style: italic;
    color: var(--encre-2);
    font-size: var(--t-16);
  }
  .segments {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  .segment {
    position: relative;
    display: inline-flex;
    align-items: center;
    min-height: 42px;
    padding: 6px 16px;
    border: 1.5px solid var(--encre);
    border-radius: 2px;
    cursor: pointer;
    font-weight: 500;
    background: var(--velin-feuille);
    white-space: nowrap;
  }
  .segment:hover {
    background: #f3eedf;
  }
  .segment.choisi {
    background: var(--prusse);
    border-color: var(--prusse);
    color: var(--velin-feuille);
  }
  .segment input {
    position: absolute;
    opacity: 0;
    inset: 0;
    margin: 0;
    cursor: pointer;
  }
  .segment:has(input:focus-visible) {
    outline: 2px solid var(--prusse);
    outline-offset: 3px;
  }
  .aide {
    margin-top: 6px;
    font-size: var(--t-16);
    color: var(--encre-2);
  }
  .regions {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 4px 16px;
  }
  .case {
    display: flex;
    align-items: center;
    gap: 8px;
    min-height: 34px;
    cursor: pointer;
  }
  .case input {
    width: 18px;
    height: 18px;
    accent-color: var(--prusse);
    margin: 0;
    flex: none;
  }
  .territoires {
    margin-top: 6px;
  }
  .resume {
    font-family: var(--fell);
    font-size: var(--t-21);
  }
  .resume.vide {
    color: var(--carmin);
  }
  .actions {
    display: flex;
    gap: 10px;
  }
</style>
