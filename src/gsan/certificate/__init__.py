"""Certificate handling and ASN.1 models for X.509 parsing.

This module provides functionality to retrieve SSL certificates from remote
servers and parse their Subject Alternative Names (SANs) using ASN.1 structures.
"""

from gsan.certificate.models import GeneralName, GeneralNames
from gsan.certificate.retrieval import allow_unsigned_certificate, get_certificate

__all__ = [
    "GeneralName",
    "GeneralNames",
    "allow_unsigned_certificate",
    "get_certificate",
]
