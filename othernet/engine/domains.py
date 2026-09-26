"""Every site on the Weave, in one place.

`indexed` says whether the Lanthorn search engine crawls the site. Roughly a
third of the Weave is invisible to search and only reachable by following
links, the Hearthring directory, or word of mouth.
"""

# key: (domain, name, category, nation, indexed, one-line description)
SITES = {
    # --- finding your way ---------------------------------------------------
    "lanthorn": ("lanthorn.ves", "Lanthorn", "Search", "PEL", False,
                 "Search the Weave by lantern rank."),
    "hearthring": ("hearthring.fol", "Hearthring", "Directories", "VEY", True,
                   "A hand-kept directory of the Weave, sorted by people, not engines."),
    "morrow": ("morrow.ves", "Morrow", "Portals", "VEY", True,
               "Your morning on the Weave: headlines, weather, rates, and links."),
    "snip": ("snip.ves", "snip.ves", "Tools", "SLT", False, "Short links for long threads."),
    "stillframe": ("stillframe.hal", "Stillframe", "Archives", "PEL", True,
                   "The Weave, as it used to be. Snapshots of pages since 401."),
    # --- knowledge -----------------------------------------------------------
    "commonplace": ("commonplace.hal", "The Commonplace", "Reference", "VEY", True,
                    "The shared commonplace book of Averra, kept by the learned guilds."),
    "numerary": ("numerary.gld", "Numerary", "Reference", "PEL", True,
                 "Rolls of proven results, kept by the Guild of Numerists."),
    "quorum": ("quorum.fol", "Quorum", "Community", "VEY", True,
               "Ask a question. Let the quorum decide."),
    "lexicon": ("lexicon.hal", "The Veylish Lexicon", "Reference", "VEY", True,
                "Words of Veylish and where they came from."),
    "observatory": ("observatory.pel", "Lanternport Observatory", "Science", "PEL", True,
                    "Moons, tides, and the night sky from the oldest observatory in Averra."),
    "chartroom": ("chartroom.ves", "Chartroom", "Maps", "VEY", True,
                  "Atlas of Averra from the Guild of Cartographers."),
    # --- news --------------------------------------------------------------
    "courier": ("ostmerecourier.wir", "The Ostmere Courier", "News", "VEY", True,
                "The Concordat's paper of record since 190 CR."),
    "tidings": ("tidings.slt", "Brineholt Tidings", "News", "SLT", True,
                "News of the Republic and the Reach."),
    "crier": ("thecrier.wir", "The Crier", "News", "VEY", True,
              "SHOUTING THE NEWS SINCE 401"),
    "lodestone": ("lodestone.wir", "Lodestone", "Science", "PEL", True,
                  "Science for the curious."),
    "radio": ("radiolantern.pel", "Radio Lantern", "Media", "PEL", False,
              "Broadcasting from Observatory Hill."),
    # --- commerce ------------------------------------------------------------
    "bazaar": ("bazaar.ves", "Bazaar", "Shopping", "VEY", True,
               "Everything, from everywhere, to your door."),
    "emberline": ("emberline.ves", "Emberline", "Travel", "SLT", True,
                  "Ferries and airships across the Glass Sea and the Grey Reach."),
    "drovers": ("drovers.ves", "Drovers' Bank", "Finance", "VEY", True,
                "Banking since 211 CR."),
    "hollowmarket": ("hollowmarket.ves", "Hollowmarket", "Shopping", "VEY", True,
                     "Auctions of antiques, looms, and curiosities."),
    "hearthfind": ("hearthfind.ves", "Hearthfind", "Property", "VEY", True,
                   "Find a hearth to call your own."),
    "vantle": ("vantle.ves", "Vantle", "Technology", "VEY", True, "Makers of the Slate."),
    "copperkettle": ("copperkettle.ves", "The Copper Kettle", "Food", "VEY", True,
                     "Tea rooms since 389."),
    "quillmere": ("quillmere.ves", "Quillmere Press", "Books", "VEY", True,
                  "Publishers and booksellers since 244 CR."),
    "tastemark": ("tastemark.ves", "Tastemark", "Reviews", "SLT", True,
                  "Honest reviews of places to eat, drink, and sleep."),
    "noticeboard": ("noticeboard.fol", "The Noticeboard", "Classifieds", "VEY", False,
                    "Pins, notes, and wanted ads."),
    # --- government and civic ------------------------------------------------
    "exchange": ("exchange.slt", "Brineholt Exchange", "Finance", "SLT", True,
                 "Share prices and filings of listed companies."),
    "registry": ("registry.vey", "Concordat Registry", "Government", "VEY", True,
                 "Public records of companies in the Concordat of Veyl."),
    "assembly": ("assembly.vey", "Concordat Assembly", "Government", "VEY", True,
                 "Delegates, bills, and votes of the Concordat Assembly."),
    "weather": ("weather.vey", "Concordat Weather Office", "Weather", "VEY", True,
                "Forecasts and climate records."),
    "tramways": ("tramways.slt", "Brineholt Tramways", "Transport", "SLT", True,
                 "Trams, funiculars, and service updates."),
    "moot": ("rulings.khr", "Moot Rulings", "Government", "KHR", False,
             "Rulings of the Moot of Holds and the clan courts."),
    "stats": ("stats.pel", "Pellucid Statistical Office", "Government", "PEL", True,
              "Numbers about the Isles, free to all."),
    "post": ("post.vey", "Concordat Post", "Government", "VEY", True,
             "Postcodes, postage, and parcel tracking."),
    "patents": ("patentrolls.gld", "Patent Rolls", "Reference", "VEY", True,
                "The rolls of the Guild of Inventors."),
    # --- learning and culture ------------------------------------------------
    "university": ("lanternport.hal", "Lanternport University", "Education", "PEL", True,
                   "Light is owed to all."),
    "annals": ("annals.hal", "The Annals", "Science", "PEL", True,
               "Collected papers of the learned halls."),
    "athenaeum": ("athenaeum.hal", "The Athenaeum", "Libraries", "VEY", True,
                  "Catalogue of the Ostmere Athenaeum and its branch libraries."),
    "museum": ("deephalls.khr", "Museum of the Deep Halls", "Museums", "KHR", True,
               "Nine centuries of the Holds, carved in stone."),
    "reelhouse": ("reelhouse.ves", "Reelhouse", "Film", "VEY", True,
                  "Every film, every player, every reel."),
    "bellows": ("bellows.ves", "Bellows Records", "Music", "SLT", True,
                "Independent records from the Rope Walk."),
    "vaultball": ("vaultball.ves", "Vaultball Premier Circuit", "Sport", "SLT", True,
                  "The official site of the Premier Circuit."),
    # --- community and personal ------------------------------------------------
    "chatter": ("chatter.fol", "Chatter", "Social", "SLT", True, "What's the chatter?"),
    "tallowboards": ("tallowboards.fol", "Tallow Boards", "Forums", "VEY", False,
                     "The oldest message boards on the Weave."),
    "wrenwrites": ("wrenwrites.fol", "Wren Writes", "Blogs", "VEY", False,
                   "Walks, ferries, and small towns."),
    "spirekeeper": ("spirekeeper.fol", "The Spire Log", "Blogs", "SLT", False,
                    "Notes from the lamp room."),
    "ossawatcher": ("ossawatcher.fol", "OSSA WATCHER", "Blogs", "VEY", False,
                    "THEY DON'T WANT YOU TO LOOK UP"),
    "hearthandhob": ("hearthandhob.fol", "Hearth & Hob", "Food", "VEY", True,
                     "Recipes from a Gorsefield kitchen."),
    "inkling": ("inkling.fol", "Inkling", "Comics", "PEL", False,
                "A comic about a squid who works in a library."),
    "fathomwiki": ("fathomwiki.fol", "Fathom Wiki", "Games", "PEL", True,
                   "The Fathom and Fathom: Undertow wiki that anyone can edit."),
    "guildwork": ("guildwork.gld", "Guildwork", "Jobs", "VEY", True,
                  "Work, apprenticeships, and guild placements."),
    "whiskerhaven": ("whiskerhaven.fol", "Whiskerhaven", "Animals", "SLT", False,
                     "Rehoming cats, dogs, and the occasional gull."),
    "weft": ("weft.gld", "Weft", "Technology", "PEL", True,
             "The Weft language for looms. Docs, reference, and releases."),
    "synod": ("synod.odd", "The Synod of the Pale Flame", "Government", "ODD", False,
              "Official notices of the Synod."),
}


def domain(key):
    return SITES[key][0]


def url(key, path="/"):
    return f"http://{SITES[key][0]}{path}"


def name(key):
    return SITES[key][1]


def key_of_domain(dom):
    for k, v in SITES.items():
        if v[0] == dom:
            return k
    return None
