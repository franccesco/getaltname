"""Characterization tests for extraction correctness fixes.

Two defects in ``src/gsan/processing/extraction.py``:
- IP-address SANs crashed extraction, because a pyasn1 ``OctetString`` was
  passed straight to ``ipaddress.ip_address()`` instead of its raw bytes
  (fails identically on pyasn1 0.6.1 and 0.6.3);
- ``clean_domains`` returned ``list(set(...))``, so output ordering was
  non-deterministic across runs (bad for a recon tool whose output is diffed
  and piped). It now returns a sorted list.
"""

import datetime
import ipaddress

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509.oid import NameOID
from OpenSSL import crypto

from gsan.processing.extraction import clean_domains, extract_subdomains


def _cert_with_sans(sans: list[x509.GeneralName]) -> crypto.X509:
    """Build a self-signed pyOpenSSL cert carrying ``sans``.

    Args:
        sans: SubjectAlternativeName entries to embed.

    Returns:
        A loaded pyOpenSSL X.509 certificate.

    """
    key = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "example.com")])
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime(2020, 1, 1))
        .not_valid_after(datetime.datetime(2035, 1, 1))
        .add_extension(x509.SubjectAlternativeName(sans), critical=False)
        .sign(key, hashes.SHA256())
    )
    return crypto.load_certificate(
        crypto.FILETYPE_ASN1, cert.public_bytes(Encoding.DER)
    )


def test_ipv4_and_ipv6_sans_are_extracted() -> None:
    """IP-address SANs are decoded to their string form instead of crashing."""
    cert = _cert_with_sans(
        [
            x509.DNSName("a.example.com"),
            x509.IPAddress(ipaddress.ip_address("10.0.0.1")),
            x509.IPAddress(ipaddress.ip_address("2001:db8::1")),
        ]
    )
    assert sorted(extract_subdomains(cert)) == sorted(
        ["a.example.com", "10.0.0.1", "2001:db8::1"]
    )


def test_clean_domains_is_sorted_and_deduplicated() -> None:
    """clean_domains strips prefixes, dedupes, and returns a sorted list."""
    result = clean_domains(
        ["www.c.example.com", "*.a.example.com", "b.example.com", "a.example.com"]
    )
    assert result == ["a.example.com", "b.example.com", "c.example.com"]
