// Révision espacée : SM-2 allégé, une carte par couple (entité, mode).
// « Maîtrisé » = la dernière réponse était juste (reps ≥ 1). L'encre pâlit quand la révision est due.

export type Grade = 'faux' | 'difficile' | 'juste'

export interface Card {
  key: string // « carte:BOL » ; phase 2 : « ville:Q1491 »
  ease: number
  interval: number // jours
  reps: number // réponses justes consécutives
  lapses: number
  due: number // ms
  last: number // ms
  seen: number
}

export const DAY = 86_400_000
// Une carte ratée revient dans une prochaine série, au plus tôt une heure après (pas dans la série en cours).
export const RELEARN = 60 * 60_000

export function newCard(key: string): Card {
  return { key, ease: 2.5, interval: 0, reps: 0, lapses: 0, due: 0, last: 0, seen: 0 }
}

export function review(card: Card, grade: Grade, now: number): Card {
  const c = { ...card, seen: card.seen + 1, last: now }
  if (grade === 'faux') {
    c.reps = 0
    c.lapses += 1
    c.ease = Math.max(1.3, c.ease - 0.2)
    c.interval = 0
    c.due = now + RELEARN
    return c
  }
  c.reps += 1
  if (c.reps === 1) c.interval = 1
  else if (c.reps === 2) c.interval = grade === 'juste' ? 3 : 2
  else c.interval = Math.max(c.interval + 1, Math.round(c.interval * c.ease * (grade === 'juste' ? 1 : 0.8)))
  if (grade === 'difficile') c.ease = Math.max(1.3, c.ease - 0.15)
  c.due = now + c.interval * DAY
  return c
}

export function isMastered(c: Card | undefined): boolean {
  return !!c && c.reps >= 1
}

export function isDue(c: Card | undefined, now: number): boolean {
  return !!c && c.seen > 0 && c.due <= now
}

/**
 * Fraîcheur de l'encre, 1 = encre neuve. Décroît après l'échéance jusqu'à 0,3 au bout de deux
 * intervalles de retard.
 */
export function freshness(c: Card | undefined, now: number): number {
  if (!c || !isMastered(c) || now <= c.due) return 1
  const late = now - c.due
  const span = Math.max(1, c.interval) * DAY * 2
  return Math.max(0.3, 1 - (0.7 * late) / span)
}

export interface Pick {
  key: string
  isNew: boolean
}

/**
 * Compose une session : d'abord les cartes dues (les plus en retard), au plus `maxDue` ;
 * puis des nouvelles (`newKeys` déjà triées par priorité) ; puis, s'il manque encore des questions,
 * les autres dues, puis les cartes vues les plus proches de leur échéance.
 * `group` regroupe les cartes d'une même entité : une seule carte par groupe dans la session.
 */
export function pickSession(
  keys: string[],
  cards: Record<string, Card>,
  now: number,
  size = 15,
  maxDue = 10,
  group: (key: string) => string = (k) => k,
): Pick[] {
  const due: Card[] = []
  const later: Card[] = []
  const fresh: string[] = []
  for (const k of keys) {
    const c = cards[k]
    if (!c || c.seen === 0) fresh.push(k)
    else if (c.due <= now) due.push(c)
    else later.push(c)
  }
  due.sort((a, b) => a.due - b.due)
  // bouche-trou (filtre restreint, tout déjà vu) : d'abord les cartes qu'on n'a pas vues depuis un moment,
  // et parmi les vues récemment, les plus anciennes, pour ne pas reprendre la série précédente
  const recent = (c: Card) => (now - c.last < RELEARN ? 1 : 0)
  later.sort((a, b) => recent(a) - recent(b) || (recent(a) ? a.last - b.last : a.due - b.due))
  const out: Pick[] = []
  const used = new Set<string>()
  const take = (k: string, isNew: boolean) => {
    if (out.length >= size || used.has(group(k))) return
    used.add(group(k))
    out.push({ key: k, isNew })
  }
  due.slice(0, maxDue).forEach((c) => take(c.key, false))
  fresh.forEach((k) => take(k, true))
  due.slice(maxDue).forEach((c) => take(c.key, false))
  later.forEach((c) => take(c.key, false))
  return out
}
