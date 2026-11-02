"""Tests of judgments and the final selection."""

import pytest

from towncrier import selection


@pytest.mark.run
@pytest.mark.selection
@pytest.mark.unit
def test_parse_lines():
    """Both short and full lines parse; comments are skipped."""
    js = selection.parse("# 1.1\narXiv:1 | y | 3 | research | - | new stream\narXiv:2 | n\n")
    assert js[0] == selection.Judgment("arXiv:1", True, 3, "research", None, "new stream")
    assert js[1].on_theme is False and js[1].score == 0


@pytest.mark.run
@pytest.mark.selection
@pytest.mark.unit
def test_parse_rejects_missing_score():
    """On-theme lines need a score."""
    with pytest.raises(ValueError, match="score"):
        selection.parse("arXiv:1 | y\n")


@pytest.mark.run
@pytest.mark.selection
@pytest.mark.unit
def test_validate_requires_exact_coverage():
    """Every candidate judged once; category 3 needs a field."""
    js = selection.parse("a | y | 2 | research | - |\nx | n\n")
    errors = selection.validate(js, ["a", "b"], category=3)
    assert any("not judged: b" in e for e in errors)
    assert any("not in this subsection" in e for e in errors)
    assert any("field tag" in e for e in errors)


def sub(sid, cat, n, **kw):
    """Resolved subsection stub."""
    return {"id": sid, "category": cat, "n_papers": n, "theme": "t", "title": sid,
            "count": cat != 3, "list_others": True, **kw}


@pytest.mark.run
@pytest.mark.selection
@pytest.mark.unit
def test_finalize_dedupes_and_lists():
    """Summaries in reading order; lists exclude summarized and already listed papers."""
    resolved = {"period": {}, "sections": [{"id": "1", "subsections": [sub("1.1", 1, 1), sub("1.2", 1, 2)]},
                                           {"id": "2", "subsections": [sub("2.1", 2, 1)]}]}
    J = selection.Judgment
    judged = {
        "1.1": [J("p1", True, 3), J("p2", True, 2), J("p3", True, 1), J("p9", False)],
        "1.2": [J("p1", True, 3), J("p2", True, 3), J("p4", True, 1)],
        "2.1": [J("p2", True, 3), J("p5", True, 2, kind="review"), J("p6", True, 1)],
    }
    records = {p: {"paper_id": p, "first_seen": "2026-10-13"} for p in ("p1", "p2", "p3", "p4", "p5", "p6")}
    sel = selection.finalize(resolved, {k: [j.paper_id for j in v] for k, v in judged.items()}, judged, records)
    s = sel["subsections"]
    assert [j["paper_id"] for j in s["1.1"]["summaries"]] == ["p1"]
    assert [j["paper_id"] for j in s["1.2"]["summaries"]] == ["p2", "p4"]
    assert [j["paper_id"] for j in s["2.1"]["summaries"]] == ["p6"]      # p2 taken, p5 is a review
    assert [j["paper_id"] for j in s["1.1"]["list"]] == ["p3"]          # p2 summarized elsewhere
    assert s["1.2"]["list"] == []
    assert s["1.1"]["count"] == 3 and s["2.1"]["count"] == 3


@pytest.mark.run
@pytest.mark.selection
@pytest.mark.unit
def test_category_3_fields():
    """Excluded fields are skipped; one paper per field."""
    resolved = {"period": {}, "sections": [{"id": "1", "subsections": [
        sub("1.1", 3, 3, one_per_field=True, exclude_fields=["Astronomy & astrophysics"])]}]}
    J = selection.Judgment
    judged = {"1.1": [J("a", True, 3, field="Astronomy & astrophysics"), J("b", True, 3, field="Biology"),
                      J("c", True, 2, field="Biology"), J("d", True, 1, field="Physics")]}
    records = {p: {"paper_id": p} for p in "abcd"}
    sel = selection.finalize(resolved, {"1.1": list("abcd")}, judged, records)
    assert [j["paper_id"] for j in sel["subsections"]["1.1"]["summaries"]] == ["b", "d"]
