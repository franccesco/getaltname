---
# You don't need to edit this file, it's empty on purpose.
# Edit theme's home layout instead if you wanna make some changes
# See: https://jekyllrb.com/docs/themes/#overriding-theme-defaults
layout: default
---

## Extract subdomains with GAN
GetAltName (or **GAN**) is a tool that **extracts sub-domains or virtual domains directly from SSL certificates** found in HTTP**S** sites. It returns a handy list of sub-domains to ease the phase of information gathering in a pen-testing assessment where you can find an interesting amount of data.

You can read more about how to do this _manually_ from my blog post on [getroot.info](https://getroot.info/tip-getaltname/) [Spanish].

## Roadmap

- [x] Returns a list of **unique** subdomains.
- [x] Strip subdomain **wildcards**.
- [x] Removes duplication for **www** subdomains (e.g. example.com and www.example.com)
- [x] Copy the **output directly to clipboard** as a single line string or as a list
- [x] A filter system for main domain and TLD's.
- [x] Get additional sub-domains from crt.sh
- [x] Colors

## What's to be added in a near future?
- [ ] [Ideas/suggestions are very welcome.](https://github.com/franccesco/getaltname/issues)

## Usage:
```
usage: getaltname.py [-h] [-p PORT] [-s [timeout]] [-m] [-o OUTPUT] [-c {l,s}]
                     [-d]
                     hostname

positional arguments:
  hostname                              Host to analyze.

optional arguments:
  -h, --help                            show this help message and exit
  -p PORT, --port PORT                  Destiny port (default 443)
  -s [timeout], --search-crt [timeout]  Retrieve subdomains found in crt.sh
  -m, --matching-domain                 Show matching domain name only
  -o OUTPUT, --output OUTPUT            Set output filename
  -c {l,s}, --clipboard {l,s}           Copy the output to the clipboard as a
                                        List or a Single string
  -d, --debug                           Set debug enable
```

- With **`-m`** GAN can **return a list of subdomains ending in the domain you previously specified**. For example, if you're analyzing _google.com_ you will get _youtube.com_ and other domains, if you only want subdomains belonging to _google.com_ then you can filter out those domains with **`-m`**
- **Select a custom port with `-p`**. This is useful if the server is on another port besides 443
- **[crt.sh](https://crt.sh/) integration**. You can now append results of crt.sh into your extracted subdomains list.
- **Copy to clipboard with option `-c`**. This argument gives you two options, copy the contents of the subdomain list in a _List_ with **`-c l`** or in a _single string_ style with **`-c s`**. This is useful if you need a quick way to analyze subdomain, say, with Nmap to provide a list of domains in a single string without having to load a file with **-iL**.

## Screenshot
[![Image Example](/assets/screenshot.png)](/getaltname/assets/screenshot.png)

## Demonstration

<script src="https://asciinema.org/a/tpebJeCEThMLDuDEXu1k1oz1o.js" id="asciicast-tpebJeCEThMLDuDEXu1k1oz1o" async></script>
_[You can also watch the demo here.](https://asciinema.org/a/tpebJeCEThMLDuDEXu1k1oz1o)_

## Installation
Required libraries:
* colorama
* ndg-httpsclient
* pyperclip
* requests
* tldextract
* termcolor

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
