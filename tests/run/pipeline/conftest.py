"""Fixtures for the end-to-end run test."""

import pytest

JUDGMENTS = {
    "1.1": "arXiv:2610.10001 | y | 3 | research | - | new stream\n"
           "arXiv:2610.10002 | y | 3 | research | - | GD-1 gaps\n"
           "arXiv:2610.10003 | y | 2 | research | - | Pal 5 tails\n",
    "1.2": "arXiv:2610.10004 | y | 2 | research | - | halo merger\n",
    "2.1": "arXiv:2610.10005 | y | 3 | research | - | H0\narXiv:2610.10006 | y | 2 | research | - | neutrinos\n",
    "2.2": "arXiv:2610.10007 | y | 2 | research | - | quenching\n",
    "3.1": "doi:10.1038/test.1 | y | 3 | research | Physics | superconductor\n"
           "doi:10.1038/test.2 | y | 3 | research | Medicine & health | gene therapy\n",
}

CAT1 = ("- **Context:** Streams trace the halo.\n- **Aims:** Find a new stream.\n"
        "- **Methods:** A mixture model on Gaia DR3 stars.\n- **Results:** {result}\n"
        "- **Conclusions:** unknown.\n")

SUMMARIES = {
    "1.1": ("<!-- paper: arXiv:2610.10001 -->\n" + CAT1.format(result="A stream 12.5 kpc long, 35 pc wide, with 340 members.")
            + "\n<!-- paper: arXiv:2610.10002 -->\n" + CAT1.format(result="Subhalo masses are constrained.")
            + "\n<!-- paper: arXiv:2610.10003 -->\n" + CAT1.format(result="Tails traced over 25 degrees.")),
    "1.2": "<!-- paper: arXiv:2610.10004 -->\nThe stellar halo records an accretion event 8 Gyr ago.\n",
    "2.1": "<!-- paper: arXiv:2610.10005 -->\nTime delays give H0 = 71.2 +- 1.5 km/s/Mpc.\n",
    "2.2": "<!-- paper: arXiv:2610.10007 -->\nJWST spectra of 45 dwarf galaxies show quenching at z = 2.3.\n",
    "3.1": ("<!-- paper: doi:10.1038/test.1 -->\nA material loses all electrical resistance at 294 K.\n\n"
            "<!-- paper: doi:10.1038/test.2 -->\nHearing improved in 9 of 11 children.\n"),
}


@pytest.fixture
def judgments():
    """Judgment lines per subsection."""
    return JUDGMENTS


@pytest.fixture
def summaries():
    """Summary bodies per subsection."""
    return SUMMARIES
