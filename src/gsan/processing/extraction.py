"""Domain extraction and cleaning utilities."""

import ipaddress

from OpenSSL import crypto
from pyasn1.codec.der import decoder

from gsan.certificate.models import GeneralNames


def clean_domains(domains: list[str]) -> list[str]:
    """Remove wildcard and www prefixes from domain names.

    Args:
        domains: List of domain names to clean.

    Returns:
        Deduplicated list of cleaned domain names.

    """
    cleaned_domains = {
        domain.removeprefix("*.").removeprefix("www.") for domain in domains
    }
    return list(cleaned_domains)


def extract_subdomains(x509: crypto.X509) -> list[str]:
    """Extract DNS names and IPs from certificate subjectAltName extension.

    Args:
        x509: X.509 certificate to parse.

    Returns:
        List of domain names and IP addresses from the certificate.

    Raises:
        ValueError: If subdomain extraction from certificate fails.

    """
    try:
        subdomains: list[str] = []
        for extension_id in range(x509.get_extension_count()):
            ext = x509.get_extension(extension_id)
            ext_name = ext.get_short_name().decode("utf-8")
            if ext_name == "subjectAltName":
                ext_data = ext.get_data()
                decoded_dat = decoder.decode(ext_data, asn1Spec=GeneralNames())  # type: ignore[arg-type]
                for name in decoded_dat:  # type: ignore[assignment]
                    if isinstance(name, GeneralNames):
                        for entry in range(len(name)):
                            component = name.getComponentByPosition(entry)  # type: ignore[attr-defined]
                            if "dNSName" in component:
                                subdomains.append(str(component.getComponent()))  # type: ignore[attr-defined]
                            elif "iPAddress" in component:
                                ip_address = str(
                                    ipaddress.ip_address(component.getComponent())  # type: ignore[attr-defined]
                                )
                                subdomains.append(ip_address)
        return subdomains
    except Exception as e:
        msg = f"Error extracting subdomains from the certificate: {e!s}"
        raise ValueError(msg) from e
