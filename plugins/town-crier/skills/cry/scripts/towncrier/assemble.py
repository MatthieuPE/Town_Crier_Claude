"""Assemble the digest file.

Titles, links, authors, counts and lists come from the data; Claude only
writes the summary bodies, in ``summaries/<subsection id>.md``::

    <!-- paper: arXiv:2610.30264 -->
    - **Context:** ...
"""

import re
from pathlib import Path

from . import config as config_mod, files, labels as labels_mod, sheets

PAPER_MARK = re.compile(r"<!--\s*paper:\s*(\S+?)\s*-->")
MISSING_BODY = "*(summary missing)*"


def parse_summaries(text):
    """Bodies of a summaries file, by paper id.

    Parameters
    ----------
    text : str
        File content.

    Returns
    -------
    dict
        Paper id -> body text.
    """
    pieces = PAPER_MARK.split(text or "")
    return {pid: body.strip() for pid, body in zip(pieces[1::2], pieces[2::2])}


def load_summaries(run_dir):
    """Bodies of every subsection, by subsection id then paper id."""
    out = {}
    for path in sorted((Path(run_dir) / "summaries").glob("*.md")):
        out[path.stem] = parse_summaries(path.read_text(encoding="utf-8"))
    return out


def link_title(rec):
    """Title safe inside Markdown link text."""
    title = " ".join((rec.get("title") or "Untitled").split())
    return title.replace("[", "(").replace("]", ")")


def entry_header(rec, judgment, category, news, labels):
    """Heading and metadata line of one summarized paper."""
    meta = [f"*{sheets.first_author(rec, labels['et_al'])}*"]
    if rec.get("journal"):
        meta.append(f"*{rec['journal']}*")
    if category == 3:
        if judgment.get("field"):
            meta.insert(0, f"**{judgment['field']}**")
        if news:
            meta.append(f"[{labels['news']}: {news['outlet']}]({news['url']})")
    return f"#### [{link_title(rec)}]({rec['url']})\n" + " · ".join(meta)


def list_line(rec, labels):
    """One line of a category-1 list."""
    return f"- [{link_title(rec)}]({rec['url']}) — {sheets.first_author(rec, labels['et_al'])}"


def count_line(count, phrase, labels):
    """Sentence giving the number of papers of the period."""
    if count is None:
        return labels["count_unknown"].format(period=phrase)
    key = "count_one" if count == 1 else "count_many"
    return labels[key].format(n=count, period=phrase)


def render(resolved, selection, summaries, notes, news):
    """Digest text.

    Parameters
    ----------
    resolved : dict
        Resolved configuration.
    selection : dict
        Output of ``selection.finalize``.
    summaries : dict
        Subsection id -> paper id -> body.
    notes : list of dict
        Notes with a ``text`` key.
    news : dict
        Paper id -> ``{"url", "outlet"}``.

    Returns
    -------
    str
        Markdown digest.
    """
    labels, _ = labels_mod.for_language(resolved["output"].get("language", "English"))
    period = resolved["period"]
    phrase = labels_mod.period_phrase(period, labels)
    papers = selection["papers"]
    out = [f"# 📯 {resolved['output'].get('title', 'The Town Crier')} — {phrase}",
           f"*{labels_mod.fmt_date(period['start'], labels)} → {labels_mod.fmt_date(period['end'], labels)}*", ""]
    if notes:
        out += [f"> **{labels['notes']}**"] + [f"> - {n['text']}" for n in notes] + [""]
    if resolved["output"].get("contents", True):
        out.append(f"## {labels['contents']}")
        for sec in resolved["sections"]:
            out.append(f"- {sec['id']}. {sec['title']}")
            for sub in sec["subsections"]:
                count = selection["subsections"][sub["id"]]["count"]
                suffix = f" ({count})" if count is not None else ""
                out.append(f"  - {sub['id']} {sub['title']}{suffix}")
        out.append("")
    for sec in resolved["sections"]:
        out += [f"## {sec['id']}. {sec['title']}", ""]
        for sub in sec["subsections"]:
            sel = selection["subsections"][sub["id"]]
            out += [f"### {sub['id']} {sub['title']}"]
            if sub.get("count"):
                out.append(f"*{count_line(sel['count'], phrase, labels)}*")
            out.append("")
            if not sel["summaries"] and not sel["list"]:
                out += [f"*{labels['empty']}*", ""]
                continue
            bodies = summaries.get(sub["id"], {})
            for judgment in sel["summaries"]:
                rec = papers[judgment["paper_id"]]
                out += [entry_header(rec, judgment, sub["category"], news.get(rec["paper_id"]), labels),
                        "", bodies.get(rec["paper_id"], MISSING_BODY), ""]
            if sel["list"]:
                out += [f"**{labels['others']}**", ""]
                out += [list_line(papers[j["paper_id"]], labels) for j in sel["list"]] + [""]
    out += ["---", f"*{labels['footer']}*", ""]
    return "\n".join(out)


def output_path(run_dir, resolved):
    """Path of the digest file."""
    name = resolved["output"].get("filename", "town-crier_{start}_{end}.md")
    return Path(run_dir) / name.format(start=resolved["period"]["start"], end=resolved["period"]["end"])


def write(run_dir):
    """Assemble the digest of a run folder.

    Parameters
    ----------
    run_dir : str or Path
        Run folder.

    Returns
    -------
    Path
        Digest file.
    """
    run_dir = Path(run_dir)
    resolved = files.read_yaml(run_dir / "config.resolved.yaml")
    selection = files.read_json(run_dir / "selection.json")
    text = render(resolved, selection, load_summaries(run_dir),
                  files.read_json(run_dir / "notes.json", []), files.read_json(run_dir / "news.json", {}))
    path = output_path(run_dir, resolved)
    path.write_text(text, encoding="utf-8")
    return path
