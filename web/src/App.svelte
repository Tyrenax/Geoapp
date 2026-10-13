<script lang="ts">
  import { onMount, tick } from 'svelte'
  import AtlasMap, { type Highlight, type Mark, type PickEvent } from './components/AtlasMap.svelte'
  import AnswerBox, { type Choice } from './components/AnswerBox.svelte'
  import Carnet from './components/Carnet.svelte'
  import CompassRose from './components/CompassRose.svelte'
  import CountrySheet from './components/CountrySheet.svelte'
  import FactPanel, { type Outcome } from './components/FactPanel.svelte'
  import FlagPlate from './components/FlagPlate.svelte'
  import Medallion from './components/Medallion.svelte'
  import Notebook from './components/Notebook.svelte'
  import SessionSetup from './components/SessionSetup.svelte'
  import SoundToggle from './components/SoundToggle.svelte'
  import { setSound, soundInk, soundRight, soundWrong } from './lib/sound'
  import { loadDataset, loadFacts, type Dataset } from './lib/data'
  import { assignPigments, buildWorld, distanceKm, type Pigment, type WorldGeo } from './lib/geo'
  import { atlasCounts, inkMap } from './lib/progress'
  import {
    answerPool,
    buildQuestion,
    buildSession,
    capitalOf,
    eligible,
    expects,
    judgeText,
    placeToleranceKm,
    previewSession,
    suggestions,
    type Question,
  } from './lib/questions'
  import { newCard, review, type Grade } from './lib/scheduler'
  import { loadState, saveState, type SaveState, type Settings } from './lib/store'
  import { capitalize, deArticle, formatKm, withArticle } from './lib/text'
  import type { AnswerStyle, Country, Fact, FactsFile, Variant } from './lib/types'

  type Screen = 'atlas' | 'lancement' | 'quiz' | 'bilan' | 'carnet'

  interface Answered {
    ok: boolean
    outcome: Outcome
    result: { chosen: string | null; correct: string } | null
  }

  interface Session {
    questions: Question[]
    index: number
    results: { key: string; ok: boolean; id: string }[]
    before: Map<string, number>
    settings: Settings
  }

  let ds = $state.raw<Dataset | null>(null)
  let world = $state.raw<WorldGeo | null>(null)
  let pigments = $state.raw(new Map<string, Pigment>())
  let error = $state<string | null>(null)
  let save = $state<SaveState>(loadState())
  let now = $state(Date.now())
  let screen = $state<Screen>('atlas')
  let ficheId = $state<string | null>(null)
  let session = $state.raw<Session | null>(null)
  let answered = $state.raw<Answered | null>(null)
  let highlights = $state.raw<Highlight[]>([])
  let marks = $state.raw<Mark[]>([])
  let factState = $state.raw<{ loading: boolean; fact: Fact | null; others: Fact[] }>({
    loading: false,
    fact: null,
    others: [],
  })
  let map: AtlasMap | undefined = $state()
  let grain = $state('')
  let complete = $state.raw(new Set<string>())

  const inks = $derived(ds ? inkMap(ds.countries, save.cards, now) : new Map())
  const counts = $derived(ds ? atlasCounts(ds.countries, inks) : null)
  const discoveredCount = $derived(Object.keys(save.facts).length)
  const question = $derived(session && screen === 'quiz' ? (session.questions[session.index] ?? null) : null)
  const progress = $derived(session ? { n: session.index + 1, total: session.questions.length } : { n: 0, total: 0 })

  // Crochets pour les recettes Playwright : lire la question en cours, forcer une session précise.
  // Les réponses, elles, passent toujours par de vrais clics.
  $effect(() => {
    const w = window as unknown as Record<string, unknown>
    w.__quiz = question
      ? {
          variant: question.variant,
          id: question.target.id,
          answer: question.answer,
          choices: question.choices.map((c) => c.id),
          answered: !!answered,
        }
      : null
  })

  function testHooks() {
    ;(window as unknown as Record<string, unknown>).__geoTest = {
      session(
        items: { key: string; variant: Variant; choices?: string[] }[],
        answer: AnswerStyle = 'choix',
      ) {
        if (!ds) return false
        const settings: Settings = { ...($state.snapshot(save.settings) as Settings), answer, territories: true }
        const questions = items.map((it) => {
          const q = buildQuestion(ds!, it.key, settings)!
          q.variant = it.variant
          if (it.choices) q.choices = it.choices.map((id) => ds!.byId.get(id)!).filter(Boolean)
          return q
        })
        session = {
          questions,
          index: 0,
          results: [],
          before: new Map([...inks].map(([id, ink]) => [id, ink.level])),
          settings,
        }
        ficheId = null
        screen = 'quiz'
        prepareQuestion()
        return true
      },
      fiche(id: string) {
        session = null
        screen = 'atlas'
        ficheId = id
      },
      ready: () => !!ds,
    }
  }

  onMount(() => {
    testHooks()
    grain = paperGrain()
    loadDataset()
      .then((d) => {
        const w = buildWorld(d)
        world = w
        pigments = assignPigments(
          [...new Set([...w.countries.map((f) => f.properties.id), ...d.countries.map((c) => c.id)])],
          w.adjacency,
        )
        ds = d
        refreshComplete()
      })
      .catch((e) => (error = String(e?.message ?? e)))
  })

  /** Grain du papier : bruit calculé une fois, posé en multiply au-dessus de tout. */
  function paperGrain(): string {
    try {
      const c = document.createElement('canvas')
      c.width = c.height = 220
      const g = c.getContext('2d')!
      const img = g.createImageData(220, 220)
      for (let i = 0; i < img.data.length; i += 4) {
        const v = 200 + Math.random() * 55
        img.data[i] = v
        img.data[i + 1] = v * 0.97
        img.data[i + 2] = v * 0.9
        img.data[i + 3] = 255
      }
      g.putImageData(img, 0, 0)
      return c.toDataURL('image/png')
    } catch {
      return ''
    }
  }

  function persist() {
    saveState($state.snapshot(save) as SaveState)
  }

  // ---------- découverte des faits ----------

  function discover(facts: Fact[]) {
    let changed = false
    const t = Date.now()
    for (const f of facts)
      if (!save.facts[f.id]) {
        save.facts[f.id] = t
        changed = true
      }
    if (changed) {
      persist()
      refreshComplete()
    }
  }

  /** Pays dont tous les faits sont découverts (marque discrète sur l'atlas). */
  async function refreshComplete() {
    if (!ds) return
    const ids = [...new Set(Object.keys(save.facts).map((f) => f.replace(/-C?\d+$/, '')))]
    const out = new Set<string>()
    await Promise.all(
      ids.map(async (id) => {
        const f = await loadFacts(ds!, id)
        const all = [...(f?.facts ?? []), ...(f?.capital_facts ?? [])]
        if (all.length && all.every((x) => save.facts[x.id])) out.add(id)
      }),
    )
    complete = out
  }

  // ---------- session ----------

  const preview = $derived(ds ? previewSession(ds, save.settings, save.cards, now) : null)

  function updateSettings(s: Settings) {
    save.settings = s
    persist()
  }

  $effect(() => setSound(!!save.settings.sound))

  function toggleSound() {
    save.settings.sound = !save.settings.sound
    setSound(save.settings.sound)
    persist()
    if (save.settings.sound) soundRight() // aperçu discret de ce qu'on vient d'activer
  }

  function startSession() {
    if (!ds) return
    now = Date.now()
    const settings = $state.snapshot(save.settings) as Settings
    const questions = buildSession(ds, settings, save.cards, now)
    if (!questions.length) return
    session = {
      questions,
      index: 0,
      results: [],
      before: new Map([...inks].map(([id, ink]) => [id, ink.level])),
      settings,
    }
    ficheId = null
    screen = 'quiz'
    prepareQuestion()
  }

  function prepareQuestion() {
    answered = null
    marks = []
    factState = { loading: false, fact: null, others: [] }
    const q = session?.questions[session.index]
    if (!q) return
    highlights = q.variant === 'carte-nommer' ? [{ id: q.target.id, tone: 'question' }] : []
    tick().then(() => {
      // pays à nommer : zoom s'il serait trop petit, ou recadrage s'il passe sous le cartouche ou les réponses
      if (q.variant === 'carte-nommer' && map) {
        const top = (document.querySelector('.barre') as HTMLElement | null)?.getBoundingClientRect().bottom ?? 120
        const bas = document.querySelector('.quiz .bas') as HTMLElement | null
        const bottom = bas ? window.innerHeight - bas.getBoundingClientRect().top : 150
        if (map.needsZoom(q.target.id))
          map.zoomTo(q.target.id, { context: 8, maxK: q.target.small ? 3 : 8, top, bottom })
        else if (
          !map.fitsFree(
            q.target.id,
            [...document.querySelectorAll('.question, .progression, .quiz .bas > *')].map((e) => e.getBoundingClientRect()),
          )
        )
          map.zoomTo(q.target.id, { context: 1.4, maxK: 4, top, bottom })
        else map.reset(400)
      } else map?.reset(400)
    })
  }

  function next() {
    if (!session) return
    if (session.index + 1 >= session.questions.length) {
      screen = 'bilan'
      highlights = []
      marks = []
      map?.reset()
      return
    }
    session = { ...session, index: session.index + 1 }
    prepareQuestion()
  }

  function quitSession() {
    if (!session) return
    screen = 'bilan'
    answered = null
    highlights = []
    marks = []
    map?.reset()
  }

  const newlyInked = $derived.by(() => {
    if (!session || !ds) return []
    return ds.countries.filter((c) => (inks.get(c.id)?.level ?? 0) > (session!.before.get(c.id) ?? 0))
  })

  async function backToAtlas() {
    const ids = newlyInked.map((c) => c.id)
    session = null
    screen = 'atlas'
    map?.reset()
    await tick()
    if (ids.length) map?.animateInk(ids, soundInk)
  }

  // ---------- réponses ----------

  function record(q: Question, grade: Grade) {
    const t = Date.now()
    const card = save.cards[q.key] ?? newCard(q.key)
    save.cards[q.key] = review(card, grade, t)
    now = t
    persist()
    if (grade === 'faux') soundWrong()
    else soundRight()
    if (!session) return
    // pas de reprise dans la série : un pays n'y sort qu'une fois, la révision espacée le ramène plus tard
    session = { ...session, results: [...session.results, { key: q.key, ok: grade !== 'faux', id: q.target.id }] }
  }

  const name = (c: Country) => withArticle(c.article_fr, c.name_fr)
  const Name = (c: Country) => capitalize(name(c))

  function capitalsLine(c: Country): string | null {
    if (c.capitals.length < 2) return null
    return (
      'Capitales : ' +
      c.capitals.map((k) => k.name_fr + (k.role_fr ? ` (${k.role_fr})` : '')).join(', ') +
      '. Toutes sont acceptées.'
    )
  }

  async function finish(q: Question, ok: boolean, grade: Grade, outcome: Omit<Outcome, 'tip'>, result: Answered['result']) {
    if (!ds) return
    record(q, grade)
    answered = { ok, outcome: { ...outcome, tip: null }, result }
    factState = { loading: true, fact: null, others: [] }
    const facts = await loadFacts(ds, q.target.id)
    if (session?.questions[session.index] !== q) return
    const tip = ok ? null : tipFor(q, facts)
    answered = { ok, outcome: { ...outcome, tip }, result }
    const chosen = chooseFact(q, facts)
    factState = { loading: false, ...chosen }
    if (chosen.fact) discover([chosen.fact])
  }

  function tipFor(q: Question, f: FactsFile | null): string | null {
    const t = f?.tips
    if (!t) return null
    if (q.mode === 'carte') return t.position ?? null
    if (q.mode === 'drapeau') return t.flag ?? null
    return (q.variant === 'placer-capitale' ? (t.capital ?? t.position) : t.capital) ?? null
  }

  function chooseFact(q: Question, f: FactsFile | null): { fact: Fact | null; others: Fact[] } {
    if (!f) return { fact: null, others: [] }
    const main = f.facts ?? []
    const caps = f.capital_facts ?? []
    const pool = q.mode === 'capitale' && caps.length ? caps : main.length ? main : caps
    const fresh = pool.filter((x) => !save.facts[x.id])
    const from = fresh.length ? fresh : pool
    // histoire d'abord parmi les inédits, sinon au hasard
    const hist = from.filter((x) => x.topic === 'histoire')
    const pickFrom = fresh.length && hist.length ? hist : from
    const fact = pickFrom[Math.floor(Math.random() * pickFrom.length)] ?? null
    const others = [...main, ...caps].filter((x) => x !== fact)
    return { fact, others }
  }

  function onAnswerText(a: { text: string; value: string | null }) {
    const q = question
    if (!q || answered || !ds) return
    const kind = expects(q)!
    const pool = answerPool(ds, q.mode, session?.settings.territories ?? false)
    let verdict: 'exact' | 'proche' | 'faux'
    if (q.answer === 'choix') verdict = a.value === q.target.id ? 'exact' : 'faux'
    else verdict = judgeText(ds, q, a.text, kind === 'capitale' ? answerPool(ds, 'capitale', true) : pool)
    const ok = verdict !== 'faux'
    const grade: Grade = verdict === 'exact' ? 'juste' : verdict === 'proche' ? 'difficile' : 'faux'
    const c = q.target
    const cap = capitalOf(c)
    let headline = ''
    const details: string[] = []
    if (q.variant === 'pays-capitale') {
      headline = ok ? `Juste : ${cap.name_fr}.` : `Non : c'est ${cap.name_fr}.`
      if (!ok) details.push(`Capitale ${deArticle(c.article_fr, c.name_fr)} : ${cap.name_fr}.`)
      const line = capitalsLine(c)
      if (line) details.push(line)
    } else if (q.variant === 'capitale-pays') {
      headline = ok ? `Juste : ${name(c)}.` : `Non : c'était ${name(c)}.`
      details.push(`${cap.name_fr} est la capitale ${deArticle(c.article_fr, c.name_fr)}.`)
    } else {
      headline = ok ? `Juste : ${name(c)}.` : `Non : c'était ${name(c)}.`
      if (q.variant === 'drapeau-nom') details.push(`C'est le drapeau ${deArticle(c.article_fr, c.name_fr)}.`)
    }
    if (verdict === 'proche') {
      headline = 'Juste, à une faute près.'
      const forms = kind === 'capitale' ? cap.name_fr : c.name_fr
      details.unshift(`On écrit « ${forms} ».`)
    }
    if (!ok && q.answer === 'saisie') details.push(`Votre réponse : « ${a.text.trim()} ».`)
    const correctValue = q.target.id
    if (q.variant === 'carte-nommer')
      highlights = [
        ...(!ok && a.value && a.value !== c.id ? [{ id: a.value, tone: 'faux' as const }] : []),
        { id: c.id, tone: ok ? ('juste' as const) : ('question' as const) },
      ]
    finish(q, ok, grade, { ok, headline, details }, { chosen: q.answer === 'saisie' ? (ok ? correctValue : null) : a.value, correct: correctValue })
  }

  function onPickFlag(id: string) {
    const q = question
    if (!q || answered || !ds) return
    const ok = id === q.target.id
    const chosen = ds.byId.get(id)!
    const headline = ok ? `Juste : voici le drapeau ${deArticle(q.target.article_fr, q.target.name_fr)}.` : 'Non.'
    const details = ok
      ? []
      : [
          `Vous avez choisi le drapeau ${deArticle(chosen.article_fr, chosen.name_fr)}.`,
          `Celui ${deArticle(q.target.article_fr, q.target.name_fr)} est marqué ✓.`,
        ]
    finish(q, ok, ok ? 'juste' : 'faux', { ok, headline, details }, { chosen: id, correct: q.target.id })
  }

  function targetPoint(c: Country): [number, number] | null {
    if (c.label) return [c.label.lon, c.label.lat]
    return null
  }

  function onMapPick(e: PickEvent) {
    if (!ds) return
    if (screen === 'atlas') {
      if (e.id && ds.byId.has(e.id)) ficheId = e.id
      return
    }
    const q = question
    if (!q || answered) return
    const c = q.target
    if (q.variant === 'carte-ou') {
      // une zone neutre n'est pas un pays : jamais une mauvaise réponse ; son nom s'affiche au survol
      if (e.neutral) return
      const ok = e.id === c.id
      const tp = targetPoint(c)
      const km = !ok && e.lonlat && tp ? distanceKm(e.lonlat, tp) : null
      const clicked = e.id ? ds.byId.get(e.id) : null
      const details: string[] = []
      if (!ok) {
        if (clicked) details.push(`Vous avez désigné ${name(clicked)}.`)
        else if (!e.id) details.push('Votre clic est tombé en mer.')
        details.push(`${Name(c)} est en vert sur la carte${km != null ? `, à ${formatKm(km)} de votre clic` : ''}.`)
      }
      highlights = ok
        ? [{ id: c.id, tone: 'juste' }]
        : [
            ...(e.id && e.id !== c.id ? [{ id: e.id, tone: 'faux' as const }] : []),
            { id: c.id, tone: 'juste' as const },
          ]
      if (!ok && e.lonlat && c.small && tp) marks = [{ lon: tp[0], lat: tp[1], kind: 'vrai' }]
      finish(q, ok, ok ? 'juste' : 'faux', { ok, headline: ok ? `Juste : ${name(c)}.` : 'Non.', details }, null)
      if (!ok) tick().then(() => map?.zoomTo(c.id, { right: panelWidth(), context: 4, maxK: 8 }))
    } else if (q.variant === 'placer-capitale') {
      if (!e.lonlat) return
      const cap = capitalOf(c)
      const km = distanceKm(e.lonlat, [cap.lon, cap.lat])
      const tol = placeToleranceKm(c)
      const ok = km <= tol
      marks = [
        { lon: e.lonlat[0], lat: e.lonlat[1], kind: 'clic' },
        { lon: cap.lon, lat: cap.lat, kind: 'vrai' },
      ]
      highlights = [{ id: c.id, tone: ok ? 'juste' : 'question' }]
      const headline = ok
        ? `Juste : à ${formatKm(km)} de ${cap.name_fr}.`
        : `Non : votre point est à ${formatKm(km)} de ${cap.name_fr}.`
      const details = [
        `L'étoile marque ${cap.name_fr}, la croix votre point. Tolérance pour ${name(c)} : ${formatKm(tol)}.`,
      ]
      const line = capitalsLine(c)
      if (line) details.push(line)
      finish(q, ok, ok ? 'juste' : 'faux', { ok, headline, details }, null)
      tick().then(() => map?.zoomTo(c.id, { right: panelWidth(), context: ok ? 3 : 5, maxK: 8 }))
    }
  }

  function panelWidth(): number {
    const v = getComputedStyle(document.documentElement).getPropertyValue('--panneau')
    const el = document.querySelector('.colonne-panneau') as HTMLElement | null
    return el?.offsetWidth || parseFloat(v) || 400
  }

  // ---------- dérivés d'affichage ----------

  const mapView = $derived.by(() => {
    if (screen !== 'quiz' || !question) return 'atlas' as const
    if (question.mode === 'carte' || question.variant === 'placer-capitale') return 'quiz' as const
    return 'voile' as const
  })

  const mapPick = $derived.by(() => {
    if (screen === 'atlas') return 'fiche' as const
    if (screen !== 'quiz' || !question || answered) return 'aucun' as const
    if (question.variant === 'carte-ou') return 'pays' as const
    if (question.variant === 'placer-capitale') return 'point' as const
    return 'aucun' as const
  })

  const quizSmall = $derived.by(() => {
    if (!ds || !session || !question || question.mode !== 'carte') return []
    return answerPool(ds, 'carte', session.settings.territories)
      .filter((c) => c.small && c.label)
      .map((c) => c.id)
  })

  function questionText(q: Question): { main: string; hint: string | null } {
    const c = q.target
    const plural = c.article_fr === 'les'
    const cap = capitalOf(c)
    switch (q.variant) {
      case 'carte-ou':
        return {
          main: `Où ${plural ? 'sont' : 'est'} ${name(c)} ?`,
          hint: 'Cliquez sur la carte. Molette pour zoomer, glisser pour déplacer.',
        }
      case 'carte-nommer':
        return {
          main: c.kind === 'territoire' ? 'Quel est ce territoire ?' : 'Quel est ce pays ?',
          hint: c.small ? 'Il est marqué en bleu sur la carte.' : 'Il est hachuré en bleu sur la carte.',
        }
      case 'drapeau-nom':
        return { main: 'À qui est ce drapeau ?', hint: null }
      case 'nom-drapeau':
        return { main: `Quel est le drapeau ${deArticle(c.article_fr, c.name_fr)} ?`, hint: 'Touches 1 à 4.' }
      case 'pays-capitale':
        return { main: `Quelle est la capitale ${deArticle(c.article_fr, c.name_fr)} ?`, hint: null }
      case 'capitale-pays':
        return { main: `${cap.name_fr} : capitale de quel pays ?`, hint: null }
      case 'placer-capitale':
        return {
          main: `Placez ${cap.name_fr}, capitale ${deArticle(c.article_fr, c.name_fr)}.`,
          hint: `Cliquez sur la carte ; tolérance ${formatKm(placeToleranceKm(c))}.`,
        }
    }
  }

  function choicesFor(q: Question): Choice[] {
    if (q.variant === 'pays-capitale') return q.choices.map((c) => ({ value: c.id, label: capitalOf(c).name_fr }))
    return q.choices.map((c) => ({ value: c.id, label: c.name_fr }))
  }

  const answerItems = $derived.by(() => {
    if (!ds || !question || !session) return []
    const kind = expects(question)
    if (!kind) return []
    return suggestions(answerPool(ds, question.mode, session.settings.territories), kind)
  })

  const wikiLink = $derived.by(() => {
    const q = question
    if (!q) return null
    if (q.mode === 'capitale') {
      const cap = capitalOf(q.target)
      if (cap.wiki_fr) return { url: cap.wiki_fr, label: `${cap.name_fr} sur Wikipédia` }
    }
    if (q.mode === 'drapeau' && q.target.flag_wiki_fr)
      return { url: q.target.flag_wiki_fr, label: 'Le drapeau sur Wikipédia' }
    return q.target.wiki_fr ? { url: q.target.wiki_fr, label: 'Article Wikipédia' } : null
  })

  function onKey(e: KeyboardEvent) {
    const tag = (e.target as HTMLElement)?.tagName
    if (e.key === 'Enter' && screen === 'quiz' && answered && tag !== 'BUTTON' && tag !== 'A' && tag !== 'INPUT') {
      e.preventDefault()
      next()
    }
    if (e.key === 'Escape' && screen === 'atlas' && ficheId) ficheId = null
  }

  const fiche = $derived(ds && ficheId ? (ds.byId.get(ficheId) ?? null) : null)
  const sessionScore = $derived(session ? session.results.filter((r) => r.ok).length : 0)
  const toReviewNames = $derived.by(() => {
    if (!session || !ds) return []
    const ids = [...new Set(session.results.filter((r) => !r.ok).map((r) => r.id))]
    return ids.map((id) => ds!.byId.get(id)!.name_fr)
  })
</script>

<svelte:window onkeydown={onKey} />

{#if error}
  <main class="erreur feuille">
    <h1>Impossible de charger l'atlas</h1>
    <p>{error}</p>
    <p>Lancez le jeu depuis un serveur local (voir le README) : <code>npm run dev</code>.</p>
  </main>
{:else if !ds || !world}
  <p class="chargement">L'encre sèche…</p>
{:else}
  <AtlasMap
    bind:this={map}
    {ds}
    {world}
    {inks}
    {pigments}
    view={mapView}
    pick={mapPick}
    {highlights}
    {marks}
    {quizSmall}
    {complete}
    layoutKey={screen + (ficheId ?? '')}
    onpick={onMapPick}
  />

  <!-- Atlas personnel -->
  {#if screen === 'atlas' || screen === 'lancement' || screen === 'carnet'}
    <div class="calque atlas" class:avec-fiche={!!fiche}>
      <div class="coin haut-gauche" data-evite-carte>
        <Notebook count={discoveredCount} onopen={() => ((screen = 'carnet'), (ficheId = null))} />
      </div>
      <div class="coin haut-droite" data-evite-carte>
        <SoundToggle on={!!save.settings.sound} ontoggle={toggleSound} />
        {#if ds.isFixture}
          <p class="demo">Données de démonstration</p>
        {/if}
      </div>
      <section class="coin bas-gauche cartouche accueil" aria-labelledby="titre-atlas" data-evite-carte>
        <h1 id="titre-atlas">Mon atlas</h1>
        {#if counts && counts.inkedStates + counts.inkedTerritories === 0}
          <p class="invite">
            Le monde est encore à tracer. Chaque pays que vous reconnaîtrez sera encré sur cette carte.
          </p>
        {:else if counts}
          <p class="compteur">
            {counts.inkedStates}
            {counts.inkedStates > 1 ? 'pays encrés' : 'pays encré'} sur {counts.totalStates}{#if counts.inkedTerritories}, et
              {counts.inkedTerritories}
              {counts.inkedTerritories > 1 ? 'territoires' : 'territoire'}{/if}
          </p>
          {#if counts.toReview}
            <p class="a-revoir">{counts.toReview} à revoir : leur encre pâlit.</p>
          {/if}
        {/if}
        <button class="btn principal" onclick={() => (screen = 'lancement')}>Commencer une session</button>
      </section>
      <div class="coin bas-droite" data-evite-carte>
        <CompassRose onrecentre={() => map?.reset()} onzoom={(f) => map?.zoomBy(f)} />
      </div>
      {#if fiche}
        <div class="colonne-panneau fiche-place" data-evite-carte>
          <CountrySheet
            {ds}
            country={fiche}
            cards={save.cards}
            discovered={save.facts}
            {now}
            onclose={() => (ficheId = null)}
            ondiscover={discover}
          />
        </div>
      {/if}
    </div>
  {/if}

  {#if screen === 'lancement' && preview}
    <div class="calque modal">
      <SessionSetup
        settings={save.settings}
        {preview}
        onchange={updateSettings}
        onstart={startSession}
        oncancel={() => (screen = 'atlas')}
      />
    </div>
  {/if}

  {#if screen === 'carnet'}
    <div class="calque modal voile-carnet">
      <Carnet
        {ds}
        discovered={save.facts}
        onclose={() => (screen = 'atlas')}
        onopencountry={(id) => ((screen = 'atlas'), (ficheId = id))}
      />
    </div>
  {/if}

  <!-- Quiz -->
  {#if screen === 'quiz' && question && session}
    {@const qt = questionText(question)}
    <div class="calque quiz" class:avec-panneau={!!answered}>
      <div class="colonne-principale">
        <header class="barre">
          <div class="cartouche question">
            <h1>{qt.main}</h1>
            {#if qt.hint && !answered}<p class="indice">{qt.hint}</p>{/if}
          </div>
          <div class="progression">
            <p>
              Question {progress.n} sur {progress.total}
            </p>
            <button class="btn discret" onclick={quitSession}>Quitter la session</button>
            <SoundToggle on={!!save.settings.sound} ontoggle={toggleSound} />
          </div>
        </header>

        <div class="milieu">
          {#if question.variant === 'drapeau-nom'}
            <FlagPlate {ds} flags={[question.target]} pickable={false} result={null} />
          {:else if question.variant === 'nom-drapeau'}
            <FlagPlate {ds} flags={question.choices} pickable={true} result={answered?.result ?? null} onpick={onPickFlag} />
          {:else if question.variant === 'pays-capitale'}
            <figure class="carton">
              <Medallion {ds} {world} id={question.target.id} />
              <figcaption>{question.target.name_fr}</figcaption>
            </figure>
          {/if}
        </div>

        <div class="bas">
          {#if expects(question)}
            {#key question}
              <AnswerBox
                style={question.answer}
                choices={choicesFor(question)}
                items={answerItems}
                placeholder={expects(question) === 'capitale' ? 'Nom de la capitale' : 'Nom du pays'}
                result={answered?.result ?? (answered ? { chosen: null, correct: question.target.id } : null)}
                onanswer={onAnswerText}
              />
            {/key}
          {/if}
        </div>
      </div>
      {#if answered}
        <div class="colonne-panneau">
          {#key question}
            <FactPanel
              outcome={answered.outcome}
              fact={factState.fact}
              others={factState.others}
              wiki={wikiLink}
              loading={factState.loading}
              last={session.index + 1 >= session.questions.length}
              onnext={next}
              ondeepen={discover}
            />
          {/key}
        </div>
      {/if}
    </div>
  {/if}

  {#if screen === 'bilan' && session}
    <div class="calque modal">
      <div class="fond-bilan"></div>
      <div class="bilan feuille" role="dialog" aria-modal="true" aria-labelledby="titre-bilan">
        <h2 id="titre-bilan">Session terminée</h2>
        <p class="score">
          {sessionScore}
          {sessionScore > 1 ? 'réponses justes' : 'réponse juste'} sur {session.results.length}.
        </p>
        {#if newlyInked.length}
          <p>
            {newlyInked.length > 1 ? 'Encrés sur votre atlas' : 'Encré sur votre atlas'} :
            {newlyInked.map((c) => c.name_fr).join(', ')}.
          </p>
        {:else}
          <p>Aucun nouveau pays encré cette fois.</p>
        {/if}
        {#if toReviewNames.length}
          <p class="revoir">À revoir bientôt : {toReviewNames.join(', ')}.</p>
        {/if}
        <div class="actions">
          <button class="btn principal" onclick={backToAtlas}>Retour à l'atlas</button>
          <button
            class="btn"
            onclick={() => {
              session = null
              screen = 'lancement'
            }}>Nouvelle session</button
          >
        </div>
      </div>
    </div>
  {/if}
{/if}

{#if grain}
  <div class="grain" style:background-image="url({grain})" aria-hidden="true"></div>
{/if}

<style>
  .chargement {
    position: fixed;
    inset: 0;
    display: grid;
    place-items: center;
    font-family: var(--fell);
    font-style: italic;
    font-size: var(--t-28);
  }
  .erreur {
    position: fixed;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    width: min(560px, calc(100vw - 32px));
    padding: 28px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .grain {
    position: fixed;
    inset: 0;
    pointer-events: none;
    mix-blend-mode: multiply;
    opacity: 0.2;
    z-index: 100;
  }

  .calque {
    position: absolute;
    inset: 0;
    pointer-events: none;
  }
  .coin {
    position: absolute;
    pointer-events: auto;
  }
  .haut-gauche {
    left: 22px;
    top: 18px;
  }
  /* Étiquettes posées sur la carte : vélin presque opaque, pour rester lisibles sur n'importe quel pays. */
  .atlas .haut-gauche,
  .atlas .haut-droite {
    background: color-mix(in srgb, var(--velin-feuille) 94%, transparent);
    border: 1px solid rgba(43, 31, 23, 0.35);
    box-shadow: 0 6px 16px -12px rgba(43, 31, 23, 0.6);
    padding: 4px 10px 4px 6px;
  }
  .atlas .haut-droite {
    padding: 2px 6px;
  }
  .haut-droite {
    right: 20px;
    top: 14px;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 2px;
  }
  .bas-gauche {
    left: 26px;
    bottom: 24px;
  }
  .bas-droite {
    right: 26px;
    bottom: 18px;
  }
  .avec-fiche .bas-droite {
    right: calc(var(--panneau) + 26px);
  }
  .avec-fiche .haut-droite {
    display: none;
  }
  .demo {
    margin: 0;
    font-style: italic;
    font-size: var(--t-16);
    color: var(--encre-2);
    pointer-events: none;
  }

  .accueil {
    width: min(360px, calc(100vw - 52px));
    padding: 18px 22px 20px;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  .accueil h1 {
    font-size: var(--t-37);
    font-style: italic;
  }
  .invite,
  .compteur {
    font-size: var(--t-18);
    line-height: 1.45;
  }
  .compteur {
    font-family: var(--fell);
    font-size: var(--t-21);
  }
  .a-revoir {
    font-size: var(--t-16);
    color: var(--encre-2);
    font-style: italic;
  }
  .accueil .btn {
    margin-top: 8px;
  }

  .colonne-panneau {
    pointer-events: auto;
    height: 100%;
    min-height: 0;
  }
  .fiche-place {
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
  }

  .modal {
    pointer-events: auto;
  }
  .voile-carnet {
    background: rgba(43, 31, 23, 0.2);
  }

  /* Quiz */
  .quiz {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    grid-template-rows: minmax(0, 1fr);
  }
  .colonne-principale {
    min-width: 0;
    display: grid;
    grid-template-rows: auto minmax(0, 1fr) auto;
    padding: 16px 24px 24px;
    gap: 12px;
  }
  .barre {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: start;
    gap: 16px;
  }
  .question {
    grid-column: 2;
    pointer-events: auto;
    padding: 10px 28px 12px;
    text-align: center;
    max-width: min(760px, 62vw);
  }
  .question h1 {
    font-size: var(--t-37);
    overflow-wrap: anywhere;
  }
  .indice {
    font-size: var(--t-16);
    color: var(--encre-2);
    font-style: italic;
    margin-top: 2px;
  }
  .progression {
    grid-column: 3;
    justify-self: end;
    pointer-events: auto;
    text-align: right;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 2px;
    font-size: var(--t-16);
    background: color-mix(in srgb, var(--velin-feuille) 94%, transparent);
    border: 1px solid rgba(43, 31, 23, 0.35);
    padding: 6px 4px 2px 12px;
  }
  .progression p {
    white-space: nowrap;
    padding-right: 8px;
  }
  .avec-panneau .question {
    max-width: min(640px, 48vw);
  }
  .milieu {
    min-height: 0;
    display: grid;
    place-items: center;
  }
  .bas {
    display: flex;
    justify-content: center;
    min-height: 0;
  }
  .carton {
    margin: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    pointer-events: auto;
  }
  .carton figcaption {
    font-family: var(--fell);
    font-style: italic;
    font-size: var(--t-28);
    background: var(--velin-feuille);
    padding: 0 12px;
    text-align: center;
    overflow-wrap: anywhere;
    max-width: 90%;
  }

  /* Bilan */
  .fond-bilan {
    position: absolute;
    inset: 0;
    background: rgba(43, 31, 23, 0.18);
  }
  .bilan {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    width: min(560px, calc(100vw - 32px));
    max-height: calc(100vh - 32px);
    overflow-y: auto;
    padding: 26px 30px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .bilan h2 {
    font-size: var(--t-37);
  }
  .score {
    font-family: var(--fell);
    font-size: var(--t-28);
  }
  .revoir {
    color: var(--encre-2);
  }
  .bilan .actions {
    display: flex;
    gap: 10px;
    margin-top: 10px;
  }
</style>
