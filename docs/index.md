---
# You don't need to edit this file, it's empty on purpose.
# Edit theme's home layout instead if you wanna make some changes
# See: https://jekyllrb.com/docs/themes/#overriding-theme-defaults
layout: default
---

## Extract subdomains with GAN
![Python Version](https://img.shields.io/badge/PyVersion-3.6-brightgreen.svg) [![Build Status](https://travis-ci.org/franccesco/getaltname.svg?branch=master)](https://travis-ci.org/franccesco/getaltname) [![Coverage Status](https://coveralls.io/repos/github/franccesco/getaltname/badge.svg?branch=master)](https://coveralls.io/github/franccesco/getaltname?branch=master) [![GitHub release](https://img.shields.io/github/release/franccesco/getaltname.svg)](https://github.com/franccesco/getaltname/releases) [![GitHub forks](https://img.shields.io/github/forks/franccesco/getaltname.svg)](https://github.com/franccesco/getaltname/network) [![GitHub stars](https://img.shields.io/github/stars/franccesco/getaltname.svg)](https://github.com/franccesco/getaltname/stargazers)

**GetAltName** (or **GAN**) is a tool that can extract [Subject Alternative Names](https://en.wikipedia.org/wiki/Subject_Alternative_Name) found in SSL Certificates directly from **HTTPS** web sites which can provide you with DNS names (subdomains) or virtual servers.

This code extract subdomain names from http**s** sites and return a list or json output of its findings. It is _**not**_ a subdomain brute-force tool, and you can [actually find those subdomains manually](https://gfycat.com/AnotherDizzyDodobird), this tools is about the automation of that process, it also offers the following features:
* Input a **host or Nmap XML file** to scan and return subdomains.
* **List or JSON output**, useful if you want to export data into other tools.
* You can _optionally_ **filter out domain names** that doesn't match the domain name that you're analyzing.
* **Copy to your clipboard** the domain names as a _list_ or _string_ if you don't want to deal with files, this is also useful for tools that doesn't accept file input.

You can read more about how to do this _manually_ from my blog post on [getroot.info](https://getroot.info/tip-getaltname/) [Spanish - _written on November 13, 2017_].

# Features
- [x] File output
- [x] Output to clipboard
- [x] Clean sub-domains wildcards
- [x] Remove duplicates
- [x] A filter system for main domain and TLD's.
- [x] Add colors (so l33t. /s)
- [x] Get additional sub-domains from crt.sh
- [x] Read Nmap XML and analyze them
- [x] JSON Output
- [x] Unit Tests

# What's on the road
- [ ] Multithreading
- [ ] [Ideas/suggestions are very welcome.](https://github.com/franccesco/getaltname/issues)

## Usage:
```
usage: getaltname.py [-h] [-p PORT] [-s [timeout]] [-m] [-q] [-o OUTPUT]
                     [-f {json,text}] [-c {l,s}] [-d] [-V]
                     hostname

positional arguments:
  hostname                              Host or Nmap XML to analyze.

optional arguments:
  -h, --help                            show this help message and exit
  -p PORT, --port PORT                  Destiny port (default 443)
  -s [timeout], --search-crt [timeout]  Retrieve subdomains found in crt.sh
  -m, --match-domain                    Show match domain name only
  -q, --quiet                           Supress output.
  -o OUTPUT, --output OUTPUT            Set output filename
  -f {json,text}, --format {json,text}  Set output format
  -c {l,s}, --clipboard {l,s}           Copy the output to the clipboard as a
                                        List or a Single string
  -d, --debug                           Set debug enable
  -V, --version                         Print version information.
```

## Example
[![Image Example](/assets/screenshot.png)](/getaltname/assets/screenshot.png)

## Demonstration

<script src="https://asciinema.org/a/bYYnK76AQJZFP9hj43e3CUaH5.js" id="asciicast-bYYnK76AQJZFP9hj43e3CUaH5" async></script>
_[You can also watch the demo here.](https://asciinema.org/a/bYYnK76AQJZFP9hj43e3CUaH5)_

## Installation
### Required:
* **python3**
* colorama
* ndg-httpsclient
* pyperclip
* requests
* tldextract
* termcolor
* tqdm

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

Also keep in mind that the `-s` option to append subdomains found from [crt.sh](https://crt.sh) it is sometimes very slow, this is because crt.sh takes too long to process large data sets and throws a '404' for whatever reason. **By default there's a 5 second time out** to reach crt.sh, but you can set this timeout with `-s [timeout]`

# Support this project
If you like the project and would like to support me you can buy me a cup of coffee, you will also be inmortalized as a patreon, thank you 🙏.

<a href="https://www.paypal.me/orozcofranccesco">
  <img height="32" src="assets/badges/paypal.png" />
</a>

<a href="https://www.buymeacoffee.com/franccesco" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/white_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>

<a href='https://ko-fi.com/V7V8AXFE' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://az743702.vo.msecnd.net/cdn/kofi2.png?v=0' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>
