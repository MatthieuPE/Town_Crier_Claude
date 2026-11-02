"""Fixed vocabularies shared by the run tools."""

# field tags of category-3 papers
FIELDS = (
    "Astronomy & astrophysics",
    "Physics",
    "Chemistry & materials",
    "Biology",
    "Medicine & health",
    "Earth & environment",
    "Mathematics & computing",
    "Engineering & technology",
    "Social & behavioural sciences",
)

# kinds of paper, judged by Claude
KINDS = ("research", "review", "proceedings", "erratum", "other")

# kinds allowed in summaries, per category (lists of category 1 keep all)
SUMMARY_KINDS = {1: {"research", "review", "proceedings", "other"}, 2: {"research", "other"},
                 3: {"research", "other"}}

# sections that can be read from full texts
SECTIONS = ("abstract", "introduction", "methods", "results", "discussion", "conclusions")

FULL_TEXT_SOURCES = ("alphaxiv", "abstract", "html")
RANK_BY = ("relevance", "impact")

UNKNOWN = "unknown"


def match_field(value):
    """Canonical field tag for a free-form value, or None.

    Parameters
    ----------
    value : str
        Field written by Claude.

    Returns
    -------
    str or None
        Entry of ``FIELDS`` matched case-insensitively.
    """
    key = (value or "").strip().lower()
    for name in FIELDS:
        if key == name.lower():
            return name
    return None
