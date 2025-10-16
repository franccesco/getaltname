"""GSAN main module for extracting Subject Alternative Names from SSL certificates.

This module provides functionality to connect to HTTPS servers and extract
Subject Alternative Names (SANs) from their SSL certificates, which can reveal
subdomains and virtual hosts.
"""

from gsan.cli.interface import app

__all__ = ["app"]
