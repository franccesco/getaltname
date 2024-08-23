# GSAN - Get Subject Alternative Names

**GSAN** is a tool that can extract [Subject Alternative Names](https://en.wikipedia.org/wiki/Subject_Alternative_Name) (SAN) found in SSL Certificates directly from https servers which can provide you with DNS names (subdomains) or virtual servers.

It doesn't rely on Certificate Transparency logs, it connects directly to the server and extracts the SANs from the certificate, which can be specially useful when you're analyzing internal servers or self-signed certificates.

## Installation

Use pipx to avoid contaminating your system with a bunch of dependencies.
```bash
$ pip install --user gsan
```

You can also install and run it using Docker.
```bash
$ docker run --rm -it francc3sco/gsan <DOMAIN>
```

## Usage

Basic usage is just passing the domain of an HTTPS server to the tool, and it will return a list of subdomains found in the certificate.
```bash
$ gsan microsoft.com

microsoft.com [126]:
- microsoft.com
- successionplanning.microsoft.com
- explore-security.microsoft.com
...
- wwwbeta.microsoft.com
- gigjam.microsoft.com
- mspartnerira.microsoft.com
...
```

Alternatively, you can pass a text file with a list of domains to scan by using the `xargs` command.
```bash
$ cat domains.txt | xargs gsan

google.com [93]:
- google.fr
...
- google.com.au

amazon.com [37]:
- uedata.amazon.com
...
- origin-www.amazon.com.au

youtube.com [93]:
- google.fr
...
- google.com.au
```
