# full word to the abbreviations are on openstreetmap
WORDS_MAP = {
    "singapore": "s'pore",
    "road": "rd",
    "drive": "dr",
    "gardens": "gdns",
    "cresent": "cres",
    "station": "stn",
    "opposite": "opp",
    "primary": "pr",
    "secondary": "sec",
    "college": "coll",
    "school": "sch",
    "complex": "cplx",
    "terminal": "ter",
    "avenue": "ave",
    "bukit": "bt",
    "after": "aft",
    "before": "bef",
    "between": "bet",
    "block": "blk",
    "centre": "ctr",
    "jalan": "jln",
    "corporation": "corp",
    "service": "svc",
    "services": "svcs",
    "woodlands": "w'lands",
    "squre": "sq",
    "serangoon": "s'goon",
    "carpark": "cp",
    "north": "nth",
    "place": "pl",
    "kampong": "kg",
    "commonwealth": "c'wealth",
    "interchange": "int",
    "international": "intl",
    "tanjong": "tg",
    "company": "co",
    "inspection": "insp",
    "and": "&",
    "library": "lib",
    "estate": "est",
    "hospital": "hosp",
    "children": "child",
    "church": "ch",
    "environment": "env",
    "metropolitan": "met",
    "saint": "st.",
    "association": "assn",
    "choa chu kang": "cck",
    "building": "bldg",
    "reservoir": "resvr",
    "lorong": "lor",
    "court": "ct",
    "walk": "wk",  # grace wk
    "terrace": "terr",  # chuan terr
    "methodist": "meth",  # Aft Trinity Meth Ch
    "schoolhouse": "s/h",  # KiddiWinkie S/H @ Mountbatten
    "house": "hse",
    "park": "pk",  # East Coast Pk Svc Rd
    "playground": "p/g",
    "tower": "twr",  # Suntec Twr Two
    "towers": "twrs",  # Lutheran Twrs
    "heights": "hts",
    "market": "mkt",
    "food centre": "fc",
    "temporary": "temp",
    "water": "wtr",  # Kranji Wtr Reclam Plt
    "reclamation": "reclam",
    "plant": "plt",
    "aerospace": "a'space",
    "link": "lk",  # Bef Seletar A'Space Lk
    "temple": "tp",
}


def transform_query_token(query_token: str) -> str:
    """
    transforms search query using a word mapping if it exists
    """
    return WORDS_MAP.get(query_token) or query_token
