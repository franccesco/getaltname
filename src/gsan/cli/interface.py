"""CLI interface for GSAN."""

from typing import Annotated

import typer

from gsan.output.formatter import output_results
from gsan.processing.domain import process_domains

app = typer.Typer(add_completion=False)


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
