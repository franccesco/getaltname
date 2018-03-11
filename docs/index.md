---
# You don't need to edit this file, it's empty on purpose.
# Edit theme's home layout instead if you wanna make some changes
# See: https://jekyllrb.com/docs/themes/#overriding-theme-defaults
layout: default
---

## Extract subdomains with GAN
GetAltName (or **GAN**) is a tool that **extracts sub-domains or virtual domains directly from SSL certificates** found in HTTP**S** sites. It returns a handy list of sub-domains to ease the phase of information gathering in a pen-testing assessment where you can find an interesting amount of data.

You can read more about how to do this _manually_ from my blog post on [getroot.info](https://getroot.info/tip-getaltname/) [Spanish].

## What features does it have?

- [x] Returns a list of **unique** subdomains.
- [x] Strip subdomain **wildcards**.
- [x] Removes duplication for **www** subdomains (e.g. example.com and www.example.com)
- [x] Copy the **output directly to clipboard** as a single line string or as a list
- [x] A filter system for main domain and TLD's.

## What's to be added in a near future?
- [ ] Get additional sub-domains from crt.sh
- [ ] [Ideas/suggestions are very welcome.](https://github.com/franccesco/getaltname/issues)

# Usage:
```
usage: getaltname.py [-h] [-p PORT] [-m] [-o OUTPUT] [-c {l,s}] [-d] hostname

positional arguments:
  hostname                     Host to analyze.

optional arguments:
  -h, --help                   show this help message and exit
  -p PORT, --port PORT         Destiny port (default 443)
  -m, --matching-domain        Show matching domain name only
  -o OUTPUT, --output OUTPUT   Set output filename
  -c {l,s}, --clipboard {l,s}  Copy the output to the clipboard as a List or a
                               Single string
  -d, --debug                  Set debug enable
```

You can output to a text file and **also copy the output to you clipboard** as a **L**ist or a **S**ingle line string, which is useful if you're trying to make a quick scan with _Nmap_ or other tools.

## Demonstration
<script src="https://asciinema.org/a/01j0mhxOmXI4UOQiq6iNStDxn.js" id="asciicast-01j0mhxOmXI4UOQiq6iNStDxn" async></script>

## Installation
Required libraries:
* colorama
* ndg-httpsclient
* pyperclip
* requests

**Installation with pipenv**:
```sh
$ git clone https://github.com/franccesco/getaltname.git
$ pipenv install
```

**Installation with Pip:**
```sh
$ git clone https://github.com/franccesco/getaltname.git
$ pip install -r requirements.txt
```

## Troubleshooting
If for some reason the **copy&paste** mechanism doesn't work, you will have to install xclip package.
**Debian/Ubuntu/Mint:**
```sh
$ apt install xclip
```
