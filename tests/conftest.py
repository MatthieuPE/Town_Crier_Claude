"""Cross-module fixtures and import paths."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))  # town_crier_fetch
sys.path.insert(0, str(ROOT / "plugins" / "town-crier" / "skills" / "cry" / "scripts"))  # towncrier


@pytest.fixture
def repo_root():
    """Repository root."""
    return ROOT


@pytest.fixture
def theme_yaml():
    """Minimal theme definition text, by name."""
    def make(name, arxiv=None, openalex=None, biorxiv=None, any_kw=None, exclude=None, authors=None):
        lines = [f"name: {name}", f"title: {name.replace('-', ' ').title()}",
                 "description: Test theme.", "databases:"]
        if arxiv:
            lines.append(f"  arxiv: [{', '.join(arxiv)}]")
        if biorxiv:
            lines.append(f"  biorxiv: [{', '.join(biorxiv)}]")
        if openalex:
            lines.append("  openalex:")
            lines.append("    journals:")
            for jname, issns in openalex.items():
                lines.append(f"      - {{name: {jname}, issn: [{', '.join(issns)}]}}")
        lines.append("keywords:")
        lines.append(f"  any: [{', '.join(repr(k) for k in (any_kw or []))}]")
        lines.append("  all: []")
        lines.append(f"  exclude: [{', '.join(repr(k) for k in (exclude or []))}]")
        lines.append(f"authors: [{', '.join(repr(a) for a in (authors or []))}]")
        return "\n".join(lines) + "\n"
    return make


@pytest.fixture
def plugin_repo(tmp_path, theme_yaml):
    """Fake repository with three theme definitions."""
    skills = tmp_path / "plugins" / "town-crier" / "skills"
    specs = {
        "streams": theme_yaml("streams", arxiv=["astro-ph.GA"], any_kw=["stellar stream*", "GD-1"]),
        "cosmo": theme_yaml("cosmo", arxiv=["astro-ph.CO"]),
        "science": theme_yaml("science", openalex={"Nature": ["0028-0836", "1476-4687"]}),
    }
    for name, text in specs.items():
        folder = skills / f"theme-{name}"
        folder.mkdir(parents=True)
        (folder / "theme.yaml").write_text(text, encoding="utf-8")
    return tmp_path
