# Geo Atlas — plan de design (rôle Front)

Sujet : un jeu pour apprendre la géographie, seul, à son bureau. Public : Josca, adulte curieux qui veut
retenir drapeaux, positions et capitales, et apprendre une chose vraie à chaque réponse.
Travail premier de l'écran : montrer **son propre atlas**, qui se dessine à mesure qu'on apprend.

Référence visuelle : les mappemondes gravées et coloriées à la main (Ortelius, *Typus Orbis Terrarum*, 1570 ;
Blaeu ; cartes marines du XIXᵉ avec leurs « lignes d'eau »). On en reprend des **techniques**, pas un thème
« parchemin » : le coloriage au pinceau le long des frontières, les lignes d'eau gravées autour des côtes,
le monde dans un ovale, le cartouche, la rose des vents, les planches de pavillons.

## Couleurs (pigments réels des cartes coloriées)

| Nom | Hex | Rôle |
|---|---|---|
| Vélin | `#DCD3BB` | le papier (plus gris et plus sourd qu'un crème : chiffon vieilli) |
| Vélin clair | `#E7E0CC` | l'intérieur de l'ovale du monde, les feuilles posées dessus |
| Encre ferro-gallique | `#2B1F17` | texte, contours encrés, traits gravés |
| Bleu de Prusse | `#1D3A5A` | lignes d'eau, actions, focus, question en cours |
| Vert-de-gris | `#3E7A68` | lavis, réponse juste |
| Carmin | `#9A2537` | sceau, réponse fausse, lavis |
| Gomme-gutte | `#C4982A` | lavis |

Les lavis des pays utilisent quatre pigments (vert-de-gris, carmin, gomme-gutte, bleu de Prusse) à faible
opacité, attribués par **coloriage de graphe** sur les voisins : deux pays voisins n'ont jamais le même
pinceau, comme sur les cartes d'époque.

## Typographies (auto-hébergées, `@fontsource/*`)

- **IM FELL English** (romain + italique) : les caractères de John Fell, imprimés à Oxford dans les années
  1670, l'époque de Blaeu et Sanson. Rôle : lettrage de la carte (noms calligraphiés en italique), titre du
  cartouche, énoncé des questions. Jamais en dessous de 18 px (la fonte est rugueuse, c'est voulu).
- **Alegreya** (romain, italique, chiffres elzéviriens) : texte courant, faits, boutons, saisie. Dessinée
  pour la lecture longue, d'origine calligraphique : elle tient compagnie à Fell sans l'imiter.
- Échelle (Bringhurst, intervalles de la quarte) : 14 · 16 · 18 · 21 · 28 · 37 · 50 px. Texte courant
  18 px / interligne 1,5 ; lignes ≤ 68 caractères.
- Les petites capitales d'Alegreya SC servent une seule fois : les noms des **océans** sur la carte, selon la
  convention cartographique (mers en capitales espacées, pays en italique). Aucun libellé d'interface en
  capitales.

## Principes

1. **Une seule chose mémorable : l'encrage.** Terra incognita = côtes en pointillé à peine posées, aucun
   pays tracé. Un pays maîtrisé dans 1 mode reçoit son contour à l'encre ; 2 modes : le **lavis de bordure**
   (bande de couleur peinte le long de la frontière, à l'intérieur, la technique réelle des cartes
   coloriées) ; 3 modes : son **nom calligraphié** en italique. Le retour à l'atlas après une session est le
   seul moment animé non provoqué : les pays gagnés se tracent (le trait court le long de la frontière), puis
   le lavis se dépose.
2. **Les pays à revoir pâlissent** : l'encre passe progressivement quand la révision est due, et un pays raté
   retombe en trace effacée (pas en terra incognita : on voit qu'on l'a su).
3. Le reste est **sobre et gravé** : traits fins, pas d'ombres portées, pas de dégradés décoratifs, pas de
   cartes arrondies empilées. Les panneaux sont des feuilles de vélin clair posées sur la carte, bord net,
   filet double à l'encre seulement pour le cartouche.
4. **Les ornements travaillent** : la rose des vents recentre la carte ; le cartouche porte le titre et le
   compteur ; le sceau de cire marque une erreur ; la planche de pavillons est le quiz « nom → drapeau ».
5. Texte aligné à gauche partout, sauf l'énoncé de la question (centré dans son cartouche, comme un titre de
   carte).

## Mises en page (1280×720 à 1920×1080, la carte occupe tout l'écran)

### Atlas personnel (accueil)
```
+--------------------------------------------------------------------------------+
|   vélin (hors du monde)                                                        |
|        .-----------------------------------------------------------.           |
|      /  ~ lignes d'eau ~   côtes en pointillé (terra incognita)      \         |
|     |      pays encrés : contour / lavis de bordure / nom italique     |       |
|     |  OCÉAN ATLANTIQUE        [Bolivie]     [France]                  |       |
|      \                                                              /          |
|        '-----------------------------------------------------------'           |
| +==========================+                                     (rose)  [+]   |
| ‖ Mon atlas                ‖                                     des     [−]   |
| ‖ 37 pays encrés sur 197   ‖                                     vents         |
| ‖ 12 à revoir              ‖                                    (recentre)     |
| ‖ [ Commencer une session ]‖                                                   |
| +==========================+                                                   |
+--------------------------------------------------------------------------------+
```
Premier lancement (0 pays encré) : l'écran est déjà complet par les côtes en pointillé, les lignes d'eau,
les noms d'océans, la rose et le cartouche ; le cartouche dit « Le monde est encore à tracer. Chaque pays que
vous reconnaîtrez sera encré sur cette carte. » et n'a qu'un bouton, « Commencer une session ».
Juste / faux ne passe jamais par la seule couleur : toujours le mot (« Juste. » / « Non : … ») et le sceau.
Clic sur un pays encré → sa fiche (feuille à droite). Survol : nom en italique au curseur, seulement pour
les pays encrés (la terra incognita ne se nomme pas).

### Lancement d'une session (feuille posée au centre)
```
+------------------------------------------------+
| Nouvelle session                               |
|                                                |
| Mode   ( ) Carte   ( ) Drapeaux  ( ) Capitales |
|        ( ) Tout mêler                          |
| Réponse  ( ) Quatre choix  ( ) Saisie libre    |
| Régions [x] Afrique [x] Amérique du Nord ...   |
|         [ ] Inclure les territoires            |
|                                                |
| 15 questions : 6 à revoir, 9 nouvelles         |
| [ Commencer ]                  [ Annuler ]     |
+------------------------------------------------+
```

### Quiz carte (« Où est … ? » / pays surligné → le nommer)
```
+--------------------------------------------------------------------------------+
|              +=====================================+          Question 4 sur 15 |
|              ‖        Où est la Bolivie ?           ‖                  [Quitter] |
|              +=====================================+                           |
|        .-----------------------------------------------------------.           |
|      /   tous les pays tracés au crayon, sans nom ni couleur         \         |
|     |    (pays surligné en bleu de Prusse pour « nommer »)            |        |
|      \                                                              /          |
|        '-----------------------------------------------------------'           |
|                    [ saisie avec complétion / quatre choix ]          (rose)   |
+--------------------------------------------------------------------------------+
```

### Quiz drapeau
```
drapeau → nom                              nom → drapeau (planche de pavillons)
+--------------------------------+         +--------------------------------------+
|  ‖ Quel est ce drapeau ? ‖     |         |   ‖ Quel est le drapeau du Pérou ? ‖ |
|   +----------------------+     |         |   +--------+   +--------+            |
|   |   drapeau, grand,    |     |         |   |  [1]   |   |  [2]   |            |
|   |   filet d'encre      |     |         |   +--------+   +--------+            |
|   +----------------------+     |         |   +--------+   +--------+            |
|  [ saisie / quatre choix ]     |         |   |  [3]   |   |  [4]   |            |
+--------------------------------+         +--------------------------------------+
```
La carte reste derrière, voilée, sans rien surligner.

### Quiz capitale
```
pays → capitale : « Quelle est la capitale du Pérou ? » + médaillon : le pays seul, encré, dans un petit
                  ovale (repère visuel, pas d'indice textuel)
capitale → pays : « Lima est la capitale de… ? »
placer          : « Placez Lima » → clic sur la carte ; réponse juste si ≤ tolérance (km, selon la taille
                  du pays) ; la vraie position est piquée d'une étoile à l'encre, distance tracée en pointillé.
```

### Panneau de fait (après chaque réponse, feuille à droite)
```
                                              +-------------------------------+
                                              | (sceau carmin si erreur)      |
                                              | Juste : la Bolivie.           |
                                              |  ou                           |
                                              | C'était le Pérou, à 2 300 km. |
                                              | Astuce : …                    |
                                              |-------------------------------|
                                              | Un pays nommé d'après Bolívar |
                                              | 1 à 2 phrases.                |
                                              | [Approfondir] [Wikipédia]     |
                                              |                               |
                                              | [ Question suivante ]  Entrée |
                                              +-------------------------------+
```
« Approfondir » déplie dans la même feuille : texte long, autres faits, sources cliquables (citation).

### Fiche Atlas d'un pays (feuille à droite, ou pleine hauteur)
```
+---------------------------------------------+
| [drapeau]  Bolivie                          |
|            État plurinational de Bolivie    |
| Capitales  Sucre (constitutionnelle)        |
|            La Paz (siège du gouvernement)   |
| Population 12 000 000 (2024)                |
| Superficie 1 098 581 km²                    |
| Ta progression : carte ✓  drapeau ·  capitale ✓ (à revoir le 14 oct.)
| Faits (tous, avec sources)                  |
| Astuces                                     |
| Wikipédia                                   |
+---------------------------------------------+
```

Les faits pas encore découverts sont repliés dans la fiche (« 2 faits à découvrir ») et se révèlent un par
un d'un clic : la fiche montre tout, sans gâcher la découverte en jouant. Compteur « 3 faits découverts sur 6 ».

### Carnet de l'explorateur (écran plein, la carte voilée derrière)
```
+--------------------------------------------------------------------------------+
| Carnet de l'explorateur            [ rechercher dans les faits…        ]  [×]  |
| 23 faits découverts sur 1 240                                                  |
| Classer par ( ) découverte  ( ) pays  ( ) continent  ( ) thème                 |
|--------------------------------------------------------------------------------|
| Bolivie (2/6)                         |  Un pays nommé d'après Bolívar          |
|   Un pays nommé d'après Bolívar  1825 |  1825, histoire                          |
|   La Paz, capitale la plus haute      |  texte court                             |
| Pérou (1/5)                           |  [Approfondir]  Bolivie : voir la fiche  |
|   …                                   |  sources (citations)                     |
+--------------------------------------------------------------------------------+
```
Accès depuis l'atlas : en haut à gauche, hors de l'ovale, un **carnet relié gravé** (vignette d'encre, avec
le nombre de faits découverts inscrit sur sa tranche) ; c'est un bouton, comme la rose des vents.
Liste à gauche (groupée selon le classement, défilante), le fait choisi à droite. Un pays dont tous les faits
sont découverts reçoit sur l'atlas un petit astérisque d'encre près de son nom (la marque discrète).

### Phase 2 (pas maintenant) : autres villes
Les questions sont produites par des « générateurs » indexés par mode (`carte`, `drapeau`, `capitale`) ;
une cible de quiz est un `{ kind: 'pays' | 'ville', id }`. Ajouter des villes = un nouveau générateur et une
nouvelle clé de carte de révision (`ville:<qid>`), sans toucher au planificateur ni à l'atlas.

## Relecture contre le brief (seconde passe) — ce que j'ai changé

- **Palette** : premier jet « parchemin #F1E6C8 + sépia + rouge brique ». C'est exactement le tic
  crème + serif + terracotta. Remplacé par les pigments documentés du coloriage à la main (vert-de-gris,
  carmin, gomme-gutte, bleu de Prusse) sur un vélin plus gris ; l'accent d'action est le bleu de Prusse,
  pas une couleur chaude.
- **Encre « par intensité »** : premier jet = remplissage plus ou moins foncé (une carte choroplèthe de
  plus). Remplacé par trois gestes de cartographe distincts (contour, lavis de bordure, nom calligraphié).
- **Projection** : premier jet Natural Earth, la projection de tous les sites. Remplacé par un monde dans un
  ovale (Hammer, centrée à 10° E pour ne pas couper la Tchoukotka), l'ovale d'Ortelius, avec lignes d'eau.
- **Compteur** : premier jet = gros chiffre + petit libellé + barre de progression (le traitement par
  défaut). Remplacé par une phrase dans le cartouche : « 37 pays encrés sur 197 ».
- **Libellés** : retiré les surtitres en capitales (« MODE », « RÉGIONS ») du lancement de session ; les
  groupes sont des phrases courtes en minuscules. Pas de « → » dans les boutons.
- **Mouvement** : retiré les apparitions en fondu de chaque panneau. Seul moment orchestré : l'encrage au
  retour sur l'atlas. Les feuilles apparaissent sans animation (ou très brève, en réponse à une action).
- **Numérotation** : « Question 4 sur 15 » reste (c'est une vraie séquence). Pas de numéros décoratifs.

## Notes de construction

- UI en **Svelte 5** : plusieurs écrans avec un état partagé (session, file de questions, progression) ;
  les runes donnent une réactivité fine sans bibliothèque d'état. La carte est un composant qui pilote d3
  impérativement (zoom, transitions) ; Svelte ne rend pas les 250 chemins.
- Carte : pays en SVG, contours en `vector-effect: non-scaling-stroke` (traits constants au zoom). Le fond
  (mer, lignes d'eau, graticule, côtes en pointillé) est un canvas : anneaux de la couche `land` empilés
  (trait bleu puis trait vélin), côtes simplifiées selon le zoom (topojson-simplify). En SVG sur les vraies
  données, ces 12 tracés des côtes donnaient 0,7 image/s au zoom ; le canvas suit le geste par une
  transformation CSS et n'est redessiné qu'à la fin (~85 ms une fois, 4 ms par image pendant le geste).
- IM FELL descend à 14 px pour les noms calligraphiés sur la carte (contrainte de place) ; ailleurs ≥ 18 px.
- Marqueurs des petites entités : zone de clic réduite (7 px) à l'échelle du monde, sinon le Vatican
  masquait le centre de l'Italie ; 11 px une fois zoomé.
- Grain du papier : texture de bruit calculée une fois dans un canvas, posée au-dessus en `multiply`.
