# full word to the abbreviations are on openstreetmap
WORDS_MAP = {
    "academy": "acad",  # Civil Defence Acad
    "aerospace": "a'space",
    "after": "aft",
    "and": "&",
    "apartments": "apts",  # Hillview Apts
    "association": "assn",
    "avenue": "ave",
    "before": "bef",
    "between": "bet",
    "block": "blk",
    "building": "bldg",
    "bukit": "bt",
    "carpark": "cp",
    "cemetery": "cemy",  # Bef Muslim Cemy Path 7
    "centre": "ctr",
    "children": "child",
    "christian": "chr",  # Aft Chr Cemy Path 9
    "choa chu kang": "cck",
    "church": "ch",
    "college": "coll",
    "commonwealth": "c'wealth",
    "company": "co",
    "complex": "cplx",
    "corporation": "corp",
    "court": "ct",
    "cresent": "cres",
    "environment": "env",
    "drive": "dr",
    "estate": "est",
    "food centre": "fc",
    "garden": "gdn",  # Nirvana Memorial Gdn
    "gardens": "gdns",
    "heights": "hts",
    "hospital": "hosp",
    "house": "hse",
    "inspection": "insp",
    "interchange": "int",
    "international": "intl",
    "kampong": "kg",
    "jalan": "jln",
    "library": "lib",
    "link": "lk",  # Bef Seletar A'Space Lk
    "lorong": "lor",
    "market": "mkt",
    "methodist": "meth",  # Aft Trinity Meth Ch
    "metropolitan": "met",
    "mosque": "mque",  # Pusara Aman Mque
    "north": "nth",
    "opposite": "opp",
    "park": "pk",  # East Coast Pk Svc Rd
    "place": "pl",
    "plant": "plt",
    "playground": "p/g",
    "primary": "pr",
    "reclamation": "reclam",
    "reservoir": "resvr",
    "road": "rd",
    "saint": "st.",
    "school": "sch",
    "schoolhouse": "s/h",  # KiddiWinkie S/H @ Mountbatten
    "secondary": "sec",
    "serangoon": "s'goon",
    "service": "svc",
    "services": "svcs",
    "singapore": "s'pore",
    "squre": "sq",
    "station": "stn",
    "tanjong": "tg",
    "temple": "tp",
    "temporary": "temp",
    "terminal": "ter",
    "terrace": "terr",  # chuan terr
    "tower": "twr",  # Suntec Twr Two
    "towers": "twrs",  # Lutheran Twrs
    "townhouse": "townhse",  # Opp Loyang Townhse
    "townhouses": "townhse",  # Opp Loyang Townhse (map plural to same one)
    "walk": "wk",  # grace wk
    "water": "wtr",  # Kranji Wtr Reclam Plt
    "woodlands": "w'lands",
}

# not mapped
# S.A. Deaf -> Singapore Association


def transform_query_token(query_token: str) -> str:
    """
    transforms search query using a word mapping if it exists
    """
    return WORDS_MAP.get(query_token) or query_token
