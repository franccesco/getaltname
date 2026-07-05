"""Characterization test for escaping untrusted SANs in console output.

gsan targets untrusted / self-signed hosts, so certificate SAN values are
attacker-controlled. A SAN containing Rich markup metacharacters (square
brackets) must be printed literally, not interpreted as console markup and
silently dropped. This drives ``process_domain`` end-to-end with a stubbed
certificate carrying a bracketed SAN.
"""

import datetime
from collections.abc import Callable

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

from gsan.certificate.retrieval import allow_unsigned_certificate
from gsan.processing import domain as domain_module


def _cert_with_sans(dns_names: list[str]) -> x509.Certificate:
    """Build a self-signed cert carrying ``dns_names`` as SANs.

    Args:
        dns_names: DNS names to embed in the SubjectAlternativeName extension.

    Returns:
        A signed self-signed X.509 certificate.

    """
    key = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "test.example.com")])
    return (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime(2020, 1, 1))
        .not_valid_after(datetime.datetime(2035, 1, 1))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName(n) for n in dns_names]),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )


def _returns_cert(cert: x509.Certificate) -> Callable[..., x509.Certificate]:
    """Build a typed stand-in for get_certificate that always returns ``cert``.

    Args:
        cert: The certificate the stub should return.

    Returns:
        A callable matching get_certificate's shape.

    """

    def _stub(*_args: object, **_kwargs: object) -> x509.Certificate:
        return cert

    return _stub


def test_bracketed_san_is_printed_literally(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A SAN containing '[...]' appears verbatim rather than being stripped."""
    cert = _cert_with_sans(["a.example.com", "evil[bold].example.com"])
    monkeypatch.setattr(domain_module, "get_certificate", _returns_cert(cert))

    result = domain_module.process_domain(
        "test.example.com", 443, 1.0, allow_unsigned_certificate(), True
    )

    assert result is not None
    stdout = capsys.readouterr().out
    assert "evil[bold].example.com" in stdout, (
        "bracketed SAN must be escaped, not parsed as Rich markup"
    )
