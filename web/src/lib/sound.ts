// Sons discrets, synthétisés (aucun fichier : le jeu reste hors ligne). Coupés par défaut.
// Pas de fanfare : un « toc » de bois pour une bonne réponse, un son sourd pour une erreur, un grattement
// de plume quand un pays s'encre sur l'atlas.

let ctx: AudioContext | null = null
let enabled = false

export function setSound(on: boolean) {
  enabled = on
}

function audio(): AudioContext | null {
  if (!enabled) return null
  try {
    ctx ??= new AudioContext()
    if (ctx.state === 'suspended') void ctx.resume()
    return ctx
  } catch {
    return null
  }
}

function tone(freq: number, start: number, dur: number, gain: number, type: OscillatorType = 'sine') {
  const a = audio()
  if (!a) return
  const t = a.currentTime + start
  const o = a.createOscillator()
  const g = a.createGain()
  o.type = type
  o.frequency.setValueAtTime(freq, t)
  g.gain.setValueAtTime(0, t)
  g.gain.linearRampToValueAtTime(gain, t + 0.008)
  g.gain.exponentialRampToValueAtTime(0.0001, t + dur)
  o.connect(g).connect(a.destination)
  o.start(t)
  o.stop(t + dur + 0.02)
}

/** Bonne réponse : deux notes de bois, une quinte, très courtes. */
export function soundRight() {
  tone(587, 0, 0.16, 0.05, 'triangle')
  tone(880, 0.07, 0.22, 0.04, 'triangle')
}

/** Erreur : un son sourd et bref, pas une alarme. */
export function soundWrong() {
  tone(165, 0, 0.25, 0.06, 'sine')
}

/** Plume qui gratte le papier : bruit filtré, court. */
export function soundInk() {
  const a = audio()
  if (!a) return
  const dur = 0.35
  const buf = a.createBuffer(1, Math.floor(a.sampleRate * dur), a.sampleRate)
  const d = buf.getChannelData(0)
  for (let i = 0; i < d.length; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / d.length)
  const src = a.createBufferSource()
  src.buffer = buf
  const f = a.createBiquadFilter()
  f.type = 'bandpass'
  f.frequency.value = 3200
  f.Q.value = 0.9
  const g = a.createGain()
  g.gain.value = 0.025
  src.connect(f).connect(g).connect(a.destination)
  src.start()
}
