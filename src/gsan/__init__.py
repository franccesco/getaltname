"""GSAN - Get Subject Alternative Names from SSL certificates.

GSAN is a Python CLI security tool that extracts Subject Alternative Names
from SSL certificates by connecting directly to HTTPS servers. It's used for
reconnaissance to discover subdomains and virtual servers.
"""

from gsan.certificate import allow_unsigned_certificate, get_certificate
from gsan.cli import app, main
from gsan.output import output_results
from gsan.processing import (
    clean_domains,
    extract_subdomains,
    process_domain,
    process_domains,
)

__all__ = [
    "allow_unsigned_certificate",
    "app",
    "clean_domains",
    "extract_subdomains",
    "get_certificate",
    "main",
    "output_results",
    "process_domain",
    "process_domains",
]
