# GetAltName

[![Python Version](https://img.shields.io/badge/PyVersion-3.6-brightgreen.svg)](https://img.shields.io/badge/PyVersion-3.6-brightgreen.svg) [![Build Status](https://travis-ci.org/franccesco/getaltname.svg?branch=master)](https://travis-ci.org/franccesco/getaltname)  [![GitHub license](https://img.shields.io/github/license/franccesco/getaltname.svg)](https://github.com/franccesco/getaltname/blob/master/LICENSE.md)


GetAltName it's a little script that can extract Subject Alt Names for SSL Certificates directly from **HTTPS** web sites which can provide you with DNS names or virtual servers.

It's useful in a discovery phase of a pen-testing assessment, this tool can provide you with more information about your target and scope.

This code is in alpha stage and has been rewritten from Ruby to Python, it doesn't do as much as it should. lots of things and features are missing, but it delivers, treat it as a quick-dirty-code. More features incoming, also you're welcome to contribute if you want.

You can read more about how this tool works from my post in [getroot.info](https://getroot.info/tip-getaltname/) (in Spanish).

# Usage:
```
usage: getaltname.py [-h] [-p PORT] [-s [timeout]] [-m] [-o OUTPUT]
                     [-f {json,text}] [-c {l,s}] [-d]
                     hostname

positional arguments:
  hostname                              Host or Nmap XML to analyze.

optional arguments:
  -h, --help                            show this help message and exit
  -p PORT, --port PORT                  Destiny port (default 443)
  -s [timeout], --search-crt [timeout]  Retrieve subdomains found in crt.sh
  -m, --match-domain                    Show match domain name only
  -o OUTPUT, --output OUTPUT            Set output filename
  -f {json,text}, --format {json,text}  Set output format
  -c {l,s}, --clipboard {l,s}           Copy the output to the clipboard as a
                                        List or a Single string
  -d, --debug                           Set debug enable
```

You can output to a text file and **also copy the output to you clipboard** as a **L**ist or a **S**ingle line string, which is useful if you're trying to make a quick scan with _Nmap_ or other tools.

# Example
In this case the tool give you sub-domains that you probably didn't find with a sub-domain brute force tool.

![Example Image](screenshot.png)

# Installation
Required libraries:
* colorama
* ndg-httpsclient
* pyperclip
* requests
* tldextract
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

For the **copy&paste** mechanism you will have to install xclip package.
**Debian/Ubuntu/Mint:**
```sh
$ apt install xclip
```

# TO-DO
- [x] File output
- [x] Output to clipboard
- [x] Clean sub-domains wildcards
- [x] Remove duplicates
- [x] A filter system for main domain and TLD's.
- [x] Add colors (so l33t. /s)
- [x] Get additional sub-domains from crt.sh
- [x] Read Nmap XML and analyze them
- [x] JSON Output

# What's on the road
- [ ] Unit Tests
- [ ] HTML Report
- [ ] Multithreading

# Contributors
* [**Djerfy**](https://github.com/djerfy)

# Contribution Guidelines
Contribution is welcome, just remember:
* **Fork** the repo.
* Make changes to the **_develop_** branch.
* Make a **Pull Request.**

# Support this project
If you like the project and would like to support me you can buy me a cup of coffee, you will also be inmortalized as a patreon, thank you 🙏.

<a href="https://www.paypal.me/orozcofranccesco">
  <img height="32" src="badges/paypal.png" />
</a> <a href="https://www.buymeacoffee.com/franccesco" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/white_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a> <a href='https://ko-fi.com/V7V8AXFE' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://az743702.vo.msecnd.net/cdn/kofi2.png?v=0' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>
