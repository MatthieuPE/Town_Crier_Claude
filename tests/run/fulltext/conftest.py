"""Fixtures for the fulltext tests."""

import json

import pytest

PAPER = """DRAFT VERSION OCTOBER 23, 2026
A Synthetic Paper on Streams
ABSTRACT
We study a synthetic stream with 340 members.
1. INTRODUCTION
Streams are useful. This introduction is long and not needed.
2 SMITH, JONES, & LEE
2. DATA AND METHODS
We select stars brighter than G = 19.5 mag from
∼10
4
candidates, using a mixture model.
f
pre
2.1. Membership
Members are kept above a probability of 0.8.
3. RESULTS
The stream is 12.5 kpc long. Its width is 35 pc, which con-
strains the progenitor mass.
4 SMITH, JONES, & LEE
More results on the stream.
4. DISCUSSION
We discuss caveats.
5. CONCLUSIONS
The stream is a cold globular-cluster stream.
ACKNOWLEDGEMENTS
We thank the referee.
REFERENCES
Bonaca, A. 2025, ARA&A
"""


@pytest.fixture
def paper_text():
    """Synthetic PDF-like paper text with running heads and debris."""
    return PAPER


@pytest.fixture
def tool_result_file(tmp_path):
    """Paper saved as an MCP tool result (JSON list of text blocks)."""
    path = tmp_path / "result.json"
    path.write_text(json.dumps([{"type": "text", "text": PAPER}]))
    return path
