"""Characterization test for deterministic domain cleaning.

``clean_domains`` returned ``list(set(...))``, so output ordering was
non-deterministic across runs (bad for a recon tool whose output is diffed
and piped). It now returns a sorted list. (IP-address SAN extraction, the
other correctness fix, is covered by ``test_extraction.py`` against the
cryptography.x509 path.)
"""

from gsan.processing.extraction import clean_domains


def test_clean_domains_is_sorted_and_deduplicated() -> None:
    """clean_domains strips prefixes, dedupes, and returns a sorted list."""
    result = clean_domains(
        ["www.c.example.com", "*.a.example.com", "b.example.com", "a.example.com"]
    )
    assert result == ["a.example.com", "b.example.com", "c.example.com"]
