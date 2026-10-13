<script lang="ts">
  // Réponse : quatre choix, ou saisie libre avec complétion (accents, casse, tirets ignorés).
  import { complete, type Suggestion } from '../lib/text'

  export interface Choice {
    value: string // id de l'entité
    label: string
  }

  interface Props {
    style: 'choix' | 'saisie'
    choices: Choice[]
    items: Suggestion[]
    placeholder: string
    /** après la réponse : ce qui a été choisi et la bonne valeur */
    result: { chosen: string | null; correct: string } | null
    onanswer: (a: { text: string; value: string | null }) => void
  }

  let { style, choices, items, placeholder, result, onanswer }: Props = $props()

  let text = $state('')
  let open = $state(false)
  let active = $state(-1)
  let input: HTMLInputElement | undefined = $state()
  const list = $derived(open ? complete(text, items, 6) : [])
  const listId = 'completion-' + Math.random().toString(36).slice(2, 8)

  $effect(() => {
    if (style === 'saisie' && !result) input?.focus()
  })

  function submit(t: string, value: string | null = null) {
    if (result || !t.trim()) return
    open = false
    onanswer({ text: t, value })
  }

  function pickSuggestion(s: Suggestion) {
    text = s.label
    submit(s.label, s.value)
  }

  function onKey(e: KeyboardEvent) {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      open = true
      active = Math.min(list.length - 1, active + 1)
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      active = Math.max(-1, active - 1)
    } else if (e.key === 'Enter') {
      e.preventDefault()
      e.stopPropagation()
      if (active >= 0 && list[active]) pickSuggestion(list[active])
      else submit(text)
    } else if (e.key === 'Escape') {
      if (open && list.length) {
        e.stopPropagation()
        open = false
        active = -1
      }
    }
  }

  function onWindowKey(e: KeyboardEvent) {
    if (style !== 'choix' || result) return
    if ((e.target as HTMLElement)?.tagName === 'INPUT') return
    const n = Number(e.key)
    if (n >= 1 && n <= choices.length) {
      e.preventDefault()
      onanswer({ text: choices[n - 1].label, value: choices[n - 1].value })
    }
  }

  function choiceState(c: Choice): string {
    if (!result) return ''
    if (c.value === result.correct) return 'juste'
    if (c.value === result.chosen) return 'faux'
    return 'eteint'
  }
</script>

<svelte:window onkeydown={onWindowKey} />

{#if style === 'choix'}
  <div class="choix" role="group" aria-label="Réponses possibles">
    {#each choices as c, i (c.value)}
      {@const st = choiceState(c)}
      <button
        class="btn option {st}"
        disabled={!!result}
        aria-keyshortcuts={String(i + 1)}
        onclick={() => onanswer({ text: c.label, value: c.value })}
      >
        <span class="touche" aria-hidden="true">{i + 1}</span>
        <span class="libelle">{c.label}</span>
        {#if st === 'juste'}<span class="signe" aria-label="bonne réponse">✓</span>{/if}
        {#if st === 'faux'}<span class="signe" aria-label="votre réponse, fausse">✗</span>{/if}
      </button>
    {/each}
  </div>
{:else}
  <div class="saisie">
    <div class="champ">
      <input
        bind:this={input}
        bind:value={text}
        type="text"
        {placeholder}
        disabled={!!result}
        autocomplete="off"
        spellcheck="false"
        role="combobox"
        aria-label={placeholder}
        aria-expanded={list.length > 0}
        aria-controls={listId}
        aria-autocomplete="list"
        aria-activedescendant={active >= 0 ? `${listId}-${active}` : undefined}
        oninput={() => {
          open = true
          active = -1
        }}
        onkeydown={onKey}
        onblur={() => setTimeout(() => (open = false), 120)}
        class={result ? (result.chosen === result.correct ? 'juste' : 'faux') : ''}
      />
      <button class="btn principal" disabled={!!result || !text.trim()} onclick={() => submit(text)}>Valider</button>
    </div>
    {#if list.length > 0 && !result}
      <ul class="completion feuille" id={listId} role="listbox">
        {#each list as s, i (s.value + s.label)}
          <li
            id="{listId}-{i}"
            role="option"
            aria-selected={i === active}
            class:actif={i === active}
            onmousedown={(e) => {
              e.preventDefault()
              pickSuggestion(s)
            }}
          >
            {s.label}
          </li>
        {/each}
      </ul>
    {/if}
  </div>
{/if}

<style>
  .choix {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
    width: min(680px, 100%);
    pointer-events: auto;
  }
  .option {
    justify-content: flex-start;
    min-height: 52px;
    padding: 8px 14px;
    white-space: normal;
    text-align: left;
    font-size: var(--t-21);
    font-weight: 400;
    gap: 12px;
  }
  .libelle {
    flex: 1;
    min-width: 0;
    overflow-wrap: anywhere;
    line-height: 1.2;
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
    flex: none;
    font-size: var(--t-21);
    line-height: 1;
  }
  .option.juste {
    background: color-mix(in srgb, var(--vert) 18%, var(--velin-feuille));
    border-color: var(--vert);
    border-width: 2.5px;
    color: var(--encre);
  }
  .option.faux {
    background: color-mix(in srgb, var(--carmin) 12%, var(--velin-feuille));
    border-color: var(--carmin);
    border-style: dashed;
    border-width: 2px;
  }
  .option.eteint {
    opacity: 0.55;
  }

  .saisie {
    position: relative;
    width: min(560px, 100%);
    pointer-events: auto;
  }
  .champ {
    display: flex;
    gap: 10px;
  }
  input {
    flex: 1;
    min-width: 0;
    height: 52px;
    padding: 6px 14px;
    font-family: var(--texte);
    font-size: var(--t-21);
    color: var(--encre);
    background: var(--velin-feuille);
    border: 1.5px solid var(--encre);
    border-radius: 2px;
  }
  input::placeholder {
    color: var(--encre-2);
    opacity: 0.75;
    font-style: italic;
  }
  input.juste {
    border-color: var(--vert);
    border-width: 2.5px;
  }
  input.faux {
    border-color: var(--carmin);
    border-style: dashed;
    border-width: 2px;
    text-decoration: line-through;
    text-decoration-color: var(--carmin);
  }
  .champ .btn {
    min-height: 52px;
  }
  .completion {
    position: absolute;
    left: 0;
    right: 0;
    bottom: calc(100% + 6px);
    margin: 0;
    padding: 4px 0;
    list-style: none;
    max-height: 290px;
    overflow-y: auto;
  }
  .completion li {
    padding: 6px 14px;
    font-size: var(--t-18);
    cursor: pointer;
    overflow-wrap: anywhere;
  }
  .completion li:hover,
  .completion li.actif {
    background: color-mix(in srgb, var(--prusse) 14%, var(--velin-feuille));
  }
  .completion li.actif {
    box-shadow: inset 3px 0 0 var(--prusse);
  }
</style>
