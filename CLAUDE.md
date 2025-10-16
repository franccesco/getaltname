# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GSAN (Get Subject Alternative Names) is a Python CLI security tool that extracts Subject Alternative Names from SSL certificates by connecting directly to HTTPS servers. It's used for reconnaissance to discover subdomains and virtual servers.

## Development Commands

### Installation & Building
```bash
# Install dependencies using uv
uv sync

# Build distribution
uv build
```

### Linting & Type Checking
```bash
# Run Ruff linter and auto-fix issues
uv run ruff check --fix

# Check formatting only (no fix)
uv run ruff check

# Format code
uv run ruff format

# Type checking with BasedPyright (strict mode)
uv run basedpyright
```

### Running the Tool
```bash
# Run with uv
uv run gsan example.com

# Run with options
uv run gsan example.com --timeout 5 --format json --output results.txt

# Multiple domains with custom port
uv run gsan example.com:8443 google.com microsoft.com

# After installation, can also run directly
gsan example.com
```

### Docker
```bash
# Build Docker image
docker build -t gsan .

# Run with Docker
docker run --rm -i gsan example.com
```

## Architecture

### Core Components

**src/gsan/main.py** - Single-file architecture containing all logic:

- **ASN.1 Parsing Classes** (`GeneralName`, `GeneralNames`): Custom pyasn1 structures for parsing the subjectAltName X.509 extension
- **Certificate Retrieval** (`get_certificate`): Creates SSL socket connections with unsigned certificate support (CERT_NONE) for testing internal/self-signed certificates
- **SAN Extraction** (`extract_subdomains`): Parses X.509 extensions to extract DNS names and IP addresses from subjectAltName field
- **Domain Processing** (`process_domain`, `process_domains`): ThreadPoolExecutor-based concurrent processing of multiple domains
- **CLI Interface** (`main`): Typer-based command with Rich output formatting

### Key Design Decisions

1. **Unsigned Certificate Support**: SSL context intentionally disables hostname verification and certificate validation to handle self-signed/internal certificates
2. **Concurrent Processing**: ThreadPoolExecutor enables parallel certificate fetching across multiple domains
3. **Domain Cleaning**: Automatically strips wildcard (`*.`) and `www.` prefixes to avoid duplicates
4. **Port Flexibility**: Supports `domain:port` format for non-standard HTTPS ports
5. **Output Modes**: Text (console), file output (for piping to tools like Nmap), and JSON format

### Dependencies

- **typer**: CLI framework
- **rich**: Terminal output formatting and progress bars
- **pyasn1**: ASN.1 parsing for X.509 certificate extensions
- **cryptography + pyOpenSSL**: Certificate handling
- **ThreadPoolExecutor**: Built-in concurrency

## Important Notes

- There are currently no tests in this codebase
- The tool intentionally accepts unsigned certificates (this is a security reconnaissance tool)
- Project uses `uv` for package management
- Ruff is configured with extensive linting rules (pycodestyle, pyflakes, isort, bugbear, pyupgrade, etc.)
- BasedPyright type checking is set to strict mode
- Python 3.14+ is required (specified in pyproject.toml)
