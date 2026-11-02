"""Judgments written by Claude, and the final selection.

Judgment file format, one paper per line::

    <paper_id> | y | <score 1-3> | <kind> | <field or -> | <reason>
    <paper_id> | n

Lines starting with ``#`` are comments.
"""

from dataclasses import asdict, dataclass

from . import config as config_mod, vocab

YES = {"y", "yes", "true", "1", "on"}
NO = {"n", "no", "false", "0", "off"}


@dataclass
class Judgment:
    """Claude's judgment of one candidate for one subsection."""

    paper_id: str
    on_theme: bool
    score: int = 0
    kind: str = "research"
    field: str = None
    reason: str = ""


def parse_line(line):
    """Judgment from one line.

    Parameters
    ----------
    line : str
        ``id | y/n | score | kind | field | reason``.

    Returns
    -------
    Judgment

    Raises
    ------
    ValueError
        Malformed line.
    """
    parts = [p.strip() for p in line.split("|")]
    if len(parts) < 2:
        raise ValueError(f"expected 'id | y/n | ...': {line!r}")
    pid, flag = parts[0], parts[1].lower()
    if flag in NO:
        return Judgment(pid, False, reason=" | ".join(parts[5:]) if len(parts) > 5 else "")
    if flag not in YES:
        raise ValueError(f"second column must be y or n: {line!r}")
    if len(parts) < 3 or not parts[2].isdigit() or not 1 <= int(parts[2]) <= 3:
        raise ValueError(f"on-theme papers need a score 1-3 in column 3: {line!r}")
    kind = parts[3].lower() if len(parts) > 3 and parts[3] else "research"
    field = parts[4] if len(parts) > 4 and parts[4] not in ("", "-") else None
    reason = " | ".join(parts[5:]) if len(parts) > 5 else ""
    return Judgment(pid, True, int(parts[2]), kind, field, reason)


def parse(text):
    """Judgments of a file; blank and ``#`` lines are skipped."""
    out = []
    for line in text.splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            out.append(parse_line(line))
    return out


def validate(judgments, pool, category):
    """Problems in one subsection's judgments.

    Parameters
    ----------
    judgments : list of Judgment
        Parsed judgments.
    pool : list of str
        Candidate ids of the subsection.
    category : int
        Summary category.

    Returns
    -------
    list of str
        Errors; empty when the judgments cover the pool exactly once.
    """
    errors = []
    ids = [j.paper_id for j in judgments]
    unknown = sorted(set(ids) - set(pool))
    missing = [p for p in pool if p not in set(ids)]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if unknown:
        errors.append(f"not in this subsection's candidates: {', '.join(unknown)}")
    if missing:
        errors.append(f"{len(missing)} candidate(s) not judged: {', '.join(missing)}")
    if dupes:
        errors.append(f"judged twice: {', '.join(dupes)}")
    for j in judgments:
        if j.on_theme and j.kind not in vocab.KINDS:
            errors.append(f"{j.paper_id}: kind must be one of {vocab.KINDS}")
        if j.on_theme and category == 3 and not vocab.match_field(j.field):
            errors.append(f"{j.paper_id}: category 3 needs a field tag among {list(vocab.FIELDS)}")
    return errors


def ranked(judgments, records):
    """On-theme judgments, best first (score, then newest, then id)."""
    on = [j for j in judgments if j.on_theme]
    on.sort(key=lambda j: j.paper_id)
    on.sort(key=lambda j: records.get(j.paper_id, {}).get("first_seen", ""), reverse=True)
    on.sort(key=lambda j: j.score, reverse=True)  # stable sorts: score wins
    return on


def _picks(sub, order, taken):
    """Papers summarized in a subsection."""
    allowed = vocab.SUMMARY_KINDS[sub["category"]]
    excluded = {vocab.match_field(f) for f in sub.get("exclude_fields") or []}
    picks, fields = [], set()
    for j in order:
        if j.paper_id in taken or j.kind not in allowed:
            continue
        if sub["category"] == 3:
            field = vocab.match_field(j.field)
            if field in excluded or (sub.get("one_per_field", True) and field in fields):
                continue
            fields.add(field)
        picks.append(j)
        if len(picks) == sub["n_papers"]:
            break
    return picks


def finalize(resolved, pools, judgments, records, uncounted=()):
    """Summaries, lists and counts of every subsection.

    Summaries are served in reading order; a paper summarized once is
    skipped afterwards. Category 1 lists then hold the remaining on-theme
    papers not summarized anywhere and not listed earlier.

    Parameters
    ----------
    resolved : dict
        Resolved configuration.
    pools : dict
        Subsection id -> candidate ids.
    judgments : dict
        Subsection id -> list of Judgment.
    records : dict
        Paper id -> record.
    uncounted : iterable of str
        Subsections filled by search instead of the data: their count is
        unknown (None).

    Returns
    -------
    dict
        Selection, ready to write as ``selection.json``.
    """
    uncounted = set(uncounted)
    subs = list(config_mod.iter_subsections(resolved))
    order = {s["id"]: ranked(judgments.get(s["id"], []), records) for s in subs}
    summarized, out = set(), {}
    for sub in subs:
        picks = _picks(sub, order[sub["id"]], summarized)
        summarized.update(j.paper_id for j in picks)
        out[sub["id"]] = {
            "category": sub["category"], "theme": sub["theme"], "title": sub["title"],
            "pool": len(pools.get(sub["id"], [])),
            "count": len(order[sub["id"]]) if sub.get("count") and sub["id"] not in uncounted else None,
            "search_only": sub["id"] in uncounted,
            "summaries": [asdict(j) for j in picks],
            "list": [],
        }
    listed = set()
    for sub in subs:
        if sub["category"] != 1 or not sub.get("list_others", True):
            continue
        rest = [j for j in order[sub["id"]] if j.paper_id not in summarized and j.paper_id not in listed]
        listed.update(j.paper_id for j in rest)
        out[sub["id"]]["list"] = [asdict(j) for j in rest]
    used = summarized | listed
    return {"period": resolved["period"], "subsections": out,
            "papers": {pid: records[pid] for pid in sorted(used) if pid in records}}
