"""Domain extraction and cleaning utilities."""

from cryptography import x509
from cryptography.x509 import (
    DNSName,
    ExtensionNotFound,
    IPAddress,
    SubjectAlternativeName,
)


def clean_domains(domains: list[str]) -> list[str]:
    """Remove wildcard and www prefixes from domain names.

    Args:
        domains: List of domain names to clean.

    Returns:
        Sorted, deduplicated list of cleaned domain names.

    """
    cleaned_domains = {
        domain.removeprefix("*.").removeprefix("www.") for domain in domains
    }
    return sorted(cleaned_domains)


def extract_subdomains(certificate: x509.Certificate) -> list[str]:
    """Extract DNS names and IPs from certificate subjectAltName extension.

    Args:
        certificate: X.509 certificate to parse.

    Returns:
        List of domain names and IP addresses from the certificate.

    Raises:
        ValueError: If subdomain extraction from certificate fails.

    """
    try:
        san = certificate.extensions.get_extension_for_class(
            SubjectAlternativeName
        ).value
    except ExtensionNotFound:
        return []
    except Exception as e:
        msg = f"Error extracting subdomains from the certificate: {e!s}"
        raise ValueError(msg) from e
    dns_names = san.get_values_for_type(DNSName)
    ip_addresses = [str(ip) for ip in san.get_values_for_type(IPAddress)]
    return [*dns_names, *ip_addresses]
