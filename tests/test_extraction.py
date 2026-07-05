"""Characterization tests for SAN extraction via cryptography.x509.

These synthesize self-signed certificates carrying known Subject Alternative
Names and assert that ``extract_subdomains`` returns exactly those names,
pinning the behaviour of the migrated certificate-parsing path (which replaced
the pyOpenSSL + pyasn1 implementation).
"""

import datetime
import ipaddress

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509 import DNSName, GeneralName, IPAddress, SubjectAlternativeName
from cryptography.x509.oid import NameOID

from gsan.processing.extraction import clean_domains, extract_subdomains


def _build_certificate(sans: list[GeneralName] | None) -> x509.Certificate:
    """Build a self-signed certificate, optionally with a SAN extension.

    Args:
        sans: Subject Alternative Name entries, or None to omit the extension.

    Returns:
        A signed self-signed X.509 certificate.

    """
    key = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "example.com")])
    builder = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime(2020, 1, 1))
        .not_valid_after(datetime.datetime(2030, 1, 1))
    )
    if sans is not None:
        builder = builder.add_extension(SubjectAlternativeName(sans), critical=False)
    return builder.sign(key, hashes.SHA256())


def _roundtrip(certificate: x509.Certificate) -> x509.Certificate:
    """Serialize to DER and re-load, mirroring the retrieval path.

    Args:
        certificate: The certificate to serialize and reload.

    Returns:
        The certificate reloaded from its DER encoding.

    """
    der = certificate.public_bytes(serialization.Encoding.DER)
    return x509.load_der_x509_certificate(der)


def test_extract_dns_and_ip_names() -> None:
    """DNS names and IP addresses are extracted as strings."""
    certificate = _roundtrip(
        _build_certificate(
            [
                DNSName("a.example.com"),
                DNSName("*.b.example.com"),
                DNSName("www.c.example.com"),
                IPAddress(ipaddress.ip_address("10.0.0.1")),
                IPAddress(ipaddress.ip_address("2001:db8::1")),
            ]
        )
    )
    assert sorted(extract_subdomains(certificate)) == sorted(
        [
            "a.example.com",
            "*.b.example.com",
            "www.c.example.com",
            "10.0.0.1",
            "2001:db8::1",
        ]
    )


def test_extract_with_cleaning_strips_prefixes() -> None:
    """clean_domains strips the '*.' and 'www.' prefixes and deduplicates."""
    certificate = _roundtrip(
        _build_certificate(
            [
                DNSName("a.example.com"),
                DNSName("*.b.example.com"),
                DNSName("www.c.example.com"),
                IPAddress(ipaddress.ip_address("10.0.0.1")),
            ]
        )
    )
    assert sorted(clean_domains(extract_subdomains(certificate))) == [
        "10.0.0.1",
        "a.example.com",
        "b.example.com",
        "c.example.com",
    ]


def test_extract_without_san_extension_returns_empty() -> None:
    """A certificate lacking a SAN extension yields an empty list."""
    certificate = _roundtrip(_build_certificate(None))
    assert extract_subdomains(certificate) == []
