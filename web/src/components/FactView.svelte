<script lang="ts">
  // Un fait : titre, texte court ; déplié : texte long et sources (citation + lien).
  import { displayQuote, typo } from '../lib/text'
  import type { Fact } from '../lib/types'

  interface Props {
    fact: Fact
    expanded?: boolean
    headingLevel?: 2 | 3 | 4
  }
  let { fact, expanded = false, headingLevel = 3 }: Props = $props()

  const TOPIC: Record<string, string> = {
    histoire: 'histoire',
    geographie: 'géographie',
    culture: 'culture',
    politique: 'politique',
    economie: 'économie',
    drapeau: 'drapeau',
  }

  function sourceLabel(url: string): string {
    try {
      const u = new URL(url)
      const title = decodeURIComponent(u.pathname.split('/').pop() ?? '').replace(/_/g, ' ')
      const lang = u.hostname.split('.')[0]
      return `Wikipédia${lang === 'fr' ? '' : ' (' + lang + ')'} : ${title}`
    } catch {
      return url
    }
  }
</script>

<article class="fait">
  <p class="contexte">
    {[fact.era, TOPIC[fact.topic ?? ''] ?? fact.topic].filter(Boolean).join(', ')}
  </p>
  <svelte:element this={'h' + headingLevel} class="titre">{typo(fact.title)}</svelte:element>
  <p class="court">{typo(fact.short)}</p>
  {#if expanded}
    {#if fact.long}
      <div class="long">
        {#each fact.long.split(/\n\s*\n/) as para, i (i)}
          <p>{typo(para)}</p>
        {/each}
      </div>
    {/if}
    {#if fact.sources?.length}
      <ul class="sources">
        {#each fact.sources as s, i (i)}
          <li>
            {#if s.quote}
              {@const paras = displayQuote(s.quote)}
              <blockquote lang="">
                {#each paras as para, j (j)}
                  <p>{j === 0 ? '«\u00a0' : ''}{para}{j === paras.length - 1 ? '\u00a0»' : ''}</p>
                {/each}
              </blockquote>
            {/if}
            <a href={s.url} target="_blank" rel="noopener noreferrer">{sourceLabel(s.url)}</a>
          </li>
        {/each}
      </ul>
    {/if}
  {/if}
</article>

<style>
  .fait {
    display: flex;
    flex-direction: column;
    gap: 4px;
    min-width: 0;
  }
  .contexte {
    font-size: var(--t-14);
    color: var(--encre-2);
    font-style: italic;
  }
  .titre {
    font-family: var(--fell);
    font-size: var(--t-21);
    line-height: 1.2;
    font-weight: 400;
    margin: 0;
    overflow-wrap: anywhere;
  }
  .court,
  .long p {
    font-size: var(--t-18);
    line-height: 1.55;
    overflow-wrap: break-word;
  }
  .long {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 6px;
  }
  .sources {
    list-style: none;
    margin: 10px 0 0;
    padding: 10px 0 0;
    border-top: 1px solid rgba(43, 31, 23, 0.25);
    display: flex;
    flex-direction: column;
    gap: 10px;
    font-size: var(--t-16);
  }
  blockquote {
    margin: 0 0 2px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-style: italic;
    color: var(--encre-2);
    overflow-wrap: anywhere;
  }
  .sources a {
    overflow-wrap: anywhere;
  }
</style>
