# Rapport de données — Geo Atlas

Généré par `tools/data/check_data.py` le 2026-10-13. Ne pas éditer à la main : les décisions se règlent dans `tools/data/curation.py` (`CAPITALS`, `DECISIONS`…).

- Entités : 250 (197 États, 53 territoires)
- Désaccords relevés : 359 ; **non tranchés : 0**
- Articles Wikipédia FR des pays en cache : 249/250 (pas de pré-remplissage en masse : décision du coordinateur, limite Wikimedia de 10 requêtes/min ; les rédacteurs de faits récupèrent ce qu'ils citent)

## Capitales réglées à la main

| id | capitale(s) et rôle |
|---|---|
| BEN | **Porto-Novo** — capitale officielle ; **Cotonou** — siège du gouvernement |
| BES | **Kralendijk** — chef-lieu de Bonaire |
| BOL | **Sucre** — capitale constitutionnelle ; **La Paz** — siège du gouvernement |
| CHE | **Berne** — ville fédérale, siège des autorités fédérales |
| CIV | **Yamoussoukro** — capitale politique et administrative ; **Abidjan** — capitale économique |
| ESH | **Laâyoune** — ville principale du territoire (statut disputé) |
| GNQ | **Ciudad de la Paz** — capitale depuis janvier 2026, à la place de Malabo |
| IDN | **Jakarta** — capitale (transfert vers Nusantara prévu, décret présidentiel non signé) |
| ISR | **Jérusalem** — capitale proclamée par Israël, statut contesté sur le plan international |
| LKA | **Sri Jayawardenapura** — capitale officielle ; **Colombo** — capitale commerciale |
| MSR | **Brades** — capitale de fait ; **Plymouth** — capitale officielle, abandonnée depuis l'éruption de 1997 |
| MYS | **Kuala Lumpur** — capitale ; **Putrajaya** — siège du gouvernement |
| NLD | **Amsterdam** — capitale ; **La Haye** — siège du gouvernement |
| NRU | **Yaren** — siège du gouvernement (pas de capitale officielle) |
| PSE | **Jérusalem-Est** — capitale proclamée par l'État de Palestine ; **Ramallah** — siège de fait de l'Autorité palestinienne |
| SGS | **King Edward Point** — siège administratif ; **Grytviken** — ancienne station baleinière voisine |
| SJM | **Longyearbyen** — centre administratif du Svalbard |
| SWZ | **Mbabane** — capitale administrative ; **Lobamba** — capitale royale et législative |
| YEM | **Sanaa** — capitale constitutionnelle, contrôlée par les Houthis ; **Aden** — capitale provisoire du gouvernement reconnu |
| ZAF | **Pretoria** — capitale administrative ; **Le Cap** — capitale législative ; **Bloemfontein** — capitale judiciaire |
| ATA | — pas de capitale : continent sans État |
| BVT | — île inhabitée, pas de capitale |
| HKG | — région administrative spéciale, pas de capitale distincte |
| HMD | — îles inhabitées, pas de capitale |
| MAC | — région administrative spéciale, pas de capitale distincte |
| TKL | — pas de capitale : le siège de l'administration tourne entre les trois atolls |
| UMI | — îles dispersées, pas de capitale |

Notes de vérification : Guinée équatoriale : Ciudad de la Paz est capitale depuis janvier 2026 (Wikidata P36 préférée depuis le 2026-01-03 ; Wikipédia FR « Ciudad de la Paz » et « Malabo »). Indonésie : Jakarta reste la capitale ; le transfert vers Nusantara attend un décret présidentiel non signé, objectif 17 août 2028 (Wikipédia FR « Nusantara (ville) », Wikidata : Nusantara déprécié). Myanmar : Naypyidaw ; Kazakhstan : Astana ; Suisse : Berne, « ville fédérale » ; Nauru : pas de capitale officielle, Yaren siège du gouvernement ; Israël / Palestine : rôles explicites sans trancher le statut de Jérusalem.

## Drapeaux réglés à la main

| id | fichier | en quiz | note |
|---|---|---|---|
| AFG | Flag of the Taliban.svg | non | Deux drapeaux coexistent : le drapeau blanc de l'Émirat islamique depuis 2021 et le tricolore noir-rouge-vert, encore utilisé à l'ONU. |
| ATA | — | non | L'Antarctique n'a pas de drapeau officiel ; celui-ci est un drapeau proposé. |
| BES | Flag of the Netherlands.svg | non | Communes néerlandaises : le drapeau officiel est celui des Pays-Bas (Bonaire, Saint-Eustache et Saba ont chacune le leur). |
| BLM | Flag of France.svg | non | Collectivité française : le drapeau officiel est celui de la France. |
| ESH | — | non | Le territoire n'a pas de drapeau reconnu par tous ; celui-ci est le drapeau de la République arabe sahraouie démocratique. |
| GLP | Flag of France.svg | non | Département français : le drapeau officiel est celui de la France. |
| GUF | Flag of France.svg | non | Département français : le drapeau officiel est celui de la France. |
| IOT | Flag of the Commissioner of the British Indian Ocean Territory.svg | non | Pavillon du commissaire du territoire, revendiqué par Maurice ; le drapeau du territoire a changé en 2025. |
| MAF | Flag of France.svg | non | Collectivité française : le drapeau officiel est celui de la France. |
| MTQ | Flag of France.svg | non | Département français : le drapeau officiel est celui de la France. |
| MYT | Flag of France.svg | non | Département français : le drapeau officiel est celui de la France. |
| NCL | Flag of FLNKS.svg | non | La Nouvelle-Calédonie hisse côte à côte le drapeau français et le drapeau kanak (celui-ci) ; elle n'a pas de drapeau propre unique. |
| REU | Flag of France.svg | non | Département français : le drapeau officiel est celui de la France. |
| SHN | Flag of Saint Helena.svg | non | Drapeau de Sainte-Hélène ; Ascension et Tristan da Cunha ont chacune le leur. |
| SPM | Flag of France.svg | non | Collectivité française : le drapeau officiel est celui de la France. |
| UMI | Flag of the United States (DDD-F-416E specifications).svg | non |  |
| WLF | Flag of France.svg | non | Collectivité française : le drapeau officiel est celui de la France. |

Drapeau identique à celui de l'État souverain (flag_shared_with, hors quiz) : BES, BLM, BVT, GLP, GUF, HMD, MAF, MTQ, MYT, REU, SJM, SPM, UMI, WLF.
Repli lipis/flag-icons (ratio 4:3, pas les vraies proportions) : ATA, ESH.

## Plaque d'immatriculation — code enregistré à l'ONU (tableau Wikipédia EN) contre Wikidata

| id | désaccord | décision |
|---|---|---|
| AGO | ONU : — ; Wikidata : ['ANG'] | règle : aucun code enregistré à l'ONU pour cette entité (tableau Wikipédia EN) → null |
| AIA | ONU : ['AXA'] ; Wikidata : — | règle : code enregistré à l'ONU (Convention de Vienne), tableau Wikipédia EN |
| BLR | ONU : ['BY'] ; Wikidata : ['BLR'] | règle : code enregistré à l'ONU (Convention de Vienne), tableau Wikipédia EN |
| BTN | ONU : — ; Wikidata : ['BHT'] | règle : aucun code enregistré à l'ONU pour cette entité (tableau Wikipédia EN) → null |
| CHN | ONU : — ; Wikidata : ['RC'] | règle : aucun code enregistré à l'ONU pour cette entité (tableau Wikipédia EN) → null |
| CPV | ONU : — ; Wikidata : ['CV'] | règle : aucun code enregistré à l'ONU pour cette entité (tableau Wikipédia EN) → null |
| CUB | ONU : ['CU'] ; Wikidata : ['C'] | règle : code enregistré à l'ONU (Convention de Vienne), tableau Wikipédia EN |
| CUW | ONU : — ; Wikidata : ['NA'] | null confirmé : CW n'apparaît que parmi les codes non officiels du tableau EN |
| EGY | ONU : ['EG'] ; Wikidata : ['ET'] | règle : code enregistré à l'ONU (Convention de Vienne), tableau Wikipédia EN |
| FLK | ONU : — ; Wikidata : ['FX'] | règle : aucun code enregistré à l'ONU pour cette entité (tableau Wikipédia EN) → null |
| GIB | ONU : ['GBZ'] ; Wikidata : — | règle : code enregistré à l'ONU (Convention de Vienne), tableau Wikipédia EN |
| GRL | ONU : — ; Wikidata : ['KN'] | null confirmé : KN n'est pas enregistré à l'ONU ; le tableau EN le range dans les codes abandonnés avec la mention « Unofficial. The official code is DK » |
| HKG | ONU : ['HK'] ; Wikidata : — | règle : code enregistré à l'ONU (Convention de Vienne), tableau Wikipédia EN |
| HND | ONU : ['HN'] ; Wikidata : — | règle : code enregistré à l'ONU (Convention de Vienne), tableau Wikipédia EN |
| KGZ | ONU : ['KG'] ; Wikidata : ['KS'] | règle : code enregistré à l'ONU (Convention de Vienne), tableau Wikipédia EN |
| KHM | ONU : ['KH'] ; Wikidata : ['K'] | règle : code enregistré à l'ONU (Convention de Vienne), tableau Wikipédia EN |
| KNA | ONU : — ; Wikidata : — | null confirmé : KAN n'apparaît que parmi les codes non officiels du tableau EN |
| MDV | ONU : ['MV'] ; Wikidata : — | règle : code enregistré à l'ONU (Convention de Vienne), tableau Wikipédia EN |
| MKD | ONU : ['NMK'] ; Wikidata : ['MK'] | règle : code enregistré à l'ONU (Convention de Vienne), tableau Wikipédia EN |
| MMR | ONU : ['MYA'] ; Wikidata : ['BUR'] | règle : code enregistré à l'ONU (Convention de Vienne), tableau Wikipédia EN |
| MTQ | ONU : — ; Wikidata : ['972'] | règle : aucun code enregistré à l'ONU pour cette entité (tableau Wikipédia EN) → null |
| MYT | ONU : — ; Wikidata : ['976'] | règle : aucun code enregistré à l'ONU pour cette entité (tableau Wikipédia EN) → null |
| OMN | ONU : ['OM'] ; Wikidata : — | règle : code enregistré à l'ONU (Convention de Vienne), tableau Wikipédia EN |
| PRI | ONU : — ; Wikidata : — | null confirmé : PR n'apparaît que parmi les codes non officiels du tableau EN |
| PRK | ONU : — ; Wikidata : ['KP'] | règle : aucun code enregistré à l'ONU pour cette entité (tableau Wikipédia EN) → null |
| PSE | ONU : — ; Wikidata : ['PS'] | null confirmé : P (avec la lettre arabe ف) n'apparaît que parmi les codes non officiels du tableau EN |
| REU | ONU : — ; Wikidata : ['974'] | règle : aucun code enregistré à l'ONU pour cette entité (tableau Wikipédia EN) → null |
| SDN | ONU : ['SUD'] ; Wikidata : — | règle : code enregistré à l'ONU (Convention de Vienne), tableau Wikipédia EN |
| TCD | ONU : ['TCH'] ; Wikidata : ['TCH', 'TD'] | règle : code enregistré à l'ONU (Convention de Vienne), tableau Wikipédia EN |
| TLS | ONU : — ; Wikidata : ['TL'] | règle : aucun code enregistré à l'ONU pour cette entité (tableau Wikipédia EN) → null |
| TON | ONU : ['TO'] ; Wikidata : — | règle : code enregistré à l'ONU (Convention de Vienne), tableau Wikipédia EN |
| TWN | ONU : ['RC'] ; Wikidata : — | règle : code enregistré à l'ONU (Convention de Vienne), tableau Wikipédia EN |
| URY | ONU : ['ROU'] ; Wikidata : ['UY'] | règle : code enregistré à l'ONU (Convention de Vienne), tableau Wikipédia EN |
| VGB | ONU : ['BVI'] ; Wikidata : — | règle : code enregistré à l'ONU (Convention de Vienne), tableau Wikipédia EN |
| XKX | ONU : ['RKS'] ; Wikidata : — | règle : code enregistré à l'ONU (Convention de Vienne), tableau Wikipédia EN |

## Sens de circulation — Wikidata contre Wikipédia EN (« Left- and right-hand traffic »)

| id | désaccord | décision |
|---|---|---|
| ABW | Wikidata : droite ; EN : — | absent du tableau EN : Wikidata conservé |
| AIA | Wikidata : gauche ; EN : — | absent du tableau EN : Wikidata conservé |
| ALA | Wikidata : droite ; EN : — | absent du tableau EN : Wikidata conservé |
| ATF | Wikidata : droite ; EN : — | absent du tableau EN : Wikidata conservé |
| BES | Wikidata : droite ; EN : — | absent du tableau EN : Wikidata conservé |
| BLM | Wikidata : droite ; EN : — | absent du tableau EN : Wikidata conservé |
| CCK | Wikidata : gauche ; EN : — | absent du tableau EN : Wikidata conservé |
| COK | Wikidata : gauche ; EN : — | absent du tableau EN : Wikidata conservé |
| CUW | Wikidata : droite ; EN : — | absent du tableau EN : Wikidata conservé |
| CXR | Wikidata : gauche ; EN : — | absent du tableau EN : Wikidata conservé |
| FRO | Wikidata : droite ; EN : — | absent du tableau EN : Wikidata conservé |
| GLP | Wikidata : droite ; EN : — | absent du tableau EN : Wikidata conservé |
| GRL | Wikidata : droite ; EN : — | absent du tableau EN : Wikidata conservé |
| GUF | Wikidata : droite ; EN : — | absent du tableau EN : Wikidata conservé |
| MAF | Wikidata : droite ; EN : — | absent du tableau EN : Wikidata conservé |
| MSR | Wikidata : gauche ; EN : — | absent du tableau EN : Wikidata conservé |
| MTQ | Wikidata : droite ; EN : — | absent du tableau EN : Wikidata conservé |
| MYT | Wikidata : droite ; EN : — | absent du tableau EN : Wikidata conservé |
| NCL | Wikidata : droite ; EN : — | absent du tableau EN : Wikidata conservé |
| NFK | Wikidata : gauche ; EN : — | absent du tableau EN : Wikidata conservé |
| NIU | Wikidata : gauche ; EN : — | absent du tableau EN : Wikidata conservé |
| PYF | Wikidata : droite ; EN : — | absent du tableau EN : Wikidata conservé |
| REU | Wikidata : droite ; EN : — | absent du tableau EN : Wikidata conservé |
| SHN | Wikidata : gauche ; EN : — | absent du tableau EN : Wikidata conservé |
| SJM | Wikidata : droite ; EN : — | absent du tableau EN : Wikidata conservé |
| SPM | Wikidata : droite ; EN : — | absent du tableau EN : Wikidata conservé |
| SXM | Wikidata : droite ; EN : — | absent du tableau EN : Wikidata conservé |
| TKL | Wikidata : gauche ; EN : — | absent du tableau EN : Wikidata conservé |
| UMI | Wikidata : droite ; EN : — | absent du tableau EN : Wikidata conservé |
| VIR | Wikidata : gauche ; EN : — | absent du tableau EN : Wikidata conservé |
| WLF | Wikidata : droite ; EN : — | absent du tableau EN : Wikidata conservé |

## Monnaies — Wikidata contre mledoze/countries

| id | désaccord | décision |
|---|---|---|
| BHS | nous : ['BSD'] ; mledoze : ['BSD', 'USD'] | règle : monnaie officielle seulement (Wikidata) ; les monnaies qui circulent en parallèle ne sont pas retenues |
| BRN | nous : ['BND'] ; mledoze : ['BND', 'SGD'] | règle : monnaie officielle seulement (Wikidata) ; les monnaies qui circulent en parallèle ne sont pas retenues |
| BTN | nous : ['BTN'] ; mledoze : ['BTN', 'INR'] | règle : monnaie officielle seulement (Wikidata) ; les monnaies qui circulent en parallèle ne sont pas retenues |
| COK | nous : ['NZD'] ; mledoze : ['CKD', 'NZD'] | règle : monnaie officielle seulement (Wikidata) ; les monnaies qui circulent en parallèle ne sont pas retenues |
| CUB | nous : ['CUP'] ; mledoze : ['CUC', 'CUP'] | règle : monnaie officielle seulement (Wikidata) ; les monnaies qui circulent en parallèle ne sont pas retenues |
| CUW | nous : ['XCG'] ; mledoze : ['ANG'] | Wikidata conservé : florin caribéen (XCG) ; Wikipédia FR « Curaçao » : « sa monnaie est le florin caribéen » ; mledoze donne encore l'ancien florin des Antilles néerlandaises (ANG) |
| ESH | nous : — ; mledoze : ['DZD', 'MAD', 'MRU'] | pas de monnaie propre : plusieurs monnaies circulent selon les zones (dirham marocain, dinar algérien… d'après mledoze), on n'en retient aucune par neutralité |
| FRO | nous : ['DKK'] ; mledoze : ['DKK', 'FOK'] | Wikidata vide ; la couronne féroïenne de mledoze est une émission locale de la couronne danoise (DKK, commun aux deux) |
| FSM | nous : ['USD'] ; mledoze : — | Wikidata conservé (source principale) : monnaie absente de mledoze |
| GGY | nous : ['GBP'] ; mledoze : ['GBP', 'GGP'] | règle : monnaie officielle seulement (Wikidata) ; les monnaies qui circulent en parallèle ne sont pas retenues |
| IMN | nous : ['GBP'] ; mledoze : ['GBP', 'IMP'] | Wikidata vide ; la livre mannoise de mledoze est une émission locale de la livre sterling (GBP, commun aux deux) |
| IOT | nous : ['GBP', 'USD'] ; mledoze : ['USD'] | Wikidata conservé (source principale) : monnaie absente de mledoze |
| JEY | nous : ['GBP'] ; mledoze : ['GBP', 'JEP'] | règle : monnaie officielle seulement (Wikidata) ; les monnaies qui circulent en parallèle ne sont pas retenues |
| KHM | nous : ['KHR'] ; mledoze : ['KHR', 'USD'] | règle : monnaie officielle seulement (Wikidata) ; les monnaies qui circulent en parallèle ne sont pas retenues |
| KIR | nous : ['AUD'] ; mledoze : ['AUD', 'KID'] | règle : monnaie officielle seulement (Wikidata) ; les monnaies qui circulent en parallèle ne sont pas retenues |
| PSE | nous : ['ILS'] ; mledoze : ['EGP', 'ILS', 'JOD'] | règle : monnaie officielle seulement (Wikidata) ; les monnaies qui circulent en parallèle ne sont pas retenues |
| SGS | nous : ['GBP'] ; mledoze : ['SHP'] | Wikidata conservé ; Wikipédia FR : « le territoire adhère à la banque d'Angleterre et utilise la livre sterling » ; la livre de Sainte-Hélène de mledoze concerne un autre territoire |
| SWZ | nous : ['SZL'] ; mledoze : ['SZL', 'ZAR'] | règle : monnaie officielle seulement (Wikidata) ; les monnaies qui circulent en parallèle ne sont pas retenues |
| SXM | nous : ['XCG'] ; mledoze : ['ANG'] | Wikidata conservé : florin caribéen (XCG), qui remplace le florin des Antilles néerlandaises (Wikipédia FR « Saint-Martin (royaume des Pays-Bas) ») ; mledoze n'est pas à jour |
| TUV | nous : ['AUD'] ; mledoze : ['AUD', 'TVD'] | règle : monnaie officielle seulement (Wikidata) ; les monnaies qui circulent en parallèle ne sont pas retenues |
| ZWE | nous : ['USD', 'ZWG'] ; mledoze : ['BWP', 'CNY', 'EUR', 'GBP', 'INR', 'JPY', 'USD', 'ZAR', 'ZWB'] | Wikidata mêle les anciennes monnaies et le panier de devises de 2009 ; on garde l'or du Zimbabwe (ZWG, en cours sur Wikidata) et le dollar américain, commun aux deux sources |

## Langues officielles — Wikidata contre mledoze/countries

| id | désaccord | décision |
|---|---|---|
| AFG | nous : ['dari', 'pachto'] ; Wikidata : ['arabe', 'baloutche', 'dari', 'langues du Pamir', 'langues nouristanies', 'ouzbek', 'pachto', 'pashai', 'turkmène'] ; mledoze : ['Dari', 'Pashto', 'Turkmen'] | les deux langues officielles nationales (Wikidata et mledoze) ; les autres ne sont officielles que dans certaines régions |
| ARG | nous : ['espagnol'] ; Wikidata : ['espagnol'] ; mledoze : ['Guaraní', 'Spanish'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| ATG | nous : ['anglais'] ; Wikidata : ['anglais', 'espagnol'] ; mledoze : ['English'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| AZE | nous : ['azéri'] ; Wikidata : ['azéri'] ; mledoze : ['Azerbaijani', 'Russian'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| BDI | nous : ['kirundi', 'français', 'anglais'] ; Wikidata : ['anglais', 'français', 'kirundi'] ; mledoze : ['French', 'Kirundi'] | l'anglais est langue officielle depuis 2014 (Wikidata) ; mledoze n'est pas à jour |
| BFA | nous : ['moré', 'dioula', 'peul', 'bissa'] ; Wikidata : ['bissa', 'dioula', 'mooré'] ; mledoze : ['French'] | Wikipédia FR, article de l'entité : « les langues officielles sont : le moré, le dioula, le foulfouldé (peul) et le bissa » (constitution de 2023) |
| BLZ | nous : ['anglais'] ; Wikidata : ['anglais'] ; mledoze : ['Belizean Creole', 'English', 'Spanish'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| BRB | nous : ['anglais'] ; Wikidata : ['anglais', 'créole barbadien'] ; mledoze : ['English'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| BRN | nous : ['malais'] ; Wikidata : ['anglais britannique', 'malais'] ; mledoze : ['Malay'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| BVT | nous : — ; Wikidata : — ; mledoze : ['Norwegian'] | île inhabitée |
| BWA | nous : ['anglais'] ; Wikidata : ['anglais'] ; mledoze : ['English', 'Tswana'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| CHN | nous : ['mandarin standard'] ; Wikidata : ['putonghua'] ; mledoze : ['Chinese'] | libellé Wikidata « putonghua » = mandarin standard (mledoze : chinois) |
| COD | nous : ['français'] ; Wikidata : ['français'] ; mledoze : ['French', 'Kikongo', 'Lingala', 'Swahili', 'Tshiluba'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| COG | nous : ['français'] ; Wikidata : ['français'] ; mledoze : ['French', 'Kikongo', 'Lingala'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| CPV | nous : ['portugais'] ; Wikidata : ['créole cap-verdien', 'portugais'] ; mledoze : ['Portuguese'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| CZE | nous : ['tchèque'] ; Wikidata : ['tchèque'] ; mledoze : ['Czech', 'Slovak'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| DZA | nous : ['arabe'] ; Wikidata : ['arabe', 'berbère standard algérien'] ; mledoze : ['Arabic'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| ECU | nous : ['espagnol'] ; Wikidata : ['espagnol', 'quichua', 'shuar'] ; mledoze : ['Spanish'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| ESH | nous : ['arabe'] ; Wikidata : ['arabe'] ; mledoze : ['Berber', 'Hassaniya', 'Spanish'] | l'arabe est langue officielle pour les deux parties qui revendiquent le territoire (Wikidata) |
| FLK | nous : ['anglais'] ; Wikidata : ['anglais britannique'] ; mledoze : ['English'] | Wikidata : « anglais britannique », sans code ; mledoze : anglais |
| GGY | nous : ['anglais', 'français'] ; Wikidata : ['anglais'] ; mledoze : ['English', 'French', 'Guernésiais'] | anglais et français dans les deux sources |
| GIB | nous : ['anglais'] ; Wikidata : ['anglais britannique'] ; mledoze : ['English'] | Wikidata : « anglais britannique », sans code ; mledoze : anglais |
| GIN | nous : ['français'] ; Wikidata : ['français', 'langues en Guinée'] ; mledoze : ['French'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| GLP | nous : ['français'] ; Wikidata : — ; mledoze : ['French'] | Wikidata vide ; département français (mledoze : français) |
| GNB | nous : ['portugais'] ; Wikidata : ['portugais'] ; mledoze : ['Portuguese', 'Upper Guinea Creole'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| GRD | nous : ['anglais'] ; Wikidata : ['anglais', 'créole grenadais'] ; mledoze : ['English'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| GUF | nous : ['français'] ; Wikidata : ['créole guyanais', 'français'] ; mledoze : ['French'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| GUM | nous : ['anglais', 'chamorro'] ; Wikidata : ['anglais', 'chamorro'] ; mledoze : ['Chamorro', 'English', 'Spanish'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| HKG | nous : ['chinois', 'anglais'] ; Wikidata : ['mandarin standard'] ; mledoze : ['Chinese', 'English'] | langues officielles : chinois et anglais (mledoze) ; Wikidata ne donne que le mandarin standard |
| IND | nous : ['anglais', 'hindi'] ; Wikidata : ['anglais', 'hindi'] ; mledoze : ['English', 'Hindi', 'Tamil'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| IRQ | nous : ['arabe', 'kurde'] ; Wikidata : ['arabe', 'kurde'] ; mledoze : ['Arabic', 'Aramaic', 'Sorani'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| ISR | nous : ['hébreu'] ; Wikidata : ['hébreu'] ; mledoze : ['Arabic', 'Hebrew'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| JEY | nous : ['anglais', 'français'] ; Wikidata : ['anglais', 'français de Jersey', 'jersiais'] ; mledoze : ['English', 'French', 'Jèrriais'] | anglais et français de Jersey dans les deux sources |
| KGZ | nous : ['kirghize', 'russe'] ; Wikidata : ['kirghize'] ; mledoze : ['Kyrgyz', 'Russian'] | le russe est langue officielle au Kirghizistan (mledoze) ; Wikidata ne donne que le kirghize |
| LBN | nous : ['arabe'] ; Wikidata : ['arabe'] ; mledoze : ['Arabic', 'French'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| MAC | nous : ['chinois', 'portugais'] ; Wikidata : ['dialecte cantonais', 'mandarin standard', 'portugais'] ; mledoze : ['Chinese', 'Portuguese'] | langues officielles : chinois et portugais (mledoze) ; Wikidata détaille cantonais et mandarin |
| MEX | nous : ['espagnol'] ; Wikidata : ['espagnol', 'maya yucatèque', 'nahuatl'] ; mledoze : ['Spanish'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| MKD | nous : ['macédonien', 'albanais'] ; Wikidata : ['albanais', 'macédonien'] ; mledoze : ['Macedonian'] | l'albanais est co-officiel depuis 2019 (Wikidata) ; mledoze n'est pas à jour |
| MLI | nous : ['bambara', 'bobo', 'bozo', 'dogon', 'hassanya', 'khassonké', 'malinké', 'mamara', 'peul', 'sénoufo', 'songhaï', 'soninké', 'tamasheq'] ; Wikidata : ['bambara', 'bozo', 'dogon', 'hassanya', 'khassonké', 'langues bobo', 'langues sénoufo', 'malinké', 'mamara', 'peul', 'songhaï', 'soninké', 'tamasheq'] ; mledoze : ['French'] | Wikipédia FR, article de l'entité : constitution de 2023, « les langues nationales sont les langues officielles du Mali » ; liste des 13 langues nationales de Wikidata |
| MRT | nous : ['arabe'] ; Wikidata : ['arabe', 'français'] ; mledoze : ['Arabic'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| MTQ | nous : ['français'] ; Wikidata : — ; mledoze : ['French'] | Wikidata vide ; collectivité française (mledoze : français) |
| MUS | nous : ['anglais', 'français'] ; Wikidata : ['anglais', 'français'] ; mledoze : ['English', 'French', 'Mauritian Creole'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| MWI | nous : ['anglais', 'chewa'] ; Wikidata : ['anglais', 'chewa', 'tumbuka'] ; mledoze : ['Chewa', 'English'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| MYS | nous : ['malais'] ; Wikidata : ['malais'] ; mledoze : ['English', 'Malay'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| MYT | nous : ['français'] ; Wikidata : ['français', 'mahorais', 'shibushi'] ; mledoze : ['French'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| NAM | nous : ['anglais'] ; Wikidata : ['anglais'] ; mledoze : ['Afrikaans', 'English', 'German', 'Herero', 'Khoekhoe', 'Kwangali', 'Lozi', 'Ndonga', 'Tswana'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| NOR | nous : ['norvégien', 'same'] ; Wikidata : ['bokmål', 'langues sames', 'norvégien', 'nynorsk'] ; mledoze : ['Norwegian Bokmål', 'Norwegian Nynorsk', 'Sami'] | Wikidata et mledoze donnent le norvégien (bokmål, nynorsk) et les langues sames |
| NZL | nous : ['anglais', 'maori'] ; Wikidata : ['anglais', 'maori'] ; mledoze : ['English', 'Māori', 'New Zealand Sign Language'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| PCN | nous : ['anglais'] ; Wikidata : ['anglais', 'pitcairnais'] ; mledoze : ['English'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| PHL | nous : ['anglais', 'philippin'] ; Wikidata : ['anglais', 'philippin', 'taglish'] ; mledoze : ['English', 'Filipino'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| PLW | nous : ['anglais', 'paluan'] ; Wikidata : ['anglais', 'japonais', 'paluan'] ; mledoze : ['English', 'Palauan'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| PRK | nous : ['coréen'] ; Wikidata : ['coréen', 'langue standard de la Corée du Nord'] ; mledoze : ['Korean'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| RWA | nous : ['kinyarwanda', 'français', 'anglais', 'swahili'] ; Wikidata : ['anglais', 'français', 'kinyarwanda', 'swahili'] ; mledoze : ['English', 'French', 'Kinyarwanda'] | le swahili est langue officielle depuis 2017 (Wikidata) ; mledoze n'est pas à jour |
| SEN | nous : ['français'] ; Wikidata : ['badiaranké', 'balante', 'français', 'wolof'] ; mledoze : ['French'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| SLE | nous : ['anglais'] ; Wikidata : ['anglais', 'krio'] ; mledoze : ['English'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| SXM | nous : ['anglais', 'néerlandais'] ; Wikidata : ['anglais', 'néerlandais'] ; mledoze : ['Dutch', 'English', 'French'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| TJK | nous : ['tadjik'] ; Wikidata : ['tadjik'] ; mledoze : ['Russian', 'Tajik'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| TKL | nous : ['anglais', 'tokelau'] ; Wikidata : ['anglais', 'tokelau'] ; mledoze : ['English', 'Samoan', 'Tokelauan'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| TKM | nous : ['turkmène'] ; Wikidata : ['turkmène'] ; mledoze : ['Russian', 'Turkmen'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| TWN | nous : ['mandarin', 'taïwanais'] ; Wikidata : ['amis', 'atayal', 'bunun', 'hakka taïwanais', 'kanakanabu', 'kavalan', 'mandarin de Taïwan', 'paiwan', 'pouyouma', 'rukai', 'saaroa', 'saisiyat', 'sakizaya', 'seediq', 'taïwanais', 'tsou', 'yami'] ; mledoze : ['Chinese'] | Wikipédia FR, article de l'entité : le mandarin est langue officielle, le taïwanais l'est devenu en 2018 |
| URY | nous : ['espagnol'] ; Wikidata : — ; mledoze : ['Spanish'] | Wikidata vide ; mledoze : espagnol |
| USA | nous : ['anglais'] ; Wikidata : ['carolinien', 'chamorro', 'espagnol', 'hawaïen', 'samoan'] ; mledoze : ['English'] | Wikipédia FR, article de l'entité : « Les États-Unis adoptent l'anglais comme langue officielle le 1er mars 2025 » |
| UZB | nous : ['ouzbek'] ; Wikidata : ['ouzbek'] ; mledoze : ['Russian', 'Uzbek'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| WLF | nous : ['français'] ; Wikidata : ['français', 'futunien', 'wallisien'] ; mledoze : ['French'] | règle : langues présentes dans les deux sources (codes ISO 639-3) ; langues des signes non listées |
| ZWE | nous : ['anglais', 'barwe', 'chewa', 'chitonga', 'kalanga', 'khoïsan', 'nambya', 'ndau', 'shona', 'ndébélé du Nord', 'sotho du Sud', 'tsonga', 'tswana', 'venda', 'xhosa'] ; Wikidata : ['anglais', 'barwe', 'chewa', 'chitonga', 'kalanga', 'langues khoïsan', 'nambya', 'ndau', 'shona', 'sindebele', 'sotho du Sud', 'tsonga', 'tswana', 'venda', 'xhosa'] ; mledoze : ['Chewa', 'Chibarwe', 'English', 'Kalanga', 'Khoisan', 'Ndau', 'Northern Ndebele', 'Shona', 'Sotho', 'Tonga', 'Tsonga', 'Tswana', 'Venda', 'Xhosa', 'Zimbabwean Sign Language'] | langues officielles de la constitution (Wikidata, 16 avec la langue des signes, écartée par la règle générale) ; « sindebele » de Wikidata = ndébélé du Nord |

## Gentilé — Wikidata contre mledoze/countries (`demonyms.fra.m`)

| id | désaccord | décision |
|---|---|---|
| ABW | nous : — ; mledoze : Arubais | Wikidata vide → null (mledoze sert seulement au contrôle) |
| AIA | nous : — ; mledoze : Anguillan | Wikidata vide → null (mledoze sert seulement au contrôle) |
| ALA | nous : — ; mledoze : Ålandais | Wikidata vide → null (mledoze sert seulement au contrôle) |
| ASM | nous : — ; mledoze : Samoan | Wikidata vide → null (mledoze sert seulement au contrôle) |
| ATA | nous : — ; mledoze : Antarcticain | pas de population permanente ; « Antarcticain » (Wikidata) n'est pas d'usage établi en français |
| ATF | nous : — ; mledoze : Français | Wikidata vide → null (mledoze sert seulement au contrôle) |
| ATG | nous : Antiguayen ; mledoze : Antiguaise et barbudien | forme Wikidata conservée (source principale) |
| BES | nous : — ; mledoze : Néerlandais | Wikidata vide → null (mledoze sert seulement au contrôle) |
| BHS | nous : Bahaméen ; mledoze : Bahamien | forme Wikidata conservée (source principale) |
| COK | nous : — ; mledoze : Cookien | Wikidata vide → null (mledoze sert seulement au contrôle) |
| CRI | nous : Costaricien ; mledoze : Costaricain | forme Wikidata conservée (source principale) |
| CUW | nous : — ; mledoze : Curacien | Wikidata vide → null (mledoze sert seulement au contrôle) |
| CYM | nous : — ; mledoze : Caïmanien | Wikidata vide → null (mledoze sert seulement au contrôle) |
| FLK | nous : — ; mledoze : Malouin | Wikidata vide → null (mledoze sert seulement au contrôle) |
| GGY | nous : — ; mledoze : Guernesiais | Wikidata vide → null (mledoze sert seulement au contrôle) |
| GLP | nous : — ; mledoze : Guadeloupéen | Wikidata vide → null (mledoze sert seulement au contrôle) |
| GUM | nous : Guamanien ; mledoze : — | mledoze muet : Wikidata conservé |
| KGZ | nous : Kirghiz ; mledoze : Kirghize | mledoze donne le féminin ; masculin de Wikidata conservé |
| KIR | nous : Gilbertin ; mledoze : Kiribatien | forme Wikidata conservée (source principale) |
| KNA | nous : Christophien ; mledoze : Kittitien-et-nevicien | forme Wikidata conservée (source principale) |
| MAC | nous : — ; mledoze : Macanais | Wikidata vide → null (mledoze sert seulement au contrôle) |
| MNP | nous : — ; mledoze : Américan | Wikidata vide → null (mledoze sert seulement au contrôle) |
| MSR | nous : — ; mledoze : Montserratien | Wikidata vide → null (mledoze sert seulement au contrôle) |
| MTQ | nous : — ; mledoze : Martiniquais | Wikidata vide → null (mledoze sert seulement au contrôle) |
| MWI | nous : Malawite ; mledoze : Malawien | forme Wikidata conservée (source principale) |
| NFK | nous : — ; mledoze : Norfolkais | Wikidata vide → null (mledoze sert seulement au contrôle) |
| NIU | nous : — ; mledoze : Niuéen | Wikidata vide → null (mledoze sert seulement au contrôle) |
| PCN | nous : — ; mledoze : Pitcairnais | Wikidata vide → null (mledoze sert seulement au contrôle) |
| PLW | nous : Palaois ; mledoze : Paluan | forme Wikidata conservée (source principale) |
| SHN | nous : — ; mledoze : Sainte-Hélènois | Wikidata vide → null (mledoze sert seulement au contrôle) |
| SPM | nous : Saint-Pierrais ou Miquelonais ; mledoze : Saint-Pierrais, Miquelonais | Wikidata et mledoze : les habitants de chacune des deux îles |
| SUR | nous : Surinamien ; mledoze : Surinamais | forme Wikidata conservée (source principale) |
| SWZ | nous : Eswatinien ; mledoze : Swazie | forme Wikidata conservée (source principale) |
| SXM | nous : — ; mledoze : Saint-Martinois | Wikidata vide → null (mledoze sert seulement au contrôle) |
| TJK | nous : Tadjik ; mledoze : Tadjike | mledoze donne le féminin ; masculin de Wikidata conservé |
| TON | nous : Tongien ; mledoze : Tonguien | forme Wikidata conservée (source principale) |
| TUV | nous : Tuvalais ; mledoze : Tuvaluan | forme Wikidata conservée (source principale) |
| UZB | nous : Ouzbek ; mledoze : Ouzbèke | mledoze donne le féminin ; masculin de Wikidata conservé |
| VAT | nous : — ; mledoze : Vatican | Wikidata vide → null (mledoze sert seulement au contrôle) |
| VUT | nous : Vanouatais ; mledoze : Vanuatuan | forme Wikidata conservée (source principale) |

## Indicatif téléphonique — Wikidata contre mledoze/countries (`idd`)

| id | désaccord | décision |
|---|---|---|
| ALA | nous : — ; mledoze : +35818 | Wikidata vide → null (mledoze sert seulement au contrôle) |
| ATA | nous : +672 ; mledoze : — | Wikidata conservé (source principale) |
| ATF | nous : — ; mledoze : +262 | Wikidata vide → null (mledoze sert seulement au contrôle) |
| BVT | nous : — ; mledoze : +47 | Wikidata vide → null (mledoze sert seulement au contrôle) |
| CXR | nous : — ; mledoze : +61 | Wikidata vide → null (mledoze sert seulement au contrôle) |
| ESH | nous : — ; mledoze : +2 | Wikidata donne +212, l'indicatif du Maroc : non retenu par neutralité |
| HMD | nous : — ; mledoze : — | Wikidata vide → null (mledoze sert seulement au contrôle) |
| SJM | nous : — ; mledoze : +4779 | Wikidata vide → null (mledoze sert seulement au contrôle) |
| UMI | nous : — ; mledoze : +268 | Wikidata vide → null (mledoze sert seulement au contrôle) |

## Domaine internet — Wikidata contre mledoze/countries (`tld`)

| id | désaccord | décision |
|---|---|---|
| ARE | nous : .ae ; mledoze : .ae, امارات. | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| BES | nous : .bq ; mledoze : .bq, .nl | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| CHN | nous : .cn ; mledoze : .cn, .中国, .中國, .公司, .网络 | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| DZA | nous : .dz ; mledoze : .dz, الجزائر. | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| EGY | nous : .eg ; mledoze : .eg, .مصر | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| ESH | nous : — ; mledoze : .eh | Wikidata vide → null (mledoze sert seulement au contrôle) |
| HKG | nous : .hk ; mledoze : .hk, .香港 | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| HMD | nous : .hm ; mledoze : .hm, .aq | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| IRN | nous : .ir ; mledoze : .ir, ایران. | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| JOR | nous : .jo ; mledoze : .jo, الاردن. | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| JPN | nous : .jp ; mledoze : .jp, .みんな | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| KAZ | nous : .kz ; mledoze : .kz, .қаз | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| KOR | nous : .kr ; mledoze : .kr, .한국 | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| LKA | nous : .lk ; mledoze : .lk, .இலங்கை, .ලංකා | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| MAF | nous : .mf ; mledoze : .fr, .gp | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| MAR | nous : .ma ; mledoze : .ma, المغرب. | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| PSE | nous : .ps ; mledoze : .ps, فلسطين. | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| QAT | nous : .qa ; mledoze : .qa, قطر. | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| RUS | nous : .ru ; mledoze : .ru, .su, .рф | .su, domaine de l'ex-URSS encore actif, n'est pas le domaine national (Wikidata et mledoze donnent .ru en premier) |
| SAU | nous : .sa ; mledoze : .sa, .السعودية | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| SGP | nous : .sg ; mledoze : .sg, .新加坡, .சிங்கப்பூர் | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| SHN | nous : — ; mledoze : .sh, .ac | Wikidata vide → null (mledoze sert seulement au contrôle) |
| SRB | nous : .rs ; mledoze : .rs, .срб | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| SYR | nous : .sy ; mledoze : .sy, سوريا. | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| THA | nous : .th ; mledoze : .th, .ไทย | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| TWN | nous : .tw ; mledoze : .tw, .台灣, .台湾 | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| UKR | nous : .ua ; mledoze : .ua, .укр | règle : domaine national en lettres latines (2 lettres) ; domaines internationalisés, gTLD et domaine de l'État souverain écartés |
| UMI | nous : — ; mledoze : .us | Wikidata vide → null (mledoze sert seulement au contrôle) |
| XKX | nous : — ; mledoze : .xk | Wikidata vide → null (mledoze sert seulement au contrôle) |

## Capitales — contre mledoze/countries (`capital`, libellés anglais Wikidata)

| id | désaccord | décision |
|---|---|---|
| ATG | mledoze : « Saint John's » ; nous : « Saint John's » | même ville (Saint John's), graphie anglaise différente |
| BES | mledoze : « Kralendijk, Oranjestad, The Bottom » ; nous : « Kralendijk » | BES regroupe trois îles, chacune a son chef-lieu ; on retient Kralendijk (Bonaire, la plus peuplée) avec le rôle « chef-lieu de Bonaire » |
| GGY | mledoze : « St. Peter Port » ; nous : « Saint-Pierre-Port » | même ville (St Peter Port = Saint-Pierre-Port) |
| GNQ | mledoze : « Malabo » ; nous : « Ciudad de la Paz » | mledoze n'est pas à jour : capitale transférée à Ciudad de la Paz en janvier 2026 (Wikidata P36 du 2026-01-03, Wikipédia FR « Ciudad de la Paz ») |
| HKG | mledoze : « City of Victoria » ; nous : « — » | Victoria n'est plus une entité administrative ; pas de capitale distincte (capital_note_fr) |
| MNG | mledoze : « Ulan Bator » ; nous : « Oulan-Bator » | même ville (Ulan Bator = Oulan-Bator) |
| TKL | mledoze : « Fakaofo » ; nous : « — » | pas de capitale officielle, l'administration tourne entre les atolls (capital_note_fr) ; Fakaofo n'est qu'un des trois |

## Continent — contre mledoze/countries (`region`/`subregion`)

| id | désaccord | décision |
|---|---|---|
| ATF | mledoze : Antarctic /  ; nous : afrique (Afrique de l'Est) | on suit les régions ONU (M49), source du champ continent pour toutes les entités ; mledoze range les îles subantarctiques à part (« Antarctic ») |
| BVT | mledoze : Antarctic /  ; nous : amerique-sud (Amérique du Sud) | on suit les régions ONU (M49), source du champ continent pour toutes les entités ; mledoze range les îles subantarctiques à part (« Antarctic ») |
| HMD | mledoze : Antarctic /  ; nous : oceanie (Australie et Nouvelle-Zélande) | on suit les régions ONU (M49), source du champ continent pour toutes les entités ; mledoze range les îles subantarctiques à part (« Antarctic ») |
| SGS | mledoze : Antarctic /  ; nous : amerique-sud (Amérique du Sud) | on suit les régions ONU (M49), source du champ continent pour toutes les entités ; mledoze range les îles subantarctiques à part (« Antarctic ») |
| UMI | mledoze : Americas / North America ; nous : oceanie (Micronésie) | M49 range les îles mineures en Océanie (Micronésie) : la plupart sont dans le Pacifique |

## Voisins — Wikidata P47 et mledoze contre la géométrie Natural Earth

| id | désaccord | décision |
|---|---|---|
| AFG | Wikidata P47 ajoute IND | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| AGO | Wikidata P47 ajoute GAB | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| ALB | Wikidata P47 ajoute SRB | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| ARE | Wikidata P47 ajoute IRN | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| ARG | Wikidata P47 ajoute GBR | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| ATG | Wikidata P47 ajoute GBR | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| AUS | Wikidata P47 ajoute IDN, NCL, NZL, PNG, SLB, TLS, VUT | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| BEL | Wikidata P47 ajoute GBR | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| BHR | Wikidata P47 ajoute IRN, SAU | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| BHS | Wikidata P47 ajoute GBR, TCA, USA | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| BRA | Wikidata P47 ajoute FRA | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| CAN | Wikidata P47 ajoute GRL, SPM | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| CHN | Wikidata P47 ajoute JPN, KOR, TWN ; Wikidata P47 n'a pas HKG, MAC | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| COD | Wikidata P47 ajoute CMR, SDN | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| COL | Wikidata P47 ajoute NIC | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| COM | Wikidata P47 ajoute FRA, MDG, MOZ, SYC, TZA | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| CUB | Wikidata P47 ajoute GBR, USA | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| CYP | Wikidata P47 ajoute GBR, ISR, TUR | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| DEU | Wikidata P47 ajoute GBR, SWE | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| DMA | Wikidata P47 ajoute VEN | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| DNK | Wikidata P47 ajoute NOR, SWE | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| DOM | Wikidata P47 ajoute TCA, USA, VEN | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| DZA | Wikidata P47 ajoute ESP, ITA | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| ESP | Wikidata P47 ajoute DZA, GBR | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| EST | Wikidata P47 ajoute SWE | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| FJI | Wikidata P47 ajoute SLB | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| FRA | Wikidata P47 ajoute BRA, GBR, MUS, SLB, SUR, VEN | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| FRO | Wikidata P47 ajoute ISL | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| FSM | Wikidata P47 ajoute PLW, PNG, USA | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| GAB | Wikidata P47 ajoute AGO, STP | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| GBR | Wikidata P47 ajoute BEL, DEU, DNK, FRA, NOR | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| GNQ | Wikidata P47 ajoute STP | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| GRD | Wikidata P47 ajoute VEN | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| GRL | Wikidata P47 ajoute CAN, ISL, NOR | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| GUM | Wikidata P47 ajoute FSM, MNP | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| HKG | Wikidata P47 n'a pas CHN | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| HTI | Wikidata P47 ajoute TCA, USA | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| IDN | Wikidata P47 ajoute AUS, IND, PHL, PLW, SGP, THA, VNM | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| IND | Wikidata P47 ajoute AFG, IDN, LKA | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| IRN | Wikidata P47 ajoute ARE, BHR, KWT, OMN, QAT, SAU | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| ISL | Wikidata P47 ajoute FRO, GRL | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| ISR | Wikidata P47 ajoute CYP | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| ITA | Wikidata P47 ajoute DZA, MLT | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| JAM | Wikidata P47 ajoute GBR | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| JPN | Wikidata P47 ajoute CHN, KOR, PHL, RUS, TWN, USA | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| KEN | Wikidata P47 ajoute SDN | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| KIR | Wikidata P47 ajoute FRA, USA | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| KNA | Wikidata P47 ajoute GBR, VEN | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| KOR | Wikidata P47 ajoute CHN, JPN | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| KWT | Wikidata P47 ajoute IRN | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| LCA | Wikidata P47 ajoute VEN | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| LKA | Wikidata P47 ajoute IND | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| LKA | mledoze ajoute IND | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| LTU | Wikidata P47 ajoute SWE | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| LVA | Wikidata P47 ajoute SWE | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| MAC | Wikidata P47 n'a pas CHN | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| MDG | Wikidata P47 ajoute COM, FRA, MOZ, SYC | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| MDV | Wikidata P47 ajoute GBR | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| MHL | Wikidata P47 ajoute FSM, KIR, NRU, USA | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| MLT | Wikidata P47 ajoute ITA | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| MOZ | Wikidata P47 ajoute COM | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| MRT | Wikidata P47 ajoute ESP | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| MUS | Wikidata P47 ajoute FRA, MDV, SYC | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| MYS | Wikidata P47 ajoute PHL, SGP | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| MYT | Wikidata P47 ajoute COM, MDG | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| NAM | Wikidata P47 n'a pas ZWE | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| NAM | mledoze n'a pas ZWE | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| NCL | Wikidata P47 ajoute AUS | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| NGA | Wikidata P47 ajoute STP | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| NIC | Wikidata P47 ajoute COL | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| NOR | Wikidata P47 ajoute DNK, GBR, GRL | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| NZL | Wikidata P47 ajoute AUS | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| OMN | Wikidata P47 ajoute IRN | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| PAN | Wikidata P47 ajoute USA | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| PHL | Wikidata P47 ajoute CHN, IDN, JPN, MYS, PLW, TWN | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| PLW | Wikidata P47 ajoute FSM, IDN, PHL | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| PNG | Wikidata P47 ajoute AUS, FSM, SLB | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| POL | Wikidata P47 ajoute SWE | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| QAT | Wikidata P47 ajoute IRN | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| RUS | Wikidata P47 ajoute JPN, SWE, USA | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| SAU | Wikidata P47 ajoute BHR, EGY, IRN | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| SGP | Wikidata P47 ajoute IDN, MYS | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| SLB | Wikidata P47 ajoute AUS, FJI, FRA, PNG, VUT | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| SPM | Wikidata P47 ajoute CAN | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| SRB | Wikidata P47 ajoute ALB | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| STP | Wikidata P47 ajoute GAB, GNQ, NGA | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| SUR | Wikidata P47 ajoute FRA | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| SWE | Wikidata P47 ajoute DEU, DNK, EST, LTU, LVA, POL, RUS | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| SXM | Wikidata P47 ajoute FRA | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| SYC | Wikidata P47 ajoute COM, FRA, MDG, MUS, TZA | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| TCA | Wikidata P47 ajoute BHS, DOM, HTI | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| TLS | Wikidata P47 ajoute AUS | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| TON | Wikidata P47 ajoute USA | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| TTO | Wikidata P47 ajoute VEN | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| TUR | Wikidata P47 ajoute CYP, UKR | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| TWN | Wikidata P47 ajoute CHN, JPN, PHL | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| TZA | Wikidata P47 ajoute SYC | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| UGA | Wikidata P47 ajoute SDN | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| UKR | Wikidata P47 ajoute TUR | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| USA | Wikidata P47 ajoute BHS, CUB, DOM, FSM, HTI, JPN, KIR, RUS, TON, VEN, WSM | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| VCT | Wikidata P47 ajoute VEN | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| VEN | Wikidata P47 ajoute DMA, DOM, FRA, GBR, GRD, KNA, LCA, TTO, USA, VCT | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| VGB | Wikidata P47 ajoute VIR | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| VIR | Wikidata P47 ajoute PRI, VGB | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| VUT | Wikidata P47 ajoute AUS, SLB | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| WSM | Wikidata P47 ajoute USA | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| ZWE | Wikidata P47 n'a pas NAM | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |
| ZWE | mledoze n'a pas NAM | règle : voisins = frontière terrestre selon la géométrie Natural Earth 10m (polygones à < 500 m) ; les voisins maritimes ou via un autre code ISO (ex. Brésil pour la France → GUF) ne comptent pas |

## Superficie — contre mledoze/countries (écart > 10%)

| id | désaccord | décision |
|---|---|---|
| BLM | Wikidata 24 km² ; mledoze 21 km² (écart 14%) | Wikidata conservé (24 km² avec les îlets) ; Wikipédia FR « Saint-Barthélemy » : « environ 21 km2 (24 km2 avec ses îlets) » |
| GIB | Wikidata 6.84 km² ; mledoze 6 km² (écart 14%) | Wikidata conservé ; Wikipédia FR « Gibraltar » : « une superficie de 6,8 km2 » (mledoze arrondit) |
| HMD | Wikidata 368 km² ; mledoze 412 km² (écart 11%) | Wikidata conservé (368 km²) ; la géométrie Natural Earth donne 395 km², entre les deux sources |
| MAC | nous (corrigé) 33.3 km² ; mledoze 30 km² (écart 11%) | Wikipédia FR « Macao » : « Aujourd'hui, Macao a une superficie de 33,3 km2 » (Wikidata 115 km² inclut les eaux) |
| NLD | Wikidata 37 378 km² ; mledoze 41 850 km² (écart 11%) | Wikidata conservé : terres seules (37 378 km²) ; mledoze compte les eaux intérieures |
| NOR | Wikidata 385 207 km² ; mledoze 323 802 km² (écart 19%) | Wikidata conservé, chiffre officiel qui inclut Svalbard et Jan Mayen ; Wikipédia FR « Norvège » : « Avec 385 155 km2 (Jan Mayen et Svalbard inclus) » |
| TCA | nous (corrigé) 616 km² ; mledoze 948 km² (écart 35%) | Wikipédia FR « Îles Turques-et-Caïques » : « superficie totale terrestre de 616,3 km2 (à marée haute) » |
| TKL | Wikidata 10 km² ; mledoze 12 km² (écart 17%) | Wikidata conservé (10 km²) ; écart d'arrondi sur des atolls (mledoze 12 km²) |
| YEM | Wikidata 455 503 km² ; mledoze 527 968 km² (écart 14%) | Wikidata conservé ; Wikipédia FR « Yémen » : « le Yémen couvre une surface de 455 503 km2 » |

## Blocages

- Wikimedia limite à 10 requêtes/min un client dont l'User-Agent n'a pas de contact (API et upload.wikimedia.org). Pré-remplissage en masse du cache Wikipédia abandonné (décision du coordinateur, 12 oct.) ; contact dans l'UA en attente de l'accord de Josca (variable GEOATLAS_UA_CONTACT ou cache/ua_contact.txt).
