# GSAN - Get Subject Alternative Names

**GSAN** is a tool that can extract [Subject Alternative Names](https://en.wikipedia.org/wiki/Subject_Alternative_Name) (SAN) found in SSL Certificates directly from https servers which can provide you with DNS names (subdomains) or virtual servers.

It doesn't rely on Certificate Transparency logs, it connects directly to the server and extracts the SANs from the certificate, which can be specially useful when you're analyzing internal servers or self-signed certificates.

## Installation

Use pip (or pipx - recommended) to avoid contaminating your system with a bunch of dependencies.
```bash
$ pipx install --user gsan
```

You can also install and run it using Docker.
```bash
$ docker run --rm -i francc3sco/gsan <DOMAIN>
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

If you're using the dockerized version, you can achieve the same by doing:
```bash
$ cat domains.txt | xargs docker run --rm -i francc3sco/gsan
```

You can combine gsan with other tools like shodan to get a list of SANs found in a list of domains or IP addresses as long as you respect the IP|DOMAIN:PORT format.
```bash
$ shodan search --fields ip_str,port --separator : --limit 100 https | cut -d : -f 1,2 | xargs gsan --timeout 1

207.21.195.58 [1]:
- orielstat.com

162.159.135.42 [4]:
- temp927.kinsta.cloud
- temp312.kinsta.cloud

34.230.178.151 [2]:
- procareltc.com
- clarest.com

20.62.53.137 [1]:
- budget.lis.virginia.gov

199.60.103.228 [3]:
- hscoscdn40.net
- sites-proxy.hscoscdn40.net
...
```

You can also output to a file by using the `--output` flag which can be useful to then pass the output to other tools such as Nmap.
```bash
$ gsan microsoft.com --output microsoft.txt | nmap -iL microsoft.txt
```

Or, if you have a large list of domains:
```bash
$ cat domains.txt | xargs gsan --output domains.txt | nmap -iL domains.txt
```

Or, if you want chaos to take the world:
```bash
$ shodan search --fields ip_str,port --separator : --limit 1000 has_ipv6:false https | \
  cut -d : -f 1,2 | \
  xargs gsan --timeout 1 --output sans.txt && \
  sudo nmap -sS -F -vvv -iL sans.txt -oX import_to_metasploit.xml
```
