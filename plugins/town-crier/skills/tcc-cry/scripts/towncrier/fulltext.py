"""Keep only some sections of a paper's full text, to save tokens.

Works on text extracted from PDFs (alphaXiv ``get_paper_content``) or
Markdown-like text. Headings are recognised when numbered (``2. DATA``,
``3 Results``, ``## 4 Discussion``) or when they are a known unnumbered
heading (``ABSTRACT``, ``References``...).
"""

import json
import re
from pathlib import Path

NUMBERED = re.compile(r"^\s*#*\s*(?P<num>\d{1,2}(?:\.\d{1,2})*)\.?\s+(?P<title>[A-Z][^\n]{1,70})$")
UNNUMBERED = re.compile(r"^\s*#*\s*(?P<title>[A-Za-z][A-Za-z &\-]{2,40})\s*:?\s*$")
KNOWN_UNNUMBERED = {
    "abstract": "abstract",
    "acknowledgements": "back", "acknowledgments": "back", "acknowledgement": "back",
    "acknowledgment": "back", "references": "back", "bibliography": "back",
    "author contributions": "back", "data availability": "back", "funding": "back",
    "conflicts of interest": "back", "competing interests": "back",
}
MIN_LETTERS = 4  # shorter lines are figure-axis or equation debris


def text_from_tool_result(raw):
    """Paper text from a saved tool result or a plain text file.

    Parameters
    ----------
    raw : str
        File content: JSON list of ``{"type": "text", "text": ...}`` blocks,
        a JSON object with ``text`` or ``content``, or plain text.

    Returns
    -------
    str
        Text.
    """
    try:
        data = json.loads(raw)
    except ValueError:
        return raw
    if isinstance(data, list):
        return "\n".join(b.get("text", "") for b in data if isinstance(b, dict))
    if isinstance(data, dict):
        for key in ("text", "content"):
            value = data.get(key)
            if isinstance(value, str):
                return value
            if isinstance(value, list):
                return "\n".join(b.get("text", "") for b in value if isinstance(b, dict))
    return raw


def _is_title_like(title):
    """True for heading-like titles, not sentence starts or running heads."""
    words = title.split()
    if len(words) > 8 or "," in title or title.rstrip().endswith((".", ";")):
        return False
    if title.isupper():
        return True
    long_words = [w for w in words if len(w) > 3]
    caps = [w for w in long_words if w[0].isupper()]
    return not long_words or len(caps) / len(long_words) >= 0.5


def classify(title):
    """Canonical name of a top-level section title, or None if unclear."""
    t = title.lower()
    if "introduc" in t:
        return "introduction"
    if "conclu" in t or t.strip() in ("summary", "summary and outlook"):
        return "conclusions"
    if "result" in t:
        return "results"
    if "discussion" in t:
        return "discussion"
    if t.startswith("appendix"):
        return "back"
    return None


def find_headings(lines):
    """Headings found in a text.

    Parameters
    ----------
    lines : list of str
        Text lines.

    Returns
    -------
    list of tuple
        ``(line index, canonical name, heading text)``. Numbered top-level
        sections with an unclear title are ``methods`` before the first
        results-like section and ``other`` after it; numbered subsections
        inherit their parent.
    """
    titles = [m.group("title").strip() for m in (NUMBERED.match(ln.strip()) for ln in lines) if m]
    repeated = {t for t in titles if titles.count(t) > 1}  # page running heads
    found, current, seen_results = [], None, False
    for i, line in enumerate(lines):
        text = line.strip()
        m = NUMBERED.match(text)
        if m and m.group("title").strip() not in repeated and _is_title_like(m.group("title")):
            if "." in m.group("num"):
                if current:
                    found.append((i, current, text))  # subsection: parent's name
                continue
            name = classify(m.group("title"))
            if name in ("results", "discussion", "conclusions"):
                seen_results = True
            current = name or ("other" if seen_results else "methods")
            found.append((i, current, text))
            continue
        m = UNNUMBERED.match(text)
        if m and m.group("title").lower().strip() in KNOWN_UNNUMBERED:
            current = KNOWN_UNNUMBERED[m.group("title").lower().strip()]
            found.append((i, current, text))
        elif m and m.group("title").lower().startswith("appendix") and len(text) < 40:
            current = "back"
            found.append((i, current, text))
    return found


EXPONENT = re.compile(r"[−-]?\d{1,2}")
ENDS_WITH_TEN = re.compile(r"(?:^|[^\d.])10$")


def _clean(block):
    """Join wrapped lines; keep numbers; rebuild powers of ten.

    PDF extraction puts superscripts on their own line (``~10`` then
    ``4``). Such pairs become ``10^4`` so that no number changes meaning.
    Lines with no digit and fewer than ``MIN_LETTERS`` letters (symbol
    debris) are dropped. Words split by an end-of-line hyphen are joined.
    """
    out = []
    for raw in block:
        line = raw.strip()
        if not line:
            continue
        if EXPONENT.fullmatch(line) and out and ENDS_WITH_TEN.search(out[-1]):
            out[-1] += "^" + line.replace("−", "-")  # superscript exponent
            continue
        if sum(c.isalpha() for c in line) < MIN_LETTERS and not any(c.isdigit() for c in line):
            continue  # symbol debris
        if out and out[-1].endswith("-") and line[:1].islower():
            out[-1] = out[-1][:-1] + line  # hyphenated word
            continue
        out.append(line)
    return " ".join(out)


def cut(text, sections, abstract=None, max_chars=60000):
    """Selected sections of a paper.

    Parameters
    ----------
    text : str
        Full text.
    sections : list of str
        Canonical sections to keep, e.g. ``["abstract", "methods",
        "results", "conclusions"]``.
    abstract : str, optional
        Abstract to use when the text has no ABSTRACT heading.
    max_chars : int
        Cap on the output size.

    Returns
    -------
    out : str
        Kept text, one block per section: ``[[name: heading]]`` then text.
    stats : dict
        Characters in and out, sections found, kept and missing.
    """
    lines = text.splitlines()
    heads = find_headings(lines)
    blocks = []
    if not heads:
        cut_at = re.search(r"\n\s*(references|bibliography)\s*\n", text, re.I)
        body = text[:cut_at.start()] if cut_at else text
        blocks.append(("full text (no headings found)", _clean(body.splitlines())))
    else:
        bounds = heads + [(len(lines), None, None)]
        for (start, name, head), (stop, _, _) in zip(bounds, bounds[1:]):
            if name in sections:
                blocks.append((f"{name}: {head}", _clean(lines[start + 1:stop])))
    found_names = sorted({n for _, n, _ in heads})
    if "abstract" in sections and "abstract" not in found_names and abstract:
        blocks.insert(0, ("abstract: from the database", abstract))
        found_names.append("abstract")
    out = "\n\n".join(f"[[{label}]]\n{body}" for label, body in blocks if body)
    truncated = len(out) > max_chars
    out = out[:max_chars]
    stats = {"chars_in": len(text), "chars_out": len(out), "approx_tokens_out": len(out) // 4,
             "sections_found": found_names, "kept": sorted({b[0].split(":")[0] for b in blocks}),
             "missing": [s for s in sections if s not in found_names], "truncated": truncated}
    return out, stats


def cut_file(src, dst, sections, abstract=None, max_chars=60000):
    """Cut a saved full text and write the result.

    Parameters
    ----------
    src : str or Path
        Saved tool result or text file.
    dst : str or Path
        Output text file.
    sections : list of str
        Sections to keep.
    abstract : str, optional
        Fallback abstract.
    max_chars : int
        Cap on the output size.

    Returns
    -------
    dict
        Statistics (see ``cut``).
    """
    text = text_from_tool_result(Path(src).read_text(encoding="utf-8"))
    out, stats = cut(text, sections, abstract=abstract, max_chars=max_chars)
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    Path(dst).write_text(out + "\n", encoding="utf-8")
    return stats
