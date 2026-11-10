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
    """Title safe inside Markdown link text: no brackets, no HTML tags.

    Math in titles such as ``<B>`` or ``0.4<z<4`` would otherwise be read
    as HTML by Markdown viewers.
    """
    title = " ".join((rec.get("title") or "Untitled").split())
    title = title.replace("[", "(").replace("]", ")")              # keep link syntax intact
    return title.replace("<", "&lt;").replace(">", "&gt;")          # shown as < and >


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


def list_line(rec, labels, field=None):
    """One line of a list of papers without summary; category 3 shows the field."""
    tag = f"**{field}** · " if field else ""
    return f"- {tag}[{link_title(rec)}]({rec['url']}) — {sheets.first_author(rec, labels['et_al'])}"


def note_lines(notes, target, labels):
    """Notes attached to one section or subsection, as quoted lines."""
    return [f"> **{labels['note']}:** {n['text']}" for n in notes if str(n.get("section") or "") == target]


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
        Notes with a ``text`` key and an optional ``section`` (section or
        subsection id). Notes are shown under their section or subsection;
        notes without one are gathered at the end, never at the top.
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
    subs_sel = selection["subsections"]
    out = [f"# 📯 {resolved['output'].get('title', 'The Town Crier')} — {phrase}",
           f"*{labels_mod.fmt_date(period['start'], labels)} → {labels_mod.fmt_date(period['end'], labels)}*", ""]
    if resolved["output"].get("contents", True):
        out.append(f"## {labels['contents']}")
        for sec in resolved["sections"]:
            out.append(f"- {sec['id']}. {sec['title']}")
            for sub in sec["subsections"]:
                count = subs_sel[sub["id"]]["count"]
                suffix = f" ({count})" if count is not None else ""
                out.append(f"  - {sub['id']} {sub['title']}{suffix}")
        out.append("")
    for sec in resolved["sections"]:
        out += [f"## {sec['id']}. {sec['title']}", ""]
        sec_notes = note_lines(notes, str(sec["id"]), labels)
        if sec_notes:
            out += sec_notes + [""]
        empty = all(not subs_sel[s["id"]]["summaries"] and not subs_sel[s["id"]]["list"]
                    for s in sec["subsections"])
        if empty and not any(note_lines(notes, s["id"], labels) for s in sec["subsections"]):
            out += [f"*{labels['empty_section'].format(period=phrase)}*", ""]
            continue
        for sub in sec["subsections"]:
            sel = subs_sel[sub["id"]]
            out += [f"### {sub['id']} {sub['title']}"]
            if sub.get("count"):
                out.append(f"*{count_line(sel['count'], phrase, labels)}*")
            out.append("")
            sub_notes = note_lines(notes, sub["id"], labels)
            if sub_notes:
                out += sub_notes + [""]
            if not sel["summaries"] and not sel["list"]:
                out += [f"*{labels['empty']}*", ""]
                continue
            if not sel["summaries"]:
                out += [f"*{labels['no_close_fit'].format(period=phrase)}*", ""]
            bodies = summaries.get(sub["id"], {})
            for judgment in sel["summaries"]:
                rec = papers[judgment["paper_id"]]
                out += [entry_header(rec, judgment, sub["category"], news.get(rec["paper_id"]), labels),
                        "", bodies.get(rec["paper_id"], MISSING_BODY), ""]
            if sel["list"]:
                heading = labels["others_3"] if sub["category"] == 3 else labels["others"]
                out += [f"**{heading}**", ""]
                out += [list_line(papers[j["paper_id"]], labels, j.get("field") if sub["category"] == 3 else None)
                        for j in sel["list"]] + [""]
    known = {str(s["id"]) for s in resolved["sections"]} | {
        s["id"] for sec in resolved["sections"] for s in sec["subsections"]}
    general = [n for n in notes if str(n.get("section") or "") not in known]
    if general:
        out += [f"## {labels['notes']}", ""] + [f"- {n['text']}" for n in general] + [""]
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
