"""Accuracy and format checks of a run, before delivery.

Errors must be fixed; warnings must be reviewed. The number check flags
every number of a summary that cannot be found in the paper's own text
(title, abstract, or the full-text sections read).
"""

import re
from pathlib import Path

from . import assemble, files, labels as labels_mod, prefilter

NUMBER = re.compile(r"\d+(?:[.,]\d+)?")
THOUSANDS = re.compile(r"(\d),(\d{3})(?!\d)")
DECIMAL_COMMA = re.compile(r"(\d),(\d)")
ABBREV = re.compile(r"\b(?:et al|e\.g|i\.e|cf|figs?|eqs?|sects?|secs?|vs|approx|ca|resp|no|dr|prof|refs?)\.",
                    re.I)
CITATION = re.compile(r"\b[A-Z][A-Za-z\-]+ (?:et al\.?|and [A-Z][A-Za-z\-]+),? \(?(?:1[89]\d\d|20\d\d)\b"
                      r"|\[\d+(?:[,\u2013-]\d+)*\]")
LINK = re.compile(r"\[[^\]]*\]\((https?://[^)\s]+)\)")


def normalize_numbers(text):
    """Text with thousands separators removed and decimal commas as points."""
    text = THOUSANDS.sub(r"\1\2", text or "")
    return DECIMAL_COMMA.sub(r"\1.\2", text)


def numbers_in(text):
    """Numbers worth checking: decimals, and integers of two digits or more."""
    found = NUMBER.findall(normalize_numbers(text))
    return [n for n in found if "." in n or len(n) >= 2]


def number_in(number, source):
    """True when ``number`` appears in ``source`` as a whole number."""
    return re.search(rf"(?<![\d.]){re.escape(number)}(?![\d])", source) is not None


def count_sentences(text):
    """Approximate sentence count, ignoring common abbreviations and decimals."""
    t = ABBREV.sub(lambda m: m.group(0).replace(".", "\u00a7"), text or "")
    t = re.sub(r"(\d)\.(\d)", "\\1\u00a7\\2", t)  # decimals
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9(\"'\u201c\u00ab\u00c0-\u00dd])", t.strip())
    return len([p for p in parts if p.strip()])


def check_category_1(body, labels):
    """Errors of a category-1 body: five labelled bullets, in order, none empty."""
    errors = []
    positions = []
    for label in labels["bullets"]:
        m = re.search(rf"^- \*\*{re.escape(label)}:\*\*(.*)$", body, re.M)
        if not m:
            errors.append(f"missing bullet '- **{label}:**'")
            continue
        positions.append(m.start())
        if not m.group(1).strip():
            errors.append(f"empty bullet '{label}': write '{labels['unknown']}' when the paper does not say")
    if positions != sorted(positions):
        errors.append("bullets out of order")
    return errors


def paper_sources(run_dir, rec):
    """Paper's own text for the number check, and whether full text was read."""
    parts = [rec.get("title", ""), rec.get("abstract", "")]
    path = Path(run_dir) / "fulltext" / f"{files.safe_name(rec['paper_id'])}.txt"
    has_full = path.exists()
    if has_full:
        parts.append(path.read_text(encoding="utf-8"))
    return normalize_numbers(" ".join(parts)), has_full


def check_numbers(run_dir, rec, body, verified):
    """Errors and warnings of the number check for one body."""
    errors, warnings = [], []
    source, has_full = paper_sources(run_dir, rec)
    flat_source = prefilter.normalize(source)
    for number in sorted(set(numbers_in(body))):
        if number_in(number, source):
            continue
        quotes = [v["quote"] for v in verified.get(rec["paper_id"], []) if v.get("number") == number]
        if any(prefilter.normalize(normalize_numbers(q)) in flat_source for q in quotes):
            continue
        if quotes and not has_full:
            warnings.append(f"{rec['paper_id']}: number {number} accepted from a recorded quote "
                            "(full text not saved, so not re-checked)")
            continue
        errors.append(f"{rec['paper_id']}: number {number} is not in the paper's text. Correct it from "
                      "the paper, write 'unknown', or record its source with `tc.py verify`.")
    return errors, warnings


def check_body(run_dir, sub, rec, body, labels, verified):
    """Errors and warnings of one summary body."""
    errors, warnings = [], []
    where = f"{sub['id']} {rec['paper_id']}"
    if not body or body == assemble.MISSING_BODY:
        return [f"{where}: summary missing in summaries/{sub['id']}.md"], []
    if sub["category"] == 1:
        errors += [f"{where}: {e}" for e in check_category_1(body, labels)]
    else:
        n = count_sentences(body)
        if n > 10:
            warnings.append(f"{where}: about {n} sentences; the maximum is 10")
    if LINK.search(body):
        errors.append(f"{where}: no links inside summaries (the heading already links the paper)")
    if CITATION.search(body):
        errors.append(f"{where}: summaries must not cite other works: '{CITATION.search(body).group(0)}'")
    errs, warns = check_numbers(run_dir, rec, body, verified)
    return errors + [f"{sub['id']} {e}" for e in errs], warnings + [f"{sub['id']} {w}" for w in warns]


def run(run_dir):
    """All checks of a run folder.

    Parameters
    ----------
    run_dir : str or Path
        Run folder, after ``assemble``.

    Returns
    -------
    dict
        ``errors`` and ``warnings`` lists.
    """
    run_dir = Path(run_dir)
    resolved = files.read_yaml(run_dir / "config.resolved.yaml")
    selection = files.read_json(run_dir / "selection.json")
    labels, _ = labels_mod.for_language(resolved["output"].get("language", "English"))
    summaries = assemble.load_summaries(run_dir)
    news = files.read_json(run_dir / "news.json", {})
    verified = files.read_json(run_dir / "verified.json", {})
    errors, warnings, seen = [], [], {}
    for sec in resolved["sections"]:
        for sub in sec["subsections"]:
            sel = selection["subsections"][sub["id"]]
            bodies = summaries.get(sub["id"], {})
            wanted = [j["paper_id"] for j in sel["summaries"]]
            for pid in sorted(set(bodies) - set(wanted)):
                errors.append(f"{sub['id']}: summary for {pid}, which is not selected here")
            for pid in wanted + [j["paper_id"] for j in sel["list"]]:
                if pid in seen:
                    errors.append(f"{pid} appears in {seen[pid]} and {sub['id']}")
                seen[pid] = sub["id"]
            for pid in wanted:
                errs, warns = check_body(run_dir, sub, selection["papers"][pid], bodies.get(pid), labels, verified)
                errors += errs
                warnings += warns
    allowed = {u for rec in selection["papers"].values()
               for u in (rec.get("url"), rec.get("html_url"), f"https://doi.org/{rec['doi']}" if rec.get("doi") else None)
               if u}
    allowed |= {n["url"] for n in news.values()}
    digest = assemble.output_path(run_dir, resolved)
    if not digest.exists():
        errors.append("digest not assembled yet: run `tc.py assemble` first")
    else:
        for url in LINK.findall(digest.read_text(encoding="utf-8")):
            if url not in allowed:
                errors.append(f"link not from the data or news.json: {url}")
    return {"errors": errors, "warnings": warnings}
