"""Fixtures shared by the run-tool tests: a synthetic data folder and configuration."""

import datetime as dt
import json

import pytest

from town_crier_fetch import store


def arxiv_rec(pid, day, cats, title, abstract, authors=("Ada Lovelace", "Alan Turing")):
    """Synthetic arXiv record."""
    return {"paper_id": f"arXiv:{pid}", "source": "arxiv", "title": title, "abstract": abstract,
            "authors": list(authors), "url": f"https://arxiv.org/abs/{pid}",
            "html_url": f"https://arxiv.org/html/{pid}", "doi": None, "categories": list(cats),
            "primary_category": cats[0], "comment": None, "journal_ref": None, "published": day,
            "updated": day, "version": 1, "first_seen": day}


def journal_rec(n, day, title, abstract):
    """Synthetic OpenAlex record (Nature)."""
    return {"paper_id": f"doi:10.1038/test.{n}", "source": "openalex", "title": title,
            "abstract": abstract, "authors": ["Marie Curie", "Pierre Curie"],
            "url": f"https://doi.org/10.1038/test.{n}", "html_url": None, "doi": f"10.1038/test.{n}",
            "categories": [], "primary_category": None, "comment": None, "journal_ref": "Nature",
            "journal": "Nature", "issn": ["0028-0836", "1476-4687"], "type": "article",
            "published": day, "updated": day, "version": 1, "first_seen": day}


@pytest.fixture
def records():
    """Papers of the week 2026-10-12 to 2026-10-18, plus one outside it."""
    return [
        arxiv_rec("2610.10001", "2026-10-13", ["astro-ph.GA"], "A new stellar stream in Gaia DR3",
                  "We detect a thin stellar stream 12.5 kpc long with 340 members."),
        arxiv_rec("2610.10002", "2026-10-14", ["astro-ph.GA"], "Gaps in GD-1 from subhaloes",
                  "We model gaps in GD-1 and constrain subhalo masses below 1e7 Msun."),
        arxiv_rec("2610.10003", "2026-10-15", ["astro-ph.SR", "astro-ph.GA"], "Tidal tails of Pal 5",
                  "Tidal tails of Pal 5 traced over 25 degrees."),
        arxiv_rec("2610.10004", "2026-10-16", ["astro-ph.GA"], "Merger history of the Milky Way halo",
                  "The stellar halo shows an accretion event 8 Gyr ago."),
        arxiv_rec("2610.10005", "2026-10-16", ["astro-ph.CO"], "Hubble constant from lensing",
                  "We measure H0 = 71.2 +- 1.5 km/s/Mpc from time delays."),
        arxiv_rec("2610.10006", "2026-10-17", ["astro-ph.CO"], "Neutrino mass bound",
                  "We find a sum of neutrino masses below 0.072 eV."),
        arxiv_rec("2610.10007", "2026-10-17", ["astro-ph.GA"], "Quenching in dwarf galaxies with JWST",
                  "JWST spectra of 45 dwarf galaxies show quenching at z = 2.3."),
        arxiv_rec("2610.09999", "2026-10-10", ["astro-ph.GA"], "An old stellar stream paper",
                  "Outside the period."),
        journal_rec(1, "2026-10-14", "A room-temperature superconductor confirmed",
                    "Resistance vanishes at 294 K in a hydride at 2 GPa."),
        journal_rec(2, "2026-10-15", "Gene therapy restores hearing",
                    "Hearing improved in 9 of 11 children."),
    ]


@pytest.fixture
def data_dir(tmp_path, records):
    """Data folder as written by the daily fetch."""
    folder = tmp_path / "data"
    index = store.new_index()
    for db in ("arxiv", "openalex"):
        recs = {r["paper_id"]: r for r in records if r["source"] == db}
        days = store.write_records(folder, db, recs, dt.date(2026, 10, 19))
        run_days = [(dt.date(2026, 10, 9) + dt.timedelta(days=i)).isoformat() for i in range(11)]
        index["databases"][db] = {"files": days, "run_days": run_days, "coverage": {}}
    index["databases"]["arxiv"]["coverage"] = {c: "2026-10-01" for c in
                                               ("astro-ph.GA", "astro-ph.SR", "astro-ph.CO")}
    index["databases"]["openalex"]["coverage"] = {i: "2026-10-01" for i in
                                                  ("0028-0836", "1476-4687", "0036-8075", "1095-9203",
                                                   "0092-8674", "1097-4172", "0027-8424", "1091-6490",
                                                   "0031-9007", "1079-7114", "0028-4793", "1533-4406")}
    index["last_run_day"] = "2026-10-19"
    (folder / "index.json").write_text(json.dumps(index))
    return folder


CONFIG = """
data:
  repository: test/repo
period:
  length: 1
  unit: week
sections:
  - title: Stellar streams
    subsections:
      - {theme: stellar-streams, category: 1}
      - {theme: galactic-archaeology, category: 2}
  - title: Next door
    subsections:
      - {theme: cosmology, category: 2}
      - {theme: galaxy-formation, category: 2}
  - title: Science at large
    subsections:
      - {theme: science-at-large, category: 3, exclude_fields: [Astronomy & astrophysics]}
"""


@pytest.fixture
def user_config(tmp_path):
    """User configuration file using the plugin's themes."""
    path = tmp_path / "me.yaml"
    path.write_text(CONFIG)
    return path


@pytest.fixture
def run_date():
    """Monday after the test week."""
    return dt.date(2026, 10, 19)
