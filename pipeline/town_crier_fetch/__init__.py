"""Daily fetch of new papers for the Town Crier digest.

Runs in a GitHub Action. Queries arXiv, bioRxiv/medRxiv and OpenAlex for
the databases declared by the theme definitions, and stores each paper
once, under the day it was first seen.
"""

__version__ = "0.1.0"
