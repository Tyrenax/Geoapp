# Geo Atlas : le jeu (rôle Front)

Vite + TypeScript + Svelte 5. Plan de design : `../docs/DESIGN.md`. Contrat de données : `../docs/ARCHITECTURE.md`.

## Lancer

```sh
npm install
npm run dev                       # http://localhost:5173
npm run build                     # dist/, chemins relatifs
python -m http.server -d dist 8405   # http://localhost:8405
```

Données : le jeu charge `data/` (généré par le rôle Données dans `public/data/`) dès qu'il y trouve
`countries.json`, sinon la fixture `fixtures/` (14 entités, faits marqués `[FICTIF]`). Le bandeau
« Données de démonstration » s'affiche en haut à droite tant que la fixture est utilisée.

## Vérifier

```sh
npm test            # vitest : planificateur, comparaison des réponses, distracteurs
npm run check       # svelte-check + tsc
npm run e2e         # Playwright sur le build : parcours (flows) et contrôle visuel (audit)
```

- `tests/e2e/flows.spec.ts` : parcours à vrais clics souris (1600×900, 1280×720).
- `tests/e2e/audit.spec.ts` : contrôle visuel en 1280×720, 1600×900, 1920×1080 : texte ou image qui sort
  de sa case, élément interactif hors écran ou recouvert (`elementFromPoint`), centrage ; sur les noms,
  capitales, faits et astuces les plus longs des données.
- Captures : `captures/` (ignoré par git). Préfixe = taille d'écran ; `audit-…` pour le contrôle visuel.

Crochets de test (`window.__quiz`, `window.__geoTest`, `window.__atlas`) : ils lisent la question en cours
et forcent une session précise ; les réponses passent toujours par de vrais clics.

## Organisation

- `src/lib/` : logique sans interface (chargement, texte, planificateur SM-2, questions, progression,
  projection, fond de carte en canvas).
- `src/components/` : écrans et ornements. `AtlasMap.svelte` pilote d3 (zoom, encrage) ; le fond (mer,
  lignes d'eau, côtes) est un canvas (`lib/basemap.ts`) redessiné en fin de geste.
- Progression : `localStorage` (`geo-atlas.v1`) ; le jeu marche sans.
