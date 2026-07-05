"""CLI interface for GSAN."""

from typing import Annotated
from urllib.parse import urlsplit

import typer

from gsan.output.formatter import output_results
from gsan.processing.domain import process_domains

app = typer.Typer(add_completion=False)

DEFAULT_PORT = 443


def parse_domain(domain: str) -> tuple[str, int]:
    """Parse a ``host`` or ``host:port`` target into a ``(host, port)`` pair.

    Uses :func:`urllib.parse.urlsplit`, so bracketed IPv6 literals such as
    ``[2001:db8::1]:443`` and bare hostnames are handled without crashing on
    the extra colons. When no port is given, :data:`DEFAULT_PORT` is used.

    Args:
        domain: A target of the form ``host`` or ``host:port``.

    Returns:
        A ``(host, port)`` tuple with the host string and integer port.

    Raises:
        ValueError: If the host is missing or the port is not a valid integer
            in the range 0-65535.

    """
    split = urlsplit(f"//{domain}")
    host = split.hostname
    if not host:
        msg = f"Could not parse a host from {domain!r}"
        raise ValueError(msg)
    try:
        port = split.port
    except ValueError:
        msg = f"Invalid port in {domain!r}"
        raise ValueError(msg) from None
    return host, port if port is not None else DEFAULT_PORT


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
) -> None:
    """Check subdomains and IPs present in SSL certificates of specified domains.

    Raises:
        typer.BadParameter: If a target cannot be parsed into a host and a
            valid port.

    """
    try:
        parsed_domains = [parse_domain(domain) for domain in domains]
    except ValueError as error:
        raise typer.BadParameter(str(error)) from error

    print_results = not output_file
    results, failed_domains = process_domains(
        parsed_domains, timeout, max_workers, print_results
    )
    output_results(results, failed_domains, output_format, output_file)
