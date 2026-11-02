"""Tests of digest assembly."""

import pytest

from towncrier import assemble


@pytest.fixture
def parts():
    """Minimal resolved configuration and selection."""
    resolved = {
        "output": {"title": "The Town Crier", "language": "English", "contents": True},
        "period": {"start": "2026-10-12", "end": "2026-10-18", "unit": "week", "length": 1},
        "sections": [
            {"id": "1", "title": "Streams", "subsections": [
                {"id": "1.1", "title": "Stellar streams", "category": 1, "count": True},
                {"id": "1.2", "title": "Empty theme", "category": 2, "count": True}]},
            {"id": "2", "title": "Science at large", "subsections": [
                {"id": "2.1", "title": "Science at large", "category": 3, "count": False}]}],
    }
    papers = {
        "arXiv:1": {"paper_id": "arXiv:1", "title": "A [new] stream", "url": "https://arxiv.org/abs/1",
                    "authors": ["Ada Lovelace", "Alan Turing"]},
        "arXiv:2": {"paper_id": "arXiv:2", "title": "Another stream", "url": "https://arxiv.org/abs/2",
                    "authors": ["Solo Author"]},
        "doi:x": {"paper_id": "doi:x", "title": "Superconductor", "url": "https://doi.org/x",
                  "authors": ["Marie Curie"], "journal": "Nature"},
    }
    selection = {"papers": papers, "subsections": {
        "1.1": {"count": 2, "summaries": [{"paper_id": "arXiv:1"}], "list": [{"paper_id": "arXiv:2"}]},
        "1.2": {"count": 0, "summaries": [], "list": []},
        "2.1": {"count": None, "summaries": [{"paper_id": "doi:x", "field": "Physics"}], "list": []},
    }}
    summaries = {"1.1": {"arXiv:1": "- **Context:** c"}, "2.1": {"doi:x": "Plain words."}}
    return resolved, selection, summaries


@pytest.mark.run
@pytest.mark.assemble
@pytest.mark.unit
def test_render(parts):
    """Headings, counts, lists, empty subsections and category-3 tags come from the data."""
    resolved, selection, summaries = parts
    news = {"doi:x": {"url": "https://news.example/a", "outlet": "Example News"}}
    text = assemble.render(resolved, selection, summaries, [{"text": "A note."}], news)
    assert text.startswith("# 📯 The Town Crier — this week\n*12 October 2026 → 18 October 2026*")
    assert "> - A note." in text
    assert "  - 1.1 Stellar streams (2)" in text
    assert "*2 papers released on this theme this week.*" in text
    assert "#### [A (new) stream](https://arxiv.org/abs/1)\n*Ada Lovelace et al.*" in text
    assert "- [Another stream](https://arxiv.org/abs/2) — Solo Author" in text
    assert "### 1.2 Empty theme\n*0 papers released on this theme this week.*\n\n*No new paper this period.*" in text
    assert "**Physics** · *Marie Curie* · *Nature* · [News: Example News](https://news.example/a)" in text


@pytest.mark.run
@pytest.mark.assemble
@pytest.mark.unit
def test_parse_summaries():
    """Bodies are split on paper markers."""
    text = "<!-- paper: arXiv:1 -->\nBody one.\n\n<!-- paper: doi:10.1/x -->\nBody two.\n"
    assert assemble.parse_summaries(text) == {"arXiv:1": "Body one.", "doi:10.1/x": "Body two."}
