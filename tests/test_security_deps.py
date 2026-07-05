"""Regression tests for the dream-2026-07-05.1 security dependency floors.

These pin the minimum fixed versions of the dependencies carrying the
advisories resolved by this change, and prove that the existing
pyOpenSSL + pyasn1 SAN-extraction path still parses a real certificate after
the bump (i.e. the security patch is behaviour-preserving).
"""

import datetime
from importlib.metadata import version

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID
from OpenSSL import crypto

from gsan.processing.extraction import extract_subdomains


def _version_tuple(dist: str) -> tuple[int, ...]:
    """Return the installed version of ``dist`` as a comparable int tuple.

    Args:
        dist: Distribution name to look up.

    Returns:
        The numeric release segments of the installed version.

    """
    release = version(dist).split("+")[0].split(".")
    parts: list[int] = []
    for segment in release:
        if segment.isdigit():
            parts.append(int(segment))
        else:
            break
    return tuple(parts)


def test_pyasn1_at_or_above_fixed_version() -> None:
    """Require pyasn1 >= 0.6.3 (CVE-2026-23490, CVE-2026-30922 decoder DoS)."""
    assert _version_tuple("pyasn1") >= (0, 6, 3)


def test_cryptography_at_or_above_fixed_version() -> None:
    """Require cryptography >= 46.0.7 (CVE-2026-26007, PYSEC-2026-35/-36)."""
    assert _version_tuple("cryptography") >= (46, 0, 7)


def test_pygments_at_or_above_fixed_version() -> None:
    """Require pygments >= 2.20.0 (CVE-2026-4539)."""
    assert _version_tuple("pygments") >= (2, 20, 0)


def _self_signed_der(sans: list[x509.GeneralName]) -> bytes:
    """Build a self-signed certificate with ``sans`` and return its DER bytes.

    Args:
        sans: Subject Alternative Name entries to embed.

    Returns:
        The DER-encoded certificate.

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
        .not_valid_after(datetime.datetime(2030, 1, 1))
        .add_extension(x509.SubjectAlternativeName(sans), critical=False)
        .sign(key, hashes.SHA256())
    )
    return cert.public_bytes(serialization.Encoding.DER)


def test_extraction_still_works_after_bump() -> None:
    """The pyOpenSSL + pyasn1 DNS-SAN path is unchanged by the version bump.

    Only DNS names are asserted here: extraction of *IP-address* SANs is
    broken in this code independently of the bump (it fails identically on
    pyasn1 0.6.1 and 0.6.3) and is fixed separately -- see the extraction
    correctness PR and the cryptography.x509 migration PR.
    """
    der = _self_signed_der(
        [
            x509.DNSName("a.example.com"),
            x509.DNSName("*.b.example.com"),
            x509.DNSName("www.c.example.com"),
        ]
    )
    certificate = crypto.load_certificate(crypto.FILETYPE_ASN1, der)
    assert sorted(extract_subdomains(certificate)) == sorted(
        ["a.example.com", "*.b.example.com", "www.c.example.com"]
    )
