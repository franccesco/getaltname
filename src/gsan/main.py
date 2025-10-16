"""GSAN main module for extracting Subject Alternative Names from SSL certificates.

This module provides functionality to connect to HTTPS servers and extract
Subject Alternative Names (SANs) from their SSL certificates, which can reveal
subdomains and virtual hosts.
"""

import ipaddress
import json
import socket
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Annotated

import typer
from OpenSSL import crypto
from pyasn1.codec.der import decoder
from pyasn1.type import char, namedtype, tag, univ
from rich import print as rprint
from rich.progress import track

app = typer.Typer(add_completion=False)


class GeneralName(univ.Choice):
    """ASN.1 structure for a single Subject Alternative Name entry (DNS or IP)."""

    componentType = namedtype.NamedTypes(  # type: ignore[assignment]
        namedtype.NamedType(
            "dNSName",
            char.IA5String().subtype(  # type: ignore[attr-defined]
                implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 2)
            ),
        ),
        namedtype.NamedType(
            "iPAddress",
            univ.OctetString().subtype(  # type: ignore[attr-defined]
                implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 7)
            ),
        ),
    )


class GeneralNames(univ.SequenceOf):
    """ASN.1 structure for a sequence of Subject Alternative Name entries."""

    componentType = GeneralName()  # type: ignore[assignment]


def allow_unsigned_certificate() -> ssl.SSLContext:
    """Create an SSL context that allows unsigned certificates.

    Returns:
        SSL context configured to accept self-signed and unsigned certificates.

    """
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context


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


def get_certificate(
    hostname: str, port: int, timeout: float, context: ssl.SSLContext
) -> crypto.X509:
    """Retrieve X.509 certificate from a hostname and port.

    Args:
        hostname: Target hostname or IP address.
        port: Target port number.
        timeout: Connection timeout in seconds.
        context: SSL context for certificate validation.

    Returns:
        X.509 certificate object.

    Raises:
        ValueError: If certificate retrieval fails or no certificate is received.

    """
    try:
        with (
            socket.create_connection((hostname, port), timeout=timeout) as sock,
            context.wrap_socket(sock, server_hostname=hostname) as ssl_sock,
        ):
            cert = ssl_sock.getpeercert(binary_form=True)
            if cert is None:
                msg = f"No certificate received from {hostname}"
                raise ValueError(msg)
            x509 = crypto.load_certificate(crypto.FILETYPE_ASN1, cert)
            return x509
    except Exception as e:
        msg = f"SSL certificate retrieval failed for {hostname}: {e!s}"
        raise ValueError(msg) from e


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


def process_domain(
    domain: str, port: int, timeout: float, context: ssl.SSLContext, print_results: bool
) -> tuple[str, list[str], None] | tuple[str, None, str] | None:
    """Process a single domain to retrieve and extract certificate SANs.

    Args:
        domain: Domain name or IP address to process.
        port: Port number to connect to.
        timeout: Connection timeout in seconds.
        context: SSL context for certificate validation.
        print_results: Whether to print results to console.

    Returns:
        Tuple of (domain, subdomains, None) on success,
        (domain, None, error_string) on failure,
        or None if no interesting subdomains found.

    """
    try:
        x509 = get_certificate(domain, port, timeout, context)
        subdomains = clean_domains(extract_subdomains(x509))

        # Skip if no subdomains are found
        if not subdomains:
            return None

        # Skip if only one subdomain exists and it is equal to the main domain
        if len(subdomains) == 1 and subdomains[0] == domain:
            return None

        if print_results:
            rprint(f"\n[bold green]{domain}[/bold green] [{len(subdomains)}]:")
            for subdomain in subdomains:
                rprint(f"- {subdomain}")

        return domain, subdomains, None
    except Exception as e:
        return domain, None, str(e)


def process_domains(
    domains_with_ports: list[tuple[str, int]],
    timeout: float,
    max_workers: int,
    print_results: bool,
) -> tuple[dict[str, list[str]], list[str]]:
    """Process multiple domains concurrently to extract SANs from certificates.

    Args:
        domains_with_ports: List of (domain, port) tuples to process.
        timeout: Connection timeout in seconds.
        max_workers: Number of concurrent workers for parallel processing.
        print_results: Whether to print results to console.

    Returns:
        Tuple of (results_dict, failed_domains_list) where results_dict maps
        domains to their extracted subdomains.

    """
    context = allow_unsigned_certificate()
    results: dict[str, list[str]] = {}
    failed_domains: list[str] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                process_domain, domain, port, timeout, context, print_results
            )
            for domain, port in domains_with_ports
        ]

        for future in track(
            as_completed(futures),
            description="Checking certificates...",
            transient=True,
        ):
            result = future.result()
            if result is None:
                continue
            domain, subdomains, error = result
            if error:
                failed_domains.append(domain)
            elif subdomains is not None:
                results[domain] = subdomains

    return results, failed_domains


def output_results(
    results: dict[str, list[str]],
    failed_domains: list[str],
    output_format: str,
    output_file: str | None,
) -> None:
    """Output processing results in the specified format.

    Args:
        results: Dictionary mapping domains to their extracted subdomains.
        failed_domains: List of domains that failed to process.
        output_format: Output format ('txt' or 'json').
        output_file: Optional file path to write results to.

    """
    if output_format == "json":
        output_data = {"results": results, "failed_domains": failed_domains}
        rprint(json.dumps(output_data, indent=2))
    elif output_file:
        with open(output_file, "w") as f:
            for subdomains in results.values():
                f.writelines(f"{subdomain}\n" for subdomain in subdomains)


@app.command()
def main(
    domains: Annotated[
        list[str],
        typer.Argument(
            help="List of domains to check (e.g. 'example.com', '127.0.01:443')"
        ),
    ],
    timeout: Annotated[
        float,
        typer.Option(help="Connection timeout in seconds"),
    ] = 10.0,
    max_workers: Annotated[
        int,
        typer.Option(help="Number of concurrent workers"),
    ] = 10,
    output_format: Annotated[
        str,
        typer.Option("--format", help="Output format: 'txt' or 'json'"),
    ] = "txt",
    output_file: Annotated[
        str | None,
        typer.Option("--output", help="File to write the results to"),
    ] = None,
):
    """Check subdomains and IPs present in SSL certificates of specified domains."""
    parsed_domains: list[tuple[str, int]] = []
    for domain in domains:
        if ":" in domain:
            host, port_str = domain.split(":")
            port = int(port_str)
        else:
            host = domain
            port = 443  # default port
        parsed_domains.append((host, port))

    print_results = not output_file
    results, failed_domains = process_domains(
        parsed_domains, timeout, max_workers, print_results
    )
    output_results(results, failed_domains, output_format, output_file)


if __name__ == "__main__":
    app()
