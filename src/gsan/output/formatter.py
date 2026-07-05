"""Output formatting for results."""

import json


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
        json_output = json.dumps(output_data, indent=2)
        # Machine-readable output must bypass Rich: its console markup would
        # strip bracketed substrings (e.g. a SAN like "[::1]") and its
        # soft-wrapping could inject newlines into long lines -- either would
        # corrupt the emitted JSON. Honour --output for JSON too (previously
        # the file was never written for the json format).
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"{json_output}\n")
        else:
            print(json_output)
    elif output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            for subdomains in results.values():
                f.writelines(f"{subdomain}\n" for subdomain in subdomains)
