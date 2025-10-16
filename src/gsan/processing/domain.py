"""Domain processing and batch operations."""

import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich import print as rprint
from rich.progress import track

from gsan.certificate.retrieval import allow_unsigned_certificate, get_certificate
from gsan.processing.extraction import clean_domains, extract_subdomains


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
