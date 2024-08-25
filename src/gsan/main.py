import ssl
import json
import socket
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed

import typer
from rich import print as rprint
from rich.progress import track
from OpenSSL import crypto
from pyasn1.codec.der import decoder
from pyasn1.type import univ, char, namedtype, tag

app = typer.Typer(add_completion=False)


class GeneralName(univ.Choice):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType(
            "dNSName",
            char.IA5String().subtype(
                implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 2)
            ),
        ),
        namedtype.NamedType(
            "iPAddress",
            univ.OctetString().subtype(
                implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 7)
            ),
        ),
    )


class GeneralNames(univ.SequenceOf):
    componentType = GeneralName()


def allow_unsigned_certificate() -> ssl.SSLContext:
    """
    Creates and returns an SSL context that allows the use of unsigned certificates.
    """
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context


def clean_domains(domains: list) -> list:
    """
    Cleans a list of domains by removing any leading "*. " or "www." prefixes.
    """
    cleaned_domains = set(
        domain.removeprefix("*.").removeprefix("www.") for domain in domains
    )
    return list(cleaned_domains)


def get_certificate(
    hostname: str, port: int, timeout: float, context: ssl.SSLContext
) -> crypto.X509:
    """
    Retrieves the X.509 certificate from the specified hostname and port.
    """
    try:
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssl_sock:
                cert = ssl_sock.getpeercert(binary_form=True)
                x509 = crypto.load_certificate(crypto.FILETYPE_ASN1, cert)
                return x509
    except Exception as e:
        raise ValueError(f"SSL certificate retrieval failed for {hostname}: {str(e)}")


def extract_subdomains(x509: crypto.X509) -> list:
    """
    Extracts subdomains and IP addresses from the certificate's subjectAltName extension.
    """
    try:
        subdomains = []
        for extension_id in range(x509.get_extension_count()):
            ext = x509.get_extension(extension_id)
            ext_name = ext.get_short_name().decode("utf-8")
            if ext_name == "subjectAltName":
                ext_data = ext.get_data()
                decoded_dat = decoder.decode(ext_data, asn1Spec=GeneralNames())
                for name in decoded_dat:
                    if isinstance(name, GeneralNames):
                        for entry in range(len(name)):
                            component = name.getComponentByPosition(entry)
                            if "dNSName" in component:
                                subdomains.append(str(component.getComponent()))
                            elif "iPAddress" in component:
                                ip_address = str(
                                    ipaddress.ip_address(component.getComponent())
                                )
                                subdomains.append(ip_address)
        return subdomains
    except Exception as e:
        raise ValueError(f"Error extracting subdomains from the certificate: {str(e)}")


def process_domain(domain: str, port: int, timeout: float, context: ssl.SSLContext, print_results: bool):
    """
    Processes the domain by retrieving the certificate and extracting subdomains.
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


def process_domains(domains_with_ports, timeout, max_workers, print_results):
    context = allow_unsigned_certificate()
    results = {}
    failed_domains = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_domain, domain, port, timeout, context, print_results) for domain, port in domains_with_ports]

        for future in track(as_completed(futures), description="Checking certificates...", transient=True):
            result = future.result()
            if result is None:
                continue
            domain, subdomains, error = result
            if error:
                failed_domains.append(domain)
            else:
                results[domain] = subdomains

    return results, failed_domains


def output_results(results, failed_domains, output_format, output_file):
    if output_format == "json":
        output_data = {"results": results, "failed_domains": failed_domains}
        rprint(json.dumps(output_data, indent=2))
    elif output_file:
        with open(output_file, 'w') as f:
            for subdomains in results.values():
                f.writelines(f"{subdomain}\n" for subdomain in subdomains)


@app.command()
def main(
    domains: list[str] = typer.Argument(..., help="List of domains to check (e.g. 'example.com', '127.0.01:443')"),
    timeout: float = typer.Option(10.0, help="Connection timeout in seconds"),
    max_workers: int = typer.Option(10, help="Number of concurrent workers"),
    output_format: str = typer.Option("txt", "--format", help="Output format: 'txt' or 'json'"),
    output_file: str = typer.Option(None, "--output", help="File to write the results to")
):
    """
    Check the subdomains and IP addresses present in the certificates of the specified domains.
    """
    parsed_domains = []
    for domain in domains:
        if ':' in domain:
            host, port = domain.split(':')
            port = int(port)
        else:
            host = domain
            port = 443  # default port
        parsed_domains.append((host, port))

    print_results = output_file is None
    results, failed_domains = process_domains(parsed_domains, timeout, max_workers, print_results)
    output_results(results, failed_domains, output_format, output_file)


if __name__ == "__main__":
    app()
