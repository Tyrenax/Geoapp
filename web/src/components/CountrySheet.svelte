<script lang="ts">
  // Fiche Atlas : drapeau, capitales, chiffres, progression, tous les faits (repliés s'ils sont à découvrir).
  import { flagUrl, loadFacts, type Dataset } from '../lib/data'
  import { cardKey } from '../lib/questions'
  import type { Card } from '../lib/scheduler'
  import { modeState } from '../lib/progress'
  import { CONTINENT_FR } from '../lib/store'
  import { formatNumber, typo } from '../lib/text'
  import { NON_RECT, type Country, type Fact, type FactsFile, type Mode } from '../lib/types'
  import FactView from './FactView.svelte'
  import PlateSticker from './PlateSticker.svelte'

  interface Props {
    ds: Dataset
    country: Country
    cards: Record<string, Card>
    discovered: Record<string, number>
    now: number
    onclose: () => void
    ondiscover: (facts: Fact[]) => void
  }
  let { ds, country, cards, discovered, now, onclose, ondiscover }: Props = $props()

  let facts = $state<FactsFile | null>(null)
  let loading = $state(true)
  let open = $state(new Set<string>())
  let closeBtn: HTMLButtonElement | undefined = $state()

  $effect(() => {
    const id = country.id
    loading = true
    facts = null
    open = new Set()
    loadFacts(ds, id).then((f) => {
      if (country.id !== id) return
      facts = f
      loading = false
    })
    closeBtn?.focus({ preventScroll: true })
  })

  const all = $derived([...(facts?.facts ?? []), ...(facts?.capital_facts ?? [])])
  const found = $derived(all.filter((f) => discovered[f.id]).length)

  const MODE_FR: Record<Mode, string> = { carte: 'Sur la carte', drapeau: 'Drapeau', capitale: 'Capitale' }
  const dateFr = new Intl.DateTimeFormat('fr-FR', { day: 'numeric', month: 'long' })

  function progress(m: Mode): string {
    const c = cards[cardKey(m, country.id)]
    const st = modeState(c, now)
    if (st === 'jamais') return 'pas encore posé'
    if (st === 'efface') return 'raté la dernière fois'
    if (st === 'a-revoir') return 'à revoir'
    return `encré, prochaine révision le ${dateFr.format(new Date(c!.due))}`
  }

  function toggle(f: Fact) {
    const next = new Set(open)
    if (next.has(f.id)) next.delete(f.id)
    else next.add(f.id)
    open = next
    if (!discovered[f.id]) ondiscover([f])
  }

  function reveal(f: Fact) {
    ondiscover([f])
  }

  function onKey(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      e.preventDefault()
      onclose()
    }
  }

  const asList = (v: string | string[] | null | undefined): string[] =>
    (Array.isArray(v) ? v : v ? [v] : []).map((x) => x.trim()).filter(Boolean)

  const plates = $derived(asList(country.plate_code))

  /** Lignes de la carte d'identité : seulement celles dont la donnée existe. */
  const identity = $derived.by(() => {
    const c = country
    const rows: { label: string; value: string }[] = []
    if (c.population && c.area_km2 && c.area_km2 >= 1) {
      const d = c.population / c.area_km2
      rows.push({ label: 'Densité', value: `${formatNumber(d >= 10 ? Math.round(d) : Math.round(d * 10) / 10)} hab./km²` })
    }
    if (c.demonym_fr) rows.push({ label: 'Habitants', value: c.demonym_fr })
    const langs = asList(c.languages_fr)
    if (langs.length) rows.push({ label: langs.length > 1 ? 'Langues officielles' : 'Langue officielle', value: langs.join(', ') })
    const cur = (c.currencies ?? []).filter((m) => m?.name_fr)
    if (cur.length)
      rows.push({
        label: cur.length > 1 ? 'Monnaies' : 'Monnaie',
        value: cur
          .map((m) => [m.name_fr, m.symbol, m.code !== m.symbol ? m.code : null].filter(Boolean).join(' · '))
          .join(' ; '),
      })
    if (c.motto_fr) rows.push({ label: 'Devise', value: `« ${c.motto_fr} »` })
    if (c.highest_point?.name_fr)
      rows.push({
        label: 'Point culminant',
        value: c.highest_point.name_fr + (c.highest_point.elevation_m ? ` (${formatNumber(c.highest_point.elevation_m)} m)` : ''),
      })
    const tel = asList(c.calling_code)
    if (tel.length) rows.push({ label: 'Indicatif', value: tel.join(', ') })
    const tld = asList(c.tld)
    if (tld.length) rows.push({ label: 'Domaine internet', value: tld.join(', ') })
    if (c.driving_side) rows.push({ label: 'On roule', value: `à ${c.driving_side}` })
    return rows
  })

  const flag = $derived(flagUrl(ds, country))
  const sovereign = $derived(country.sovereign ? ds.byId.get(country.sovereign) : null)
</script>

<svelte:window onkeydown={onKey} />

<aside class="fiche feuille" aria-label="Fiche de {country.name_fr}">
  <header class="tete">
    <div class="haut">
      {#if flag}
        <img
          src={flag}
          alt="Drapeau : {country.name_fr}"
          class="drapeau"
          class:sans-filet={NON_RECT.has(country.id)}
          onerror={(e) => ((e.currentTarget as HTMLImageElement).style.display = 'none')}
        />
      {:else}
        <span></span>
      {/if}
      <button class="btn fermer" bind:this={closeBtn} onclick={onclose} aria-label="Fermer la fiche">×</button>
    </div>
    {#if country.flag_note_fr}
      <p class="note-drapeau">{typo(country.flag_note_fr)}</p>
    {/if}
    <div class="noms">
      <h2>{country.name_fr}</h2>
      {#if country.name_official_fr && country.name_official_fr !== country.name_fr}
        <p class="officiel">{country.name_official_fr}</p>
      {/if}
      {#if country.kind === 'territoire'}
        <p class="statut">{country.status_fr ?? 'territoire'}{#if sovereign && !country.status_fr} ({sovereign.name_fr}){/if}</p>
      {/if}
    </div>
  </header>

  <div class="corps" data-defilant>
    <dl class="chiffres">
      <dt>{country.capitals.length > 1 ? 'Capitales' : 'Capitale'}</dt>
      <dd>
        {#each country.capitals as k, i (i)}
          <span class="capitale">
            {#if k.wiki_fr}<a href={k.wiki_fr} target="_blank" rel="noopener noreferrer">{k.name_fr}</a>{:else}{k.name_fr}{/if}{#if k.role_fr}{' '}<span class="role">({k.role_fr})</span>{/if}
          </span>
        {:else}
          <span class="role">{country.capital_note_fr ?? 'pas de capitale officielle'}</span>
        {/each}
        {#if country.capitals.length && country.capital_note_fr}
          <span class="role note-capitale">{typo(country.capital_note_fr)}</span>
        {/if}
      </dd>
      {#if country.population}
        <dt>Population</dt>
        <dd>{formatNumber(country.population)}{#if country.population_year}{' '}<span class="role">({country.population_year})</span>{/if}</dd>
      {/if}
      {#if country.area_km2}
        <dt>Superficie</dt>
        <dd>{formatNumber(country.area_km2)}&nbsp;km²</dd>
      {/if}
      <dt>Région</dt>
      <dd>{country.subregion_fr ?? CONTINENT_FR[country.continent]}</dd>
    </dl>

    {#if identity.length || plates.length || country.kind === 'territoire'}
      <section class="identite">
        <h3>Carte d'identité</h3>
        <dl class="chiffres">
          {#each identity as row (row.label)}
            <dt>{row.label}</dt>
            <dd>{typo(row.value)}</dd>
          {/each}
          <dt>Lettres de plaque</dt>
          <dd>
            {#if plates.length}
              <span class="plaques">
                {#each plates as p (p)}<PlateSticker code={p} />{/each}
              </span>
            {:else}
              <span class="role">{country.kind === 'territoire' ? 'pas de code propre' : 'aucun code international enregistré'}</span>
            {/if}
          </dd>
        </dl>
      </section>
    {/if}

    <section>
      <h3>Votre progression</h3>
      <ul class="progression">
        {#each ['carte', 'drapeau', 'capitale'] as const as m (m)}
          <li><span class="mode">{MODE_FR[m]}</span> <span class="etat">{progress(m)}</span></li>
        {/each}
      </ul>
    </section>

    <section>
      <h3>Faits</h3>
      {#if loading}
        <p class="role">Chargement…</p>
      {:else if !all.length}
        <p class="role">Pas encore de fait rédigé pour ce pays.</p>
      {:else}
        <p class="compte">{found} {found > 1 ? 'faits découverts' : 'fait découvert'} sur {all.length}</p>
        <ol class="faits">
          {#each all as f (f.id)}
            <li>
              {#if discovered[f.id]}
                <FactView fact={f} expanded={open.has(f.id)} headingLevel={4} />
                <button class="btn discret petit" onclick={() => toggle(f)} aria-expanded={open.has(f.id)}>
                  {open.has(f.id) ? 'Replier' : 'Approfondir'}
                </button>
              {:else}
                <div class="cache">
                  <span>Fait à découvrir{#if f.topic}, {f.topic === 'geographie' ? 'géographie' : f.topic === 'economie' ? 'économie' : f.topic}{/if}</span>
                  <button class="btn petit" onclick={() => reveal(f)}>Révéler</button>
                </div>
              {/if}
            </li>
          {/each}
        </ol>
      {/if}
    </section>

    {#if facts?.tips && (facts.tips.position || facts.tips.flag || facts.tips.capital)}
      <section>
        <h3>Astuces</h3>
        <dl class="astuces">
          {#if facts.tips.position}<dt>Position</dt><dd>{typo(facts.tips.position)}</dd>{/if}
          {#if facts.tips.flag}<dt>Drapeau</dt><dd>{typo(facts.tips.flag)}</dd>{/if}
          {#if facts.tips.capital}<dt>Capitale</dt><dd>{typo(facts.tips.capital)}</dd>{/if}
        </dl>
      </section>
    {/if}

    <section class="liens">
      {#if country.wiki_fr}<a href={country.wiki_fr} target="_blank" rel="noopener noreferrer">Article Wikipédia</a>{/if}
      {#if country.flag_wiki_fr}<a href={country.flag_wiki_fr} target="_blank" rel="noopener noreferrer">Le drapeau sur Wikipédia</a>{/if}
    </section>
  </div>
</aside>

<style>
  .fiche {
    width: var(--panneau);
    height: 100%;
    display: flex;
    flex-direction: column;
    pointer-events: auto;
    border-right: 0;
    border-top: 0;
    border-bottom: 0;
  }
  .tete {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 18px 18px 16px 26px;
    border-bottom: 1px solid rgba(43, 31, 23, 0.3);
  }
  .haut {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
  }
  .drapeau {
    display: block;
    width: auto;
    height: auto;
    max-width: 150px;
    max-height: 84px;
    border: 1px solid var(--encre);
  }
  .drapeau.sans-filet {
    border: 0;
  }
  .note-drapeau {
    font-size: var(--t-14);
    font-style: italic;
    color: var(--encre-2);
    margin-top: -6px;
    overflow-wrap: break-word;
  }
  .noms {
    flex: 1;
    min-width: 0;
  }
  h2 {
    font-size: var(--t-37);
    line-height: 1.05;
    overflow-wrap: break-word;
    padding-right: 8px;
  }
  .officiel,
  .statut {
    font-style: italic;
    color: var(--encre-2);
    font-size: var(--t-16);
    margin-top: 4px;
    overflow-wrap: anywhere;
  }
  .fermer {
    flex: none;
    margin-left: auto;
    width: 40px;
    min-height: 40px;
    padding: 0;
    font-size: 26px;
    line-height: 1;
  }
  .corps {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    padding: 16px 26px 24px;
    display: flex;
    flex-direction: column;
    gap: 22px;
  }
  h3 {
    font-family: var(--texte);
    font-style: italic;
    font-weight: 500;
    font-size: var(--t-16);
    color: var(--encre-2);
    margin: 0 0 6px;
  }
  .chiffres,
  .astuces {
    display: grid;
    grid-template-columns: auto minmax(0, 1fr);
    gap: 6px 16px;
    margin: 0;
  }
  /* Chiffres et carte d'identité : même colonne d'intitulés, pour que les deux listes s'alignent. */
  .chiffres {
    grid-template-columns: 7.4em minmax(0, 1fr);
    column-gap: 14px;
  }
  dt {
    font-style: italic;
    color: var(--encre-2);
    font-size: var(--t-16);
    padding-top: 2px;
  }
  dd {
    margin: 0;
    overflow-wrap: anywhere;
  }
  .capitale {
    display: block;
  }
  .plaques {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding-top: 2px;
  }
  .role {
    color: var(--encre-2);
    font-style: italic;
  }
  .note-capitale {
    display: block;
    margin-top: 4px;
    font-size: 0.92em;
  }
  .progression {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .mode {
    font-weight: 500;
  }
  .etat {
    color: var(--encre-2);
  }
  .compte {
    margin-bottom: 10px;
  }
  .faits {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .faits li {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
  }
  .cache {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    width: 100%;
    padding: 8px 12px;
    border: 1px dashed rgba(43, 31, 23, 0.4);
    color: var(--encre-2);
    font-style: italic;
  }
  .petit {
    min-height: 34px;
    font-size: var(--t-16);
    padding: 2px 12px;
  }
  .btn.discret.petit {
    padding-inline: 0;
  }
  .liens {
    display: flex;
    flex-wrap: wrap;
    gap: 6px 18px;
  }
</style>
