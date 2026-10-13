<script lang="ts">
  // Carnet de l'explorateur : tous les faits découverts, classés, cherchables.
  import { loadFacts, type Dataset } from '../lib/data'
  import { CONTINENT_FR } from '../lib/store'
  import { normalize, typo } from '../lib/text'
  import type { Continent, Country, Fact } from '../lib/types'
  import FactView from './FactView.svelte'

  interface Props {
    ds: Dataset
    discovered: Record<string, number>
    onclose: () => void
    onopencountry: (id: string) => void
  }
  let { ds, discovered, onclose, onopencountry }: Props = $props()

  type Order = 'decouverte' | 'pays' | 'continent' | 'theme'
  const ORDERS: { v: Order; label: string }[] = [
    { v: 'decouverte', label: 'Ordre de découverte' },
    { v: 'pays', label: 'Pays' },
    { v: 'continent', label: 'Continent' },
    { v: 'theme', label: 'Thème' },
  ]
  const TOPICS = ['histoire', 'geographie', 'politique', 'culture', 'economie', 'drapeau']
  const TOPIC_FR: Record<string, string> = {
    histoire: 'Histoire',
    geographie: 'Géographie',
    politique: 'Politique',
    culture: 'Culture',
    economie: 'Économie',
    drapeau: 'Drapeaux',
  }

  interface Entry {
    fact: Fact
    country: Country
    at: number
    capital: boolean
    /** texte normalisé une fois pour toutes : fait, pays, alias, capitales, région */
    text: string
  }

  /** Filtre de région : tout, un continent (« c:europe ») ou une sous-région (« r:Europe du Nord »). */
  let region = $state('tout')
  /** Filtre de thème : tout, un `topic`, ou « capitale » (faits sur la capitale). */
  let theme = $state('tout')
  let order = $state<Order>('decouverte')
  let query = $state('')
  let entries = $state<Entry[]>([])
  let loading = $state(true)
  let selected = $state<string | null>(null)
  let deep = $state(false)
  let search: HTMLInputElement | undefined = $state()

  /** Pays d'un id de fait : « BOL-3 », « BOL-C1 » → BOL. */
  const countryOfFact = (fid: string) => fid.replace(/-C?\d+$/, '')

  $effect(() => {
    const ids = [...new Set(Object.keys(discovered).map(countryOfFact))].filter((id) => ds.byId.has(id))
    Promise.all(ids.map((id) => loadFacts(ds, id))).then((files) => {
      const out: Entry[] = []
      files.forEach((f, i) => {
        if (!f) return
        const country = ds.byId.get(ids[i])!
        const about = [
          country.name_fr,
          country.name_official_fr ?? '',
          ...(country.aliases_fr ?? []),
          ...country.capitals.map((k) => k.name_fr),
          country.subregion_fr ?? '',
        ].join(' ')
        const push = (fact: Fact, capital: boolean) => {
          if (!discovered[fact.id]) return
          const text = normalize([fact.title, fact.short, fact.long ?? '', about].join(' '))
          out.push({ fact, country, at: discovered[fact.id], capital, text })
        }
        for (const fact of f.facts ?? []) push(fact, false)
        for (const fact of f.capital_facts ?? []) push(fact, true)
      })
      entries = out
      loading = false
      if (!selected && out.length) selected = [...out].sort((a, b) => b.at - a.at)[0].fact.id
    })
    search?.focus({ preventScroll: true })
  })

  const filtered = $derived.by(() => {
    const q = normalize(query)
    return entries.filter((e) => {
      if (region.startsWith('c:') && e.country.continent !== region.slice(2)) return false
      if (region.startsWith('r:') && e.country.subregion_fr !== region.slice(2)) return false
      if (theme === 'capitale' && !e.capital) return false
      if (theme !== 'tout' && theme !== 'capitale' && e.fact.topic !== theme) return false
      return !q || e.text.includes(q)
    })
  })

  /** Régions présentes dans le carnet, rangées par continent. */
  const regionOptions = $derived.by(() => {
    const byContinent = new Map<Continent, Set<string>>()
    for (const e of entries) {
      const k = e.country.continent
      const set = byContinent.get(k) ?? byContinent.set(k, new Set()).get(k)!
      if (e.country.subregion_fr) set.add(e.country.subregion_fr)
    }
    return [...byContinent.keys()]
      .map((c) => ({ continent: c, label: CONTINENT_FR[c], subs: [...byContinent.get(c)!].sort((a, b) => a.localeCompare(b, 'fr')) }))
      .sort((a, b) => a.label.localeCompare(b.label, 'fr'))
  })

  const themeOptions = $derived.by(() => {
    const present = new Set(entries.map((e) => e.fact.topic ?? ''))
    const out = TOPICS.filter((t) => present.has(t)).map((t) => ({ v: t, label: TOPIC_FR[t] }))
    if (entries.some((e) => e.capital)) out.push({ v: 'capitale', label: 'Capitales' })
    return out
  })

  const filtering = $derived(region !== 'tout' || theme !== 'tout' || !!query.trim())

  const groups = $derived.by((): { title: string | null; items: Entry[] }[] => {
    // Chercher un pays par son nom : ses propres faits passent avant ceux qui le mentionnent.
    const q = normalize(query)
    const own = (e: Entry) => (q.length >= 3 && normalize(e.country.name_fr).startsWith(q) ? 1 : 0)
    const byAt = [...filtered].sort((a, b) => own(b) - own(a) || b.at - a.at)
    if (order === 'decouverte') return byAt.length ? [{ title: null, items: byAt }] : []
    const map = new Map<string, Entry[]>()
    const keyOf = (e: Entry) =>
      order === 'pays'
        ? e.country.name_fr
        : order === 'continent'
          ? CONTINENT_FR[e.country.continent]
          : (TOPIC_FR[e.fact.topic ?? ''] ?? 'Autres')
    for (const e of byAt) (map.get(keyOf(e)) ?? map.set(keyOf(e), []).get(keyOf(e))!).push(e)
    let keys = [...map.keys()]
    if (order === 'theme') {
      const rank = (k: string) => {
        const i = TOPICS.findIndex((t) => TOPIC_FR[t] === k)
        return i < 0 ? 99 : i
      }
      keys.sort((a, b) => rank(a) - rank(b))
    } else {
      const ownKey = (k: string) => (q.length >= 3 && order === 'pays' && normalize(k).startsWith(q) ? 1 : 0)
      keys.sort((a, b) => ownKey(b) - ownKey(a) || a.localeCompare(b, 'fr'))
    }
    return keys.map((k) => ({
      title: k,
      items:
        order === 'continent'
          ? map.get(k)!.sort((a, b) => a.country.name_fr.localeCompare(b.country.name_fr, 'fr'))
          : map.get(k)!,
    }))
  })

  /** Le fait affiché : le choisi s'il passe les filtres, sinon le premier de la liste filtrée. */
  const current = $derived(filtered.find((e) => e.fact.id === selected) ?? groups[0]?.items[0] ?? null)
  const countries = $derived(new Set(entries.map((e) => e.country.id)).size)

  function select(id: string) {
    selected = id
    deep = false
  }

  function onKey(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      e.preventDefault()
      onclose()
    }
  }
</script>

<svelte:window onkeydown={onKey} />

<div class="carnet feuille" role="dialog" aria-modal="true" aria-labelledby="titre-carnet">
  <header class="tete">
    <div class="titres">
      <h2 id="titre-carnet">Carnet de l'explorateur</h2>
      <p class="compte">
        {#if loading}Chargement…{:else if entries.length}{entries.length}
          {entries.length > 1 ? 'faits découverts' : 'fait découvert'}, dans {countries}
          {countries > 1 ? 'pays' : 'pays'}{:else}Aucun fait découvert pour l'instant.{/if}
      </p>
    </div>
    <input
      bind:this={search}
      bind:value={query}
      type="search"
      class="recherche"
      placeholder="Chercher un pays, un mot…"
      aria-label="Chercher dans les faits"
    />
    <button class="btn fermer" onclick={onclose} aria-label="Fermer le carnet">×</button>
  </header>

  <div class="reglages">
    <div class="classement" role="radiogroup" aria-label="Classer par">
      <span class="classer">Classer par</span>
      {#each ORDERS as o (o.v)}
        <button
          class="btn petit"
          class:choisi={order === o.v}
          role="radio"
          aria-checked={order === o.v}
          onclick={() => (order = o.v)}>{o.label}</button
        >
      {/each}
    </div>
    <div class="filtres">
      <label class="filtre">
        <span>Région</span>
        <select bind:value={region} aria-label="Filtrer par région">
          <option value="tout">Toutes</option>
          {#each regionOptions as r (r.continent)}
            <optgroup label={r.label}>
              <option value="c:{r.continent}">{r.label}, en entier</option>
              {#each r.subs as s (s)}
                <option value="r:{s}">{s}</option>
              {/each}
            </optgroup>
          {/each}
        </select>
      </label>
      <label class="filtre">
        <span>Thème</span>
        <select bind:value={theme} aria-label="Filtrer par thème">
          <option value="tout">Tous</option>
          {#each themeOptions as t (t.v)}
            <option value={t.v}>{t.label}</option>
          {/each}
        </select>
      </label>
      {#if filtering}
        <p class="compte-filtre" aria-live="polite">{filtered.length} sur {entries.length}</p>
      {/if}
    </div>
  </div>

  <div class="contenu">
    {#if !loading && !entries.length}
      <p class="vide">
        Chaque réponse fait découvrir un fait sur le pays. Ils s'inscrivent ici, avec leurs sources.
      </p>
    {:else}
      <nav class="liste" data-defilant aria-label="Faits découverts">
        {#each groups as g (g.title ?? '-')}
          {#if g.title}<h3>{g.title}</h3>{/if}
          <ul>
            {#each g.items as e (e.fact.id)}
              <li>
                <button class="entree" class:actif={current?.fact.id === e.fact.id} onclick={() => select(e.fact.id)}>
                  <span class="entree-titre">{typo(e.fact.title)}</span>
                  <span class="entree-pays">{e.country.name_fr}{#if e.capital}, capitale{/if}{#if e.fact.era}, {e.fact.era}{/if}</span>
                </button>
              </li>
            {/each}
          </ul>
        {:else}
          <p class="vide">
            {query.trim() ? `Rien ne correspond à « ${query.trim()} »` : 'Aucun fait'}{region !== 'tout' ||
            theme !== 'tout'
              ? ' avec ces filtres'
              : ''}.
          </p>
        {/each}
      </nav>
      <section class="detail" data-defilant aria-live="polite">
        {#if current}
          {@const cap = current.capital
            ? (current.country.capitals.find((k) => k.name_fr === current.country.quiz_capital) ??
              current.country.capitals[0])
            : null}
          {@const wiki = cap?.wiki_fr ?? current.country.wiki_fr}
          <p class="sujet">{current.country.name_fr}{#if cap}, capitale : {cap.name_fr}{/if}</p>
          <FactView fact={current.fact} expanded={deep} headingLevel={3} />
          <div class="actions">
            <button class="btn" onclick={() => (deep = !deep)} aria-expanded={deep}>
              {deep ? 'Replier' : 'Approfondir'}
            </button>
            <button class="btn discret" onclick={() => onopencountry(current.country.id)}>
              Voir la fiche : {current.country.name_fr}
            </button>
            {#if wiki}
              <a class="btn discret" href={wiki} target="_blank" rel="noopener noreferrer">Article Wikipédia</a>
            {/if}
          </div>
        {/if}
      </section>
    {/if}
  </div>
</div>

<style>
  .carnet {
    position: absolute;
    inset: 24px 32px;
    display: flex;
    flex-direction: column;
    pointer-events: auto;
    max-width: 1400px;
    margin: 0 auto;
  }
  .tete {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 20px 20px 12px 30px;
  }
  .titres {
    flex: 1;
    min-width: 0;
  }
  h2 {
    font-size: var(--t-37);
  }
  .compte {
    color: var(--encre-2);
    font-size: var(--t-16);
  }
  .recherche {
    width: min(360px, 32vw);
    height: 44px;
    padding: 4px 12px;
    font: inherit;
    font-size: var(--t-18);
    background: var(--velin-clair);
    border: 1.5px solid var(--encre);
    border-radius: 2px;
    color: var(--encre);
  }
  .recherche::placeholder {
    font-style: italic;
    color: var(--encre-2);
  }
  .fermer {
    width: 44px;
    min-height: 44px;
    padding: 0;
    font-size: 26px;
  }
  .reglages {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 10px 24px;
    padding: 0 30px 14px;
    border-bottom: 1px solid rgba(43, 31, 23, 0.3);
  }
  .classement,
  .filtres {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
  }
  .filtres {
    gap: 8px 16px;
  }
  .filtre {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .filtre span {
    font-style: italic;
    color: var(--encre-2);
    font-size: var(--t-16);
  }
  select {
    height: 36px;
    max-width: 240px;
    padding: 2px 8px;
    font: inherit;
    font-size: var(--t-16);
    color: var(--encre);
    background: var(--velin-clair);
    border: 1.5px solid var(--encre);
    border-radius: 2px;
    cursor: pointer;
  }
  .compte-filtre {
    font-size: var(--t-16);
    color: var(--encre-2);
    white-space: nowrap;
  }
  .sujet {
    font-family: var(--fell);
    font-style: italic;
    font-size: var(--t-21);
    margin-bottom: 8px;
    overflow-wrap: anywhere;
  }
  .classer {
    font-style: italic;
    color: var(--encre-2);
    font-size: var(--t-16);
    margin-right: 4px;
  }
  .petit {
    min-height: 36px;
    font-size: var(--t-16);
    padding: 2px 14px;
  }
  .btn.choisi {
    background: var(--prusse);
    border-color: var(--prusse);
    color: var(--velin-feuille);
  }
  .contenu {
    flex: 1;
    min-height: 0;
    display: grid;
    grid-template-columns: minmax(280px, 2fr) 3fr;
  }
  .liste {
    overflow-y: auto;
    padding: 14px 18px 24px 30px;
    border-right: 1px solid rgba(43, 31, 23, 0.3);
  }
  .liste h3 {
    font-family: var(--fell);
    font-size: var(--t-21);
    margin: 14px 0 4px;
  }
  .liste h3:first-child {
    margin-top: 0;
  }
  .liste ul {
    list-style: none;
    margin: 0;
    padding: 0;
  }
  .entree {
    display: flex;
    flex-direction: column;
    width: 100%;
    text-align: left;
    border: 0;
    background: none;
    padding: 7px 10px;
    cursor: pointer;
    border-left: 3px solid transparent;
  }
  .entree:hover {
    background: rgba(29, 58, 90, 0.07);
  }
  .entree.actif {
    border-left-color: var(--prusse);
    background: rgba(29, 58, 90, 0.1);
  }
  .entree-titre {
    font-size: var(--t-18);
    line-height: 1.3;
    overflow-wrap: anywhere;
  }
  .entree-pays {
    font-size: var(--t-14);
    color: var(--encre-2);
    font-style: italic;
  }
  .detail {
    overflow-y: auto;
    padding: 22px 36px 30px;
    max-width: 760px;
  }
  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 18px;
  }
  .vide {
    padding: 30px;
    font-style: italic;
    color: var(--encre-2);
    max-width: 60ch;
  }
</style>
