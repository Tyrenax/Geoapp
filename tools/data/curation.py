"""Décisions éditoriales appliquées par build_countries.py par-dessus Wikidata.

Chaque entrée est une décision : la justification et la source qui tranche sont reprises dans
data/DATA_REPORT.md par check_data.py.
"""

# États hors des 193 membres de l'ONU tels que Wikidata les rattache (le membre ONU est le « royaume »
# pour le Danemark et les Pays-Bas), plus les 4 États du périmètre hors ONU.
EXTRA_ETATS = {"DNK", "NLD", "VAT", "PSE", "XKX", "TWN"}

# Territoires : (id de l'État dont il dépend ou None, statut en français).
TERRITORIES = {
    "ABW": ("NLD", "pays constitutif du royaume des Pays-Bas"),
    "AIA": ("GBR", "territoire britannique d'outre-mer"),
    "ALA": ("FIN", "région autonome de la Finlande"),
    "ASM": ("USA", "territoire non incorporé des États-Unis"),
    "ATA": (None, "continent régi par le traité sur l'Antarctique"),
    "ATF": ("FRA", "territoire d'outre-mer français"),
    "BES": ("NLD", "communes à statut particulier des Pays-Bas"),
    "BLM": ("FRA", "collectivité d'outre-mer française"),
    "BMU": ("GBR", "territoire britannique d'outre-mer"),
    "BVT": ("NOR", "dépendance inhabitée de la Norvège"),
    "CCK": ("AUS", "territoire extérieur de l'Australie"),
    "COK": ("NZL", "État librement associé à la Nouvelle-Zélande"),
    "CUW": ("NLD", "pays constitutif du royaume des Pays-Bas"),
    "CXR": ("AUS", "territoire extérieur de l'Australie"),
    "CYM": ("GBR", "territoire britannique d'outre-mer"),
    "ESH": (None, "territoire non autonome au statut disputé, revendiqué par le Maroc et par la République arabe sahraouie démocratique"),
    "FLK": ("GBR", "territoire britannique d'outre-mer, revendiqué par l'Argentine"),
    "FRO": ("DNK", "territoire autonome du Danemark"),
    "GGY": ("GBR", "dépendance de la Couronne britannique"),
    "GIB": ("GBR", "territoire britannique d'outre-mer, revendiqué par l'Espagne"),
    "GLP": ("FRA", "département et région d'outre-mer français"),
    "GRL": ("DNK", "territoire autonome du Danemark"),
    "GUF": ("FRA", "collectivité territoriale unique d'outre-mer française"),
    "GUM": ("USA", "territoire non incorporé des États-Unis"),
    "HKG": ("CHN", "région administrative spéciale de la Chine"),
    "HMD": ("AUS", "territoire extérieur inhabité de l'Australie"),
    "IMN": ("GBR", "dépendance de la Couronne britannique"),
    "IOT": ("GBR", "territoire britannique d'outre-mer, revendiqué par Maurice"),
    "JEY": ("GBR", "dépendance de la Couronne britannique"),
    "MAC": ("CHN", "région administrative spéciale de la Chine"),
    "MAF": ("FRA", "collectivité d'outre-mer française"),
    "MNP": ("USA", "commonwealth associé aux États-Unis"),
    "MSR": ("GBR", "territoire britannique d'outre-mer"),
    "MTQ": ("FRA", "collectivité territoriale unique d'outre-mer française"),
    "MYT": ("FRA", "département et région d'outre-mer français"),
    "NCL": ("FRA", "collectivité française à statut particulier"),
    "NFK": ("AUS", "territoire extérieur de l'Australie"),
    "NIU": ("NZL", "État librement associé à la Nouvelle-Zélande"),
    "PCN": ("GBR", "territoire britannique d'outre-mer"),
    "PRI": ("USA", "territoire non incorporé des États-Unis (commonwealth)"),
    "PYF": ("FRA", "collectivité d'outre-mer française"),
    "REU": ("FRA", "département et région d'outre-mer français"),
    "SGS": ("GBR", "territoire britannique d'outre-mer, revendiqué par l'Argentine"),
    "SHN": ("GBR", "territoire britannique d'outre-mer"),
    "SJM": ("NOR", "territoires norvégiens à statut particulier"),
    "SPM": ("FRA", "collectivité d'outre-mer française"),
    "SXM": ("NLD", "pays constitutif du royaume des Pays-Bas"),
    "TCA": ("GBR", "territoire britannique d'outre-mer"),
    "TKL": ("NZL", "territoire dépendant de la Nouvelle-Zélande"),
    "UMI": ("USA", "îles inhabitées ou presque, sous administration des États-Unis"),
    "VGB": ("GBR", "territoire britannique d'outre-mer"),
    "VIR": ("USA", "territoire non incorporé des États-Unis"),
    "WLF": ("FRA", "collectivité d'outre-mer française"),
}

NOT_QUIZZABLE = {"ATA"}

# Nom usuel quand le libellé Wikidata ne convient pas (les minuscules initiales sont corrigées à part).
NAME_FR = {
    "CHN": "Chine",
    "PSE": "Palestine",
    "SXM": "Sint Maarten",          # « Saint-Martin » est déjà MAF (partie française)
}

# Article défini quand l'heuristique sur la 1re phrase de l'article Wikipédia ne suffit pas.
ARTICLE_FR = {
    "REU": "",       # le nom contient déjà l'article : « La Réunion »
    "BES": "les",    # 1re phrase « Bonaire, Saint-Eustache et Saba » ; nom usuel « les Pays-Bas caribéens »
    "COD": "la",     # 1re phrase « Le Congo… » ; nom usuel « la République démocratique du Congo »
    "GGY": "",       # 1re phrase « Le bailliage de Guernesey » ; on dit « Guernesey »
    "SXM": "",       # 1re phrase « Saint-Martin, … » ; nom retenu « Sint Maarten »
}

# Nom officiel quand la 1re phrase Wikipédia (« en forme longue … ») ou Wikidata ne donne pas un nom propre.
# None = pas de nom officiel distinct à afficher.
OFFICIAL_FR = {
    "AFG": None,     # Wikipédia : « de facto l'émirat islamique… » ; régime non reconnu, on n'affiche rien
    "FSM": None,     # le nom usuel est déjà le nom officiel
    "PRY": "République du Paraguay",            # la phrase continue par « depuis 1813 »
    "GEO": None,     # Wikidata : « Géorgie (la) »
    "REU": None,
    "BLM": None,
    "DZA": "République algérienne démocratique et populaire",  # la 1re variante Wikipédia omet « et »
}

# Variantes acceptées en saisie libre (en plus du nom usuel et du nom officiel).
ALIASES_FR = {
    "ARE": ["EAU", "Émirats"],
    "BES": ["Bonaire, Saint-Eustache et Saba", "Îles BES"],
    "BIH": ["Bosnie", "Bosnie-et-Herzégovine"],
    "BLM": ["Saint-Barth"],
    "BLR": ["Bélarus"],
    "CAF": ["Centrafrique", "RCA"],
    "CCK": ["Îles Keeling", "Îles Cocos (Keeling)"],
    "CHN": ["République populaire de Chine", "RPC"],
    "CIV": ["Côte-d'Ivoire"],
    "COD": ["RDC", "RD Congo", "Congo-Kinshasa"],
    "COG": ["Congo", "Congo-Brazzaville"],
    "CPV": ["Cabo Verde"],
    "CZE": ["République tchèque"],
    "FLK": ["Îles Falkland", "Malouines"],
    "FSM": ["Micronésie"],
    "GBR": ["Grande-Bretagne", "UK"],
    "GNB": ["Guinée-Bissao"],
    "IRQ": ["Iraq"],
    "KNA": ["Saint-Kitts-et-Nevis"],
    "KOR": ["République de Corée"],
    "LKA": ["Ceylan"],
    "MDA": ["Moldova"],
    "MKD": ["Macédoine"],
    "MMR": ["Myanmar"],
    "MUS": ["Île Maurice"],
    "NLD": ["Hollande"],
    "PRK": ["RPDC"],
    "PSE": ["État de Palestine"],
    "SLV": ["El Salvador"],
    "SSD": ["Sud-Soudan"],
    "STP": ["São Tomé-et-Príncipe"],
    "SWZ": ["Swaziland"],
    "TCA": ["Îles Turks-et-Caïcos"],
    "TLS": ["Timor-Leste", "Timor-Oriental"],
    "TTO": ["Trinidad-et-Tobago"],
    "TWN": ["République de Chine", "Formose"],
    "USA": ["USA", "États-Unis d'Amérique"],
    "VAT": ["Saint-Siège", "Cité du Vatican"],
    "VGB": ["BVI"],
    "VIR": ["Îles Vierges américaines"],
    "VNM": ["Viêt Nam"],
    "XKX": ["Kossovo"],
}

# Capitales réglées à la main : [(nom, rôle)], la première est la réponse principale (quiz_capital).
# Les noms sont cherchés parmi les P36 Wikidata, sinon dans EXTRA_CAPITALS (titre Wikipédia FR).
CAPITALS = {
    "BEN": [("Porto-Novo", "capitale officielle"), ("Cotonou", "siège du gouvernement")],
    "BES": [("Kralendijk", "chef-lieu de Bonaire")],
    "BOL": [("Sucre", "capitale constitutionnelle"), ("La Paz", "siège du gouvernement")],
    "CHE": [("Berne", "ville fédérale, siège des autorités fédérales")],
    "CIV": [("Yamoussoukro", "capitale politique et administrative"), ("Abidjan", "capitale économique")],
    "ESH": [("Laâyoune", "ville principale du territoire (statut disputé)")],
    "GNQ": [("Ciudad de la Paz", "capitale depuis janvier 2026, à la place de Malabo")],
    "IDN": [("Jakarta", "capitale (transfert vers Nusantara prévu, décret présidentiel non signé)")],
    "ISR": [("Jérusalem", "capitale proclamée par Israël, statut contesté sur le plan international")],
    "LKA": [("Sri Jayawardenapura", "capitale officielle"), ("Colombo", "capitale commerciale")],
    "MSR": [("Brades", "capitale de fait"), ("Plymouth", "capitale officielle, abandonnée depuis l'éruption de 1997")],
    "MYS": [("Kuala Lumpur", "capitale"), ("Putrajaya", "siège du gouvernement")],
    "NLD": [("Amsterdam", "capitale"), ("La Haye", "siège du gouvernement")],
    "NRU": [("Yaren", "siège du gouvernement (pas de capitale officielle)")],
    "PSE": [("Jérusalem-Est", "capitale proclamée par l'État de Palestine"),
            ("Ramallah", "siège de fait de l'Autorité palestinienne")],
    "SGS": [("King Edward Point", "siège administratif"), ("Grytviken", "ancienne station baleinière voisine")],
    "SJM": [("Longyearbyen", "centre administratif du Svalbard")],
    "SWZ": [("Mbabane", "capitale administrative"), ("Lobamba", "capitale royale et législative")],
    "YEM": [("Sanaa", "capitale constitutionnelle, contrôlée par les Houthis"),
            ("Aden", "capitale provisoire du gouvernement reconnu")],
    "ZAF": [("Pretoria", "capitale administrative"), ("Le Cap", "capitale législative"),
            ("Bloemfontein", "capitale judiciaire")],
}

# Capitales absentes des P36 Wikidata : titre de l'article Wikipédia FR (QID et coordonnées lus via l'API).
EXTRA_CAPITALS = {
    "Abidjan": "Abidjan",
    "Kralendijk": "Kralendijk",
    "Laâyoune": "Laâyoune",
    "La Haye": "La Haye",
    "Longyearbyen": "Longyearbyen",
}

# Capitales sans lien Wikipédia FR sur Wikidata : titre de l'article FR.
CAPITAL_WIKI_FR = {"Managua": "Managua", "Saïpan": "Saïpan"}

# Note affichée à côté de la capitale (statut disputé), en plus des rôles.
CAPITAL_NOTE = {
    "ISR": "Israël a proclamé Jérusalem sa capitale ; ce statut n'est pas reconnu par une grande partie de la "
           "communauté internationale, et la plupart des pays ont leur ambassade à Tel-Aviv.",
    "PSE": "L'État de Palestine a proclamé Jérusalem-Est sa capitale ; ses institutions siègent à Ramallah. "
           "Les deux réponses sont acceptées.",
}

# Entités sans capitale : raison affichable.
NO_CAPITAL = {
    "ATA": "pas de capitale : continent sans État",
    "BVT": "île inhabitée, pas de capitale",
    "HKG": "région administrative spéciale, pas de capitale distincte",
    "HMD": "îles inhabitées, pas de capitale",
    "MAC": "région administrative spéciale, pas de capitale distincte",
    "TKL": "pas de capitale : le siège de l'administration tourne entre les trois atolls",
    "UMI": "îles dispersées, pas de capitale",
}

# Variantes acceptées pour les noms de capitales.
CAPITAL_ALIASES = {
    "Sri Jayawardenapura": ["Sri Jayawardenapura Kotte", "Kotte"],
    "Jérusalem-Est": ["Jérusalem"],
    "Laâyoune": ["El Aaiún", "Layoune"],
    "Naypyidaw": ["Naypyitaw", "Nay Pyi Taw"],
    "Pékin": ["Beijing"],
    "Kiev": ["Kyiv", "Kyïv"],
    "Astana": ["Nour-Soultan"],
    "Abou Dabi": ["Abu Dhabi", "Abou Dhabi"],
    "Dacca": ["Dhaka"],
    "Bogota": ["Bogotá"],
    "Asuncion": ["Asunción"],
    "Chișinău": ["Chisinau", "Kichinev"],
    "Tarawa-Sud": ["Tarawa", "South Tarawa"],
    "Hagåtña": ["Agana"],
    "Port Stanley": ["Stanley"],
    "Mata Utu": ["Mata-Utu"],
    "Nukuʻalofa": ["Nuku'alofa", "Nukualofa"],
    "Tórshavn": ["Torshavn"],
    "Saint-Pierre-Port": ["St Peter Port"],
    "Saint-Hélier": ["St Helier"],
    "Oulan-Bator": ["Oulan Bator", "Ulaanbaatar"],
    "Thimphou": ["Thimphu"],
    "Achgabat": ["Achkhabad"],
    "Douchanbé": ["Douchanbe", "Dushanbe"],
    "Bichkek": ["Bishkek"],
    "Tachkent": ["Tashkent"],
    "Mascate": ["Muscat"],
    "Djouba": ["Juba"],
    "Hanoï": ["Hanoi"],
    "Mexico": ["Mexico City"],
    "Washington": ["Washington D.C.", "Washington DC"],
    "Koweït": ["Koweït City", "Kuwait City"],
    "Ciudad de la Paz": ["Oyala"],
    "Saint-Marin": ["Ville de Saint-Marin"],
    "Saint John's": ["St. John's"],
    "Saint-Pierre-Port": ["St Peter Port", "St. Peter Port"],
}

# Superficie corrigée : id → (km², source qui tranche).
AREA_OVERRIDE = {
    "FRA": (543000, "France métropolitaine seule (les DROM sont des entités à part) ; Wikipédia FR « France » : "
                    "« La France métropolitaine couvre une superficie d'environ 543 000 km2 »"),
    "HKG": (1114, "terres émergées ; Wikipédia FR « Hong Kong » : « une surface des terres émergées de 1 114,35 km2 » "
                  "(Wikidata 2 755 km² inclut les eaux)"),
    "MAC": (33.3, "Wikipédia FR « Macao » : « Aujourd'hui, Macao a une superficie de 33,3 km2 » (Wikidata 115 km² inclut les eaux)"),
    "TCA": (616, "Wikipédia FR « Îles Turques-et-Caïques » : « superficie totale terrestre de 616,3 km2 (à marée haute) »"),
    "VAT": (0.44, "Wikipédia FR « Vatican » : « une superficie totale de 0,439 km2 »"),
    "WLF": (142, "Wikipédia FR « Wallis-et-Futuna » : « La superficie de l'ensemble est de 142 km2 » (Wikidata 274 km² douteux)"),
}

# Voisins ajoutés à la géométrie (zone neutre entre les deux) : paire → raison.
NEIGHBORS_ADD = {
    ("ISR", "SYR"): "frontière internationale à travers le plateau du Golan, mis en zone neutre sur la carte",
}

# Continent : régions ONU (M49) sauf exceptions documentées.
CONTINENT_OVERRIDE = {
    "TWN": ("asie", "absent des régions ONU (M49) ; Asie de l'Est, comme dans mledoze/countries", "Asie de l'Est"),
    "CYP": ("europe", "M49 range Chypre en Asie de l'Ouest ; membre de l'Union européenne, classé en Europe comme dans mledoze/countries", None),
}

# Vérifications à la main des capitales piégeuses (étape 1), reprises dans DATA_REPORT.md.
CAPITAL_NOTES = (
    "Guinée équatoriale : Ciudad de la Paz est capitale depuis janvier 2026 (Wikidata P36 préférée depuis le "
    "2026-01-03 ; Wikipédia FR « Ciudad de la Paz » et « Malabo »). "
    "Indonésie : Jakarta reste la capitale ; le transfert vers Nusantara attend un décret présidentiel non signé, "
    "objectif 17 août 2028 (Wikipédia FR « Nusantara (ville) », Wikidata : Nusantara déprécié). "
    "Myanmar : Naypyidaw ; Kazakhstan : Astana ; Suisse : Berne, « ville fédérale » ; Nauru : pas de capitale "
    "officielle, Yaren siège du gouvernement ; Israël / Palestine : rôles explicites sans trancher le statut de "
    "Jérusalem."
)

# (contrôle, id) → décision motivée, avec la source qui tranche.
_M49 = ("on suit les régions ONU (M49), source du champ continent pour toutes les entités ; "
        "mledoze range les îles subantarctiques à part (« Antarctic »)")
DECISIONS: dict[tuple[str, str], str] = {
    ("capitale-en", "ATG"): "même ville (Saint John's), graphie anglaise différente",
    ("capitale-en", "GGY"): "même ville (St Peter Port = Saint-Pierre-Port)",
    ("capitale-en", "MNG"): "même ville (Ulan Bator = Oulan-Bator)",
    ("capitale-en", "BES"): "BES regroupe trois îles, chacune a son chef-lieu ; on retient Kralendijk (Bonaire, la plus "
                            "peuplée) avec le rôle « chef-lieu de Bonaire »",
    ("capitale-en", "GNQ"): "mledoze n'est pas à jour : capitale transférée à Ciudad de la Paz en janvier 2026 "
                            "(Wikidata P36 du 2026-01-03, Wikipédia FR « Ciudad de la Paz »)",
    ("capitale-en", "HKG"): "Victoria n'est plus une entité administrative ; pas de capitale distincte (capital_note_fr)",
    ("capitale-en", "TKL"): "pas de capitale officielle, l'administration tourne entre les atolls (capital_note_fr) ; "
                            "Fakaofo n'est qu'un des trois",
    ("continent", "ATF"): _M49,
    ("continent", "BVT"): _M49,
    ("continent", "HMD"): _M49,
    ("continent", "SGS"): _M49,
    ("continent", "UMI"): "M49 range les îles mineures en Océanie (Micronésie) : la plupart sont dans le Pacifique",
    ("superficie", "BLM"): "Wikidata conservé (24 km² avec les îlets) ; Wikipédia FR « Saint-Barthélemy » : "
                           "« environ 21 km2 (24 km2 avec ses îlets) »",
    ("superficie", "GIB"): "Wikidata conservé ; Wikipédia FR « Gibraltar » : « une superficie de 6,8 km2 » (mledoze arrondit)",
    ("superficie", "HMD"): "Wikidata conservé (368 km²) ; la géométrie Natural Earth donne 395 km², entre les deux sources",
    ("superficie", "NLD"): "Wikidata conservé : terres seules (37 378 km²) ; mledoze compte les eaux intérieures",
    ("superficie", "NOR"): "Wikidata conservé, chiffre officiel qui inclut Svalbard et Jan Mayen ; Wikipédia FR « Norvège » : "
                           "« Avec 385 155 km2 (Jan Mayen et Svalbard inclus) »",
    ("superficie", "TKL"): "Wikidata conservé (10 km²) ; écart d'arrondi sur des atolls (mledoze 12 km²)",
    ("monnaie", "CUW"): "Wikidata conservé : florin caribéen (XCG) ; Wikipédia FR « Curaçao » : « sa monnaie est le "
                        "florin caribéen » ; mledoze donne encore l'ancien florin des Antilles néerlandaises (ANG)",
    ("monnaie", "SXM"): "Wikidata conservé : florin caribéen (XCG), qui remplace le florin des Antilles néerlandaises "
                        "(Wikipédia FR « Saint-Martin (royaume des Pays-Bas) ») ; mledoze n'est pas à jour",
    ("monnaie", "SGS"): "Wikidata conservé ; Wikipédia FR : « le territoire adhère à la banque d'Angleterre et utilise "
                        "la livre sterling » ; la livre de Sainte-Hélène de mledoze concerne un autre territoire",
    ("plaque", "GRL"): "null confirmé : KN n'est pas enregistré à l'ONU ; le tableau EN le range dans les codes "
                       "abandonnés avec la mention « Unofficial. The official code is DK »",
    ("plaque", "CUW"): "null confirmé : CW n'apparaît que parmi les codes non officiels du tableau EN",
    ("plaque", "KNA"): "null confirmé : KAN n'apparaît que parmi les codes non officiels du tableau EN",
    ("plaque", "PRI"): "null confirmé : PR n'apparaît que parmi les codes non officiels du tableau EN",
    ("plaque", "PSE"): "null confirmé : P (avec la lettre arabe ف) n'apparaît que parmi les codes non officiels du "
                       "tableau EN",
    ("superficie", "YEM"): "Wikidata conservé ; Wikipédia FR « Yémen » : « le Yémen couvre une surface de 455 503 km2 »",
}

# Blocages > 20 min (brief) : notés ici, repris dans le rapport.
BLOCKERS: list[str] = [
    "Wikimedia limite à 10 requêtes/min un client dont l'User-Agent n'a pas de contact (API et upload.wikimedia.org). "
    "Pré-remplissage en masse du cache Wikipédia abandonné (décision du coordinateur, 12 oct.) ; contact dans l'UA "
    "en attente de l'accord de Josca (variable GEOATLAS_UA_CONTACT ou cache/ua_contact.txt).",
]

# Drapeaux : id → (fichier Commons à utiliser ou None pour garder P41, flag_quizzable, flag_note_fr).
# Un fichier identique à celui de l'État souverain donne flag_shared_with automatiquement.
_FR = "Flag of France.svg"
_FR_NOTE = "Collectivité française : le drapeau officiel est celui de la France."
FLAG_OVERRIDE = {
    "ESH": (None, False, "Le territoire n'a pas de drapeau reconnu par tous ; celui-ci est le drapeau de la "
                         "République arabe sahraouie démocratique."),
    "GUF": (_FR, False, "Département français : le drapeau officiel est celui de la France."),
    "GLP": (_FR, False, "Département français : le drapeau officiel est celui de la France."),
    "MTQ": (_FR, False, "Département français : le drapeau officiel est celui de la France."),
    "MYT": (_FR, False, "Département français : le drapeau officiel est celui de la France."),
    "REU": (_FR, False, "Département français : le drapeau officiel est celui de la France."),
    "BLM": (_FR, False, _FR_NOTE),
    "MAF": (_FR, False, _FR_NOTE),
    "SPM": (_FR, False, _FR_NOTE),
    "WLF": (_FR, False, _FR_NOTE),
    "NCL": (None, False, "La Nouvelle-Calédonie hisse côte à côte le drapeau français et le drapeau kanak "
                         "(celui-ci) ; elle n'a pas de drapeau propre unique."),
    "BES": ("Flag of the Netherlands.svg", False, "Communes néerlandaises : le drapeau officiel est celui des "
                                                  "Pays-Bas (Bonaire, Saint-Eustache et Saba ont chacune le leur)."),
    "SHN": ("Flag of Saint Helena.svg", False, "Drapeau de Sainte-Hélène ; Ascension et Tristan da Cunha ont "
                                               "chacune le leur."),
    "IOT": (None, False, "Pavillon du commissaire du territoire, revendiqué par Maurice ; le drapeau du territoire "
                         "a changé en 2025."),
    "UMI": ("Flag of the United States (DDD-F-416E specifications).svg", False, None),
    "ATA": (None, False, "L'Antarctique n'a pas de drapeau officiel ; celui-ci est un drapeau proposé."),
    "AFG": (None, False, "Deux drapeaux coexistent : le drapeau blanc de l'Émirat islamique depuis 2021 et le "
                         "tricolore noir-rouge-vert, encore utilisé à l'ONU."),
}

# Libellés Wikidata de langues remplacés partout par le nom français usuel.
LANG_NAME_FR = {
    "nrebele": "ndébélé du Sud",      # Wikidata « nrebele » : graphie fautive (ISO 639-3 nbl)
    "grec moderne": "grec",           # même langue que « grec » (Grèce) ; Chypre l'affichait autrement
    "māori": "maori",                 # graphie française (Wikipédia FR « Maori (langue) »)
    "palau": "paluan",                # nom de la langue (Wikipédia FR « Paluan ») ; Palau est le pays
}

# Carte d'identité : id → {champ: (valeur, raison avec la source qui tranche)}. Prime sur Wikidata.
_EUR = {"code": "EUR", "name_fr": "euro", "symbol": "€"}
_WF = "Wikipédia FR, article de l'entité"
_ZWE_CUR = ([{"code": "ZWG", "name_fr": "or du Zimbabwe", "symbol": "ZiG"},
             {"code": "USD", "name_fr": "dollar des États-Unis", "symbol": "$"}],
            "Wikidata mêle les anciennes monnaies et le panier de devises de 2009 ; on garde l'or du Zimbabwe "
            "(ZWG, en cours sur Wikidata) et le dollar américain, commun aux deux sources")
_MAC_CUR = ([{"code": "MOP", "name_fr": "pataca", "symbol": "MOP$"}],
            "monnaie officielle : la pataca ; le dollar de Hong Kong y circule seulement (mledoze ne donne que MOP)")
IDENTITY_OVERRIDE: dict[str, dict[str, tuple]] = {
    # monnaies
    "POL": {"currencies": ([{"code": "PLN", "name_fr": "złoty", "symbol": "zł"}],
                           "PLZ est l'ancien złoty, remplacé par le PLN")},
    "FRO": {"currencies": ([{"code": "DKK", "name_fr": "couronne danoise", "symbol": "kr"}],
                           "Wikidata vide ; la couronne féroïenne de mledoze est une émission locale de la couronne "
                           "danoise (DKK, commun aux deux)")},
    "IMN": {"currencies": ([{"code": "GBP", "name_fr": "livre sterling", "symbol": "£"}],
                           "Wikidata vide ; la livre mannoise de mledoze est une émission locale de la livre sterling "
                           "(GBP, commun aux deux)")},
    "ESH": {"calling_code": (None, "Wikidata donne +212, l'indicatif du Maroc : non retenu par neutralité"),
            "currencies": (None, "pas de monnaie propre : plusieurs monnaies circulent selon les zones (dirham "
                                 "marocain, dinar algérien… d'après mledoze), on n'en retient aucune par neutralité"),
            "languages_fr": (["arabe"], "l'arabe est langue officielle pour les deux parties qui revendiquent "
                                        "le territoire (Wikidata)")},
    "MAC": {"currencies": _MAC_CUR,
            "languages_fr": (["chinois", "portugais"], "langues officielles : chinois et portugais (mledoze) ; "
                                                       "Wikidata détaille cantonais et mandarin")},
    "ZWE": {"currencies": _ZWE_CUR,
            "languages_fr": (["anglais", "barwe", "chewa", "chitonga", "kalanga", "khoïsan", "nambya", "ndau",
                              "shona", "ndébélé du Nord", "sotho du Sud", "tsonga", "tswana", "venda", "xhosa"],
                             "langues officielles de la constitution (Wikidata, 16 avec la langue des signes, "
                             "écartée par la règle générale) ; « sindebele » de Wikidata = ndébélé du Nord")},
    # langues
    "AUT": {"languages_fr": (["allemand"], "mledoze donne le bavarois, à tort ; l'allemand est la langue "
                                           "officielle (Wikidata)")},
    "BFA": {"languages_fr": (["moré", "dioula", "peul", "bissa"],
                             _WF + " : « les langues officielles sont : le moré, le dioula, le foulfouldé (peul) "
                                   "et le bissa » (constitution de 2023)")},
    "MLI": {"languages_fr": (["bambara", "bobo", "bozo", "dogon", "hassanya", "khassonké", "malinké", "mamara",
                              "peul", "sénoufo", "songhaï", "soninké", "tamasheq"],
                             _WF + " : constitution de 2023, « les langues nationales sont les langues officielles "
                                   "du Mali » ; liste des 13 langues nationales de Wikidata")},
    "NER": {"languages_fr": (["haoussa"], _WF + " : « La langue nationale du Niger est le haoussa » ; le français "
                                                "n'est plus langue officielle depuis 2025")},
    "TWN": {"languages_fr": (["mandarin", "taïwanais"], _WF + " : le mandarin est langue officielle, le taïwanais "
                                                              "l'est devenu en 2018")},
    "USA": {"languages_fr": (["anglais"], _WF + " : « Les États-Unis adoptent l'anglais comme langue officielle "
                                                "le 1er mars 2025 »")},
    "FLK": {"languages_fr": (["anglais"], "Wikidata : « anglais britannique », sans code ; mledoze : anglais")},
    "GIB": {"languages_fr": (["anglais"], "Wikidata : « anglais britannique », sans code ; mledoze : anglais")},
    "GLP": {"languages_fr": (["français"], "Wikidata vide ; département français (mledoze : français)")},
    "MTQ": {"languages_fr": (["français"], "Wikidata vide ; collectivité française (mledoze : français)")},
    "GRC": {"languages_fr": (["grec"], "Wikidata : grec, sans code ISO ; mledoze : grec")},
    "URY": {"languages_fr": (["espagnol"], "Wikidata vide ; mledoze : espagnol")},
    "HKG": {"languages_fr": (["chinois", "anglais"], "langues officielles : chinois et anglais (mledoze) ; "
                                                     "Wikidata ne donne que le mandarin standard")},
    "CHN": {"languages_fr": (["mandarin standard"], "libellé Wikidata « putonghua » = mandarin standard "
                                                    "(mledoze : chinois)")},
    "NOR": {"languages_fr": (["norvégien", "same"], "Wikidata et mledoze donnent le norvégien (bokmål, nynorsk) "
                                                    "et les langues sames")},
    "BDI": {"languages_fr": (["kirundi", "français", "anglais"], "l'anglais est langue officielle depuis 2014 "
                                                                 "(Wikidata) ; mledoze n'est pas à jour")},
    "RWA": {"languages_fr": (["kinyarwanda", "français", "anglais", "swahili"],
                             "le swahili est langue officielle depuis 2017 (Wikidata) ; mledoze n'est pas à jour")},
    "MKD": {"languages_fr": (["macédonien", "albanais"], "l'albanais est co-officiel depuis 2019 (Wikidata) ; "
                                                         "mledoze n'est pas à jour")},
    "KGZ": {"languages_fr": (["kirghize", "russe"], "le russe est langue officielle au Kirghizistan (mledoze) ; "
                                                    "Wikidata ne donne que le kirghize")},
    "NFK": {"languages_fr": (["anglais", "norfolk"], "le norfolk est co-officiel (Wikidata et mledoze)")},
    "COM": {"languages_fr": (["comorien", "arabe", "français"], "comorien, arabe et français dans les deux sources "
                                                                "(Wikidata sans code ISO pour le comorien)")},
    "GGY": {"languages_fr": (["anglais", "français"], "anglais et français dans les deux sources")},
    "JEY": {"languages_fr": (["anglais", "français"], "anglais et français de Jersey dans les deux sources"),
            "demonym_fr": ("Jersiais", "Wikidata : « Jèrriais(e) », forme épicène ; mledoze : Jersiais")},
    "AFG": {"languages_fr": (["dari", "pachto"], "les deux langues officielles nationales (Wikidata et mledoze) ; "
                                                 "les autres ne sont officielles que dans certaines régions")},
    "BVT": {"languages_fr": (None, "île inhabitée")},
    # gentilés
    "GNB": {"demonym_fr": ("Bissau-Guinéen", "Wikidata : « Bissaoguinéen » et « Guinéen » (ce dernier désigne la "
                                             "Guinée) ; Wikipédia FR écrit « bissau-guinéen » (10 occurrences, aucune "
                                             "de « bissaoguinéen ») ; mledoze : Bissau-Guinéen")},
    "NCL": {"demonym_fr": ("Néo-Calédonien", "Wikidata : « Néo-Calédonien » et « Calédonien » ; mledoze : "
                                             "Néo-Calédonien")},
    "VGB": {"demonym_fr": (None, "Wikidata : « britannique » (pas propre au territoire) ; mledoze vide")},
    "ATA": {"demonym_fr": (None, "pas de population permanente ; « Antarcticain » (Wikidata) n'est pas d'usage "
                                 "établi en français")},
    "NZL": {"demonym_fr": ("Néo-Zélandais", "Wikidata : « Néozélandais » ; Wikipédia FR et mledoze écrivent "
                                            "« Néo-Zélandais »")},
    "LKA": {"demonym_fr": ("Sri-Lankais", "Wikidata : « Srilankais » ; Wikipédia FR écrit surtout « Sri-Lankais » "
                                          "(13 occurrences contre 5 dans les articles en cache)")},
    "SLE": {"demonym_fr": ("Sierra-Léonais", "Wikidata : « Sierraléonais » ; Wikipédia FR écrit « Sierra-Léonais » "
                                             "(8 occurrences contre 1)")},
    "TLS": {"demonym_fr": ("Est-Timorais", "Wikidata : « Timorais », qui vaut aussi pour le Timor occidental "
                                           "indonésien ; Wikipédia FR : « est-timorais »")},
    "LCA": {"demonym_fr": ("Saint-Lucien", "Wikidata : « Lucien » ; Wikipédia FR « Sainte-Lucie » : « créole "
                                           "saint-lucien » ; les autres « Saint-… » gardent la forme de leur article "
                                           "(« les Vincentais, Saint-Vincentais », « soldats christophiens », "
                                           "« Antiguayens »)")},
    "WSM": {"demonym_fr": ("Samoan", "Wikidata : « Samoen » ; Wikipédia FR « Samoa » : « les Samoans vivant à "
                                     "l'étranger », « femme politique samoane » ; aucune occurrence de « samoen » "
                                     "dans les articles en cache")},
    # sommets
    "ATG": {"highest_point": ({"name_fr": "mont Obama", "elevation_m": 402},
                              "nom gardé : Wikipédia FR « Antigua-et-Barbuda » : « leur point le plus haut est le "
                              "mont Obama à 402 m » ; l'article ne mentionne pas l'ancien nom Boggy Peak")},
    "CZE": {"highest_point": ({"name_fr": "Sněžka", "elevation_m": 1603},
                              "Wikidata : « Sniejka » ; titre de l'article Wikipédia FR : « Sněžka »")},
    "NIU": {"highest_point": (None, "Wikidata : « Point culminant de Niue », pas un nom de sommet")},
    # devises, indicatifs, symboles
    "FRA": {"currencies": ([_EUR], "le franc Pacifique (XPF) donné par Wikidata est la monnaie des collectivités "
                                   "du Pacifique, pas de la France"),
            "motto_fr": ("Liberté, Égalité, Fraternité", "Wikidata donne aussi « Rendez-vous en France », slogan "
                                                         "touristique et non devise nationale")},
    "SPM": {"demonym_fr": ("Saint-Pierrais ou Miquelonais", "Wikidata et mledoze : les habitants de chacune des "
                                                            "deux îles"),
            "motto_fr": (None, "« A mare labor » est en latin, pas en français")},
    "SSD": {"currencies": ([{"code": "SSP", "name_fr": "livre sud-soudanaise", "symbol": None}],
                           "Wikidata donne « Db », symbole de la dobra de Sao Tomé : erreur, symbole laissé vide")},
    "STP": {"currencies": ([{"code": "STN", "name_fr": "dobra", "symbol": "Db"}],
                           "Wikidata donne ₡ (colón du Costa Rica) et Db ; Db confirmé par mledoze")},
    # domaines internet
    "RUS": {"tld": (".ru", ".su, domaine de l'ex-URSS encore actif, n'est pas le domaine national (Wikidata et "
                           "mledoze donnent .ru en premier)")},
}
