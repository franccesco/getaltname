"""Characterization tests for ``output_results``.

Pin three behaviours corrected in this change:
- ``--format json --output FILE`` now writes the JSON to the file (previously
  the json branch printed to the console and never touched the file);
- machine-readable JSON is emitted verbatim, without Rich console markup
  mangling bracketed substrings;
- files are written with an explicit UTF-8 encoding.
"""

import json
from pathlib import Path

import pytest

from gsan.output.formatter import output_results

_RESULTS = {"example.com": ["a.example.com", "[bracketed].example.com"]}
_FAILED = ["down.example.com"]


def test_json_output_is_written_to_file(tmp_path: Path) -> None:
    """JSON format honours --output and writes parseable JSON to the file."""
    out = tmp_path / "results.json"
    output_results(_RESULTS, _FAILED, "json", str(out))

    assert out.exists(), "json + --output must write the file"
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded == {"results": _RESULTS, "failed_domains": _FAILED}


def test_json_to_stdout_is_plain_and_parseable(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """JSON to the console is emitted verbatim, brackets intact, and parses."""
    output_results(_RESULTS, _FAILED, "json", None)

    stdout = capsys.readouterr().out
    assert "[bracketed].example.com" in stdout, "Rich markup must not strip '[...]'"
    assert json.loads(stdout) == {"results": _RESULTS, "failed_domains": _FAILED}


def test_txt_output_written_to_file(tmp_path: Path) -> None:
    """Text format writes one subdomain per line to the file."""
    out = tmp_path / "results.txt"
    output_results(_RESULTS, _FAILED, "txt", str(out))

    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines == ["a.example.com", "[bracketed].example.com"]
