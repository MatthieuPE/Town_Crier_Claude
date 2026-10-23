"""End-to-end run through tc.py on a synthetic data folder."""

import json

import pytest

from towncrier import cli


def tc(*args):
    """Run one tc.py command."""
    return cli.main([str(a) for a in args])


@pytest.mark.run
@pytest.mark.integration
def test_full_run(tmp_path, user_config, data_dir, judgments, summaries, capsys):
    """resolve -> load -> judge -> finalize -> cut -> summaries -> assemble -> check."""
    runs = tmp_path / "runs"
    assert tc("resolve", "--config", user_config, "--run-date", "2026-10-19", "--out", runs,
              "--data-dir", data_dir) == 0
    run = runs / "2026-10-12_2026-10-18"
    assert tc("load", "--run", run) == 0
    for sid, text in judgments.items():
        path = tmp_path / f"j{sid}.txt"
        path.write_text(text)
        assert tc("judge", "--run", run, "--sub", sid, "--file", path) == 0
    assert tc("finalize", "--run", run) == 0
    sel = json.loads((run / "selection.json").read_text())
    assert sel["subsections"]["1.1"]["count"] == 3
    assert [j["paper_id"] for j in sel["subsections"]["2.1"]["summaries"]] == ["arXiv:2610.10005"]

    full = tmp_path / "paper.txt"
    full.write_text("ABSTRACT\nWe detect a stream.\n3. RESULTS\nThe stream is 35 pc wide.\n")
    assert tc("cut", "--run", run, "--paper", "arXiv:2610.10001", "--input", full) == 0
    (run / "summaries").mkdir()
    for sid, text in summaries.items():
        (run / "summaries" / f"{sid}.md").write_text(text)
    assert tc("news", "--run", run, "--paper", "doi:10.1038/test.1", "--url", "https://news.example/sc",
              "--outlet", "Example News") == 0
    assert tc("assemble", "--run", run) == 0
    capsys.readouterr()
    assert tc("check", "--run", run) == 0, capsys.readouterr().out

    digest = (run / "town-crier_2026-10-12_2026-10-18.md").read_text()
    assert "### 1.1 Stellar streams\n*3 papers released on this theme this week.*" in digest
    assert "[News: Example News](https://news.example/sc)" in digest

    # an invented number is caught
    path = run / "summaries" / "1.1.md"
    path.write_text(path.read_text().replace("12.5 kpc", "13.7 kpc"))
    assert tc("check", "--run", run) == 1
    assert "number 13.7 is not in the paper's text" in capsys.readouterr().out
    # a quote not in the paper does not help
    tc("verify", "--run", run, "--paper", "arXiv:2610.10001", "--number", "13.7", "--quote", "a 13.7 kpc stream")
    assert tc("check", "--run", run) == 1
    # writing 'unknown' fixes it
    path.write_text(path.read_text().replace("13.7 kpc", "unknown length"))
    assert tc("check", "--run", run) == 0

    # citations of other works are refused
    path.write_text(path.read_text().replace("Streams trace the halo.", "Streams trace the halo (Smith et al. 2020)."))
    capsys.readouterr()
    assert tc("check", "--run", run) == 1
    assert "must not cite other works" in capsys.readouterr().out


@pytest.mark.run
@pytest.mark.integration
def test_default_config_stops_on_placeholders(tmp_path, data_dir, capsys):
    """The default configuration reports its placeholders and creates no run folder."""
    assert tc("resolve", "--run-date", "2026-10-19", "--out", tmp_path / "runs", "--data-dir", data_dir) == 2
    out = capsys.readouterr().out
    assert "placeholder to fill" in out
    assert not (tmp_path / "runs").exists()


@pytest.mark.run
@pytest.mark.integration
def test_fallback_import(tmp_path, user_config, capsys):
    """Without data, papers found by search are imported; counts become unknown."""
    empty = tmp_path / "nodata"
    empty.mkdir()
    runs = tmp_path / "runs"
    assert tc("resolve", "--config", user_config, "--run-date", "2026-10-19", "--out", runs,
              "--data-dir", empty) == 0
    run = runs / "2026-10-12_2026-10-18"
    assert tc("load", "--run", run) == 3
    found = tmp_path / "found.jsonl"
    found.write_text(json.dumps({"paper_id": "arXiv:2610.20001", "title": "Found by search",
                                 "url": "https://arxiv.org/abs/2610.20001", "found_for": ["1.1"],
                                 "abstract": "A stream with 77 members."}) + "\n")
    assert tc("import", "--run", run, "--file", found, "--reason", "data branch unreachable") == 0
    jfile = tmp_path / "j.txt"
    jfile.write_text("arXiv:2610.20001 | y | 3 | research | - | stream\n")
    assert tc("judge", "--run", run, "--sub", "1.1", "--file", jfile) == 0
    assert tc("finalize", "--run", run) == 0
    sel = json.loads((run / "selection.json").read_text())
    assert sel["subsections"]["1.1"]["count"] is None and sel["subsections"]["1.1"]["search_only"]
    (run / "summaries").mkdir()
    (run / "summaries" / "1.1.md").write_text(
        "<!-- paper: arXiv:2610.20001 -->\n" + "\n".join(
            f"- **{b}:** unknown." if b != "Results" else "- **Results:** 77 members."
            for b in ("Context", "Aims", "Methods", "Results", "Conclusions")) + "\n")
    assert tc("assemble", "--run", run) == 0
    capsys.readouterr()
    assert tc("check", "--run", run) == 0, capsys.readouterr().out
    digest = (run / "town-crier_2026-10-12_2026-10-18.md").read_text()
    assert "Number of papers released on this theme this week: unknown." in digest
    assert "papers found by search (data branch unreachable)" in digest
