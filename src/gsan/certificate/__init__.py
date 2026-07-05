"""Certificate handling for X.509 parsing.

This module provides functionality to retrieve SSL certificates from remote
servers and parse their Subject Alternative Names (SANs).
"""

from gsan.certificate.retrieval import allow_unsigned_certificate, get_certificate

__all__ = [
    "allow_unsigned_certificate",
    "get_certificate",
]
