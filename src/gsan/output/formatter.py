"""Output formatting for results."""

import json

from rich import print as rprint


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
