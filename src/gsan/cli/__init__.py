"""Command-line interface for GSAN.

This module provides the CLI entry point using Typer for argument parsing
and Rich for formatted terminal output.
"""

from gsan.cli.interface import app, main

__all__ = ["app", "main"]
