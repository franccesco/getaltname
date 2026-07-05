"""Characterization tests for host:port target parsing.

The previous ``domain.split(":")`` + unguarded ``int(...)`` crashed with an
unhandled traceback on IPv6 literals and malformed ports. ``parse_domain``
handles bracketed IPv6 and reports bad input as a ``typer.BadParameter``.
"""

import pytest
from typer.testing import CliRunner

from gsan.cli.interface import DEFAULT_PORT, app, parse_domain


def test_host_only_uses_default_port() -> None:
    """A bare host resolves to the default HTTPS port."""
    assert parse_domain("example.com") == ("example.com", DEFAULT_PORT)


def test_host_with_explicit_port() -> None:
    """An explicit port is parsed as an integer."""
    assert parse_domain("example.com:8443") == ("example.com", 8443)


def test_bracketed_ipv6_without_port() -> None:
    """A bracketed IPv6 literal parses without crashing on inner colons."""
    assert parse_domain("[2001:db8::1]") == ("2001:db8::1", DEFAULT_PORT)


def test_bracketed_ipv6_with_port() -> None:
    """A bracketed IPv6 literal with a port keeps host and port separate."""
    assert parse_domain("[2001:db8::1]:8443") == ("2001:db8::1", 8443)


def test_non_numeric_port_raises_valueerror() -> None:
    """A non-numeric port is rejected rather than crashing on int()."""
    with pytest.raises(ValueError, match="Invalid port"):
        parse_domain("example.com:https")


def test_out_of_range_port_raises_valueerror() -> None:
    """A port outside 0-65535 is rejected."""
    with pytest.raises(ValueError, match="Invalid port"):
        parse_domain("example.com:99999")


def test_cli_reports_bad_port_without_traceback() -> None:
    """Invalid input exits non-zero via BadParameter, not an uncaught crash."""
    result = CliRunner().invoke(app, ["example.com:https"])
    assert result.exit_code != 0
    assert result.exception is None or isinstance(result.exception, SystemExit)
