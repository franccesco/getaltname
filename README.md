# GSAN - Get Subject Alternative Names

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gsan)![PyPI](https://img.shields.io/pypi/v/gsan)![PyPI - License](https://img.shields.io/pypi/l/gsan)


**GSAN** is a tool that can extract [Subject Alternative Names](https://en.wikipedia.org/wiki/Subject_Alternative_Name) found in SSL Certificates _directly_ from https web sites which can provide you with DNS names (subdomains) or virtual servers.

This tool extract subdomain names from http**s** sites and return a list or CSV/JSON output of its findings. It is _**not**_ a subdomain brute-force tool, and you can [actually find those subdomains manually](https://gfycat.com/AnotherDizzyDodobird), this tools is about the automation of that process, it also offers the following features:

* Define multiple hosts:port on your terminal or using a text file.
* CSV or JSON output, useful if you want to export data into other tools.
* You can _optionally_ filter out domain names that doesn't match the domain name that you're analyzing.
* Integration with CRT.SH so you can extract more subdomains from certificates of the same entity.
* Also works with **Self-signed** certificates.

## Installation
```bash
$ pip install --user gsan
```

## Usage

You have 2 ways of executing GSAN, getting subdomain names from CRT.SH, in which GSAN acts as a wrapper for CRT.SH, or getting subdomain names by directly connecting

```
Usage: gsan [OPTIONS] COMMAND [ARGS]...

  Get subdomain names from SSL Certificates.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  crtsh  Get domains from crt.sh
  scan   Scan domains from input or a text file, format is HOST[:PORT].
```

### Getting subdomains from CRT.SH
If you prefer to get the subdomain names directly from CRT.SH you can do that by using the subcomand `crtsh`.

```bash
$ gsan crtsh --help
Usage: gsan crtsh [OPTIONS] [DOMAINS]...

  Get domains from crt.sh

Options:
  -m, --match-domain     Match domain name only.
  -o, --output TEXT      Output to path/filename.
  -t, --timeout INTEGER  Set timeout for CRT.SH
  --help                 Show this message and exit.

$ gsan crtsh facebook.com
[+] Getting subdomains for facebook.com
[+] Results:
                                        FACEBOOK.COM
1                                  free-facebook.com
2                                   the-facebook.com
3                                google-facebook.com
4                                    me-facebook.com
5                                       facebook.com
6                                  bomb-facebook.com
--- SNIP ---
142                              china--facebook.com
143                         imagem-para-facebook.com
144                           aplikacje-facebook.com
145                     tourism-ireland-facebook.com
146                                 tsc-facebook.com
147                             edenred-facebook.com
```

### Getting subdomains directly from SSL certificates
Most programs that _"abuse"_ transparency certificates are only a wrapper for crt.sh, however you can extract subdomain names directly from SSL certificates found in HTTPS services. This allows you to find subdomain names in services that have self-signed certificates or deployed services that are not found anywhere. You can do this using the subcomand `scan`.

```bash
$ gsan scan --help
Usage: gsan scan [OPTIONS] [HOSTNAMES]...

  Scan domains from input or a text file, format is HOST[:PORT].

  e.g: gsan scan domain1.com domain2.com:port

  You can also pass a text file instead, just replace the first domain
  argument for a file. eg: gsan scan filename.txt

  If no ports are defined, then gsan assumes the port 443 is available.

Options:
  -o, --output TEXT      Output to path/filename.
  -m, --match-domain     Match domain name only.
  -c, --crtsh            Include results from CRT.SH
  -t, --timeout INTEGER  Set timeout [default: 3]
  --help                 Show this message and exit.

$ gsan scan facebook.com starbucks.com:443
[+] Getting subdomains for facebook.com
[+] Getting subdomains for starbucks.com
[+] Results:
      FACEBOOK.COM          STARBUCKS.COM
1     facebook.com          starbucks.com
2     facebook.net    app.starbucks.co.uk
3           fb.com   app.starbucks.com.br
4        fbcdn.net       app.starbucks.de
5        fbsbx.com           starbucks.ca
6    messenger.com           starbucks.fr
7   m.facebook.com           starbucks.ie
8     xx.fbcdn.net       app.starbucks.fr
9     xy.fbcdn.net           starbucks.de
10    xz.fbcdn.net       starbucks.com.br
11                  preview.starbucks.com
12                       app.starbucks.ca
13                       app.starbucks.ie
14                        starbucks.co.uk
15                      app.starbucks.com
16                        fr.starbucks.ca
17                    fr.app.starbucks.ca
```

You can also pass a list of hosts their ports, formatted as host[:port] (port is optional), and gsan will go through them trying to extract subdomain names. You can use the same subcomand `scan` and pass a text file as argument instead of a domain name:

```bash
gsan scan hosts.txt -o subdomains.csv
[+] Getting subdomains for facebook.com
[+] Getting subdomains for starbucks.com
[+] Getting subdomains for fakedomain.com
[!] Unable to connect to host fakedomain.com
[+] Getting subdomains for amazon.com
[+] Results:
      FACEBOOK.COM          STARBUCKS.COM                         AMAZON.COM
1     facebook.com          starbucks.com                       amazon.co.uk
2     facebook.net    app.starbucks.co.uk                uedata.amazon.co.uk
3           fb.com   app.starbucks.com.br                origin-amazon.co.uk
4        fbcdn.net       app.starbucks.de                        peg.a2z.com
5        fbsbx.com           starbucks.ca                         amazon.com
6    messenger.com           starbucks.fr                           amzn.com
7   m.facebook.com           starbucks.ie                  uedata.amazon.com
8     xx.fbcdn.net       app.starbucks.fr                      us.amazon.com
9     xy.fbcdn.net           starbucks.de               corporate.amazon.com
10    xz.fbcdn.net       starbucks.com.br                  buybox.amazon.com
11                  preview.starbucks.com                  iphone.amazon.com
12                       app.starbucks.ca                      yp.amazon.com
13                       app.starbucks.ie                    home.amazon.com
14                        starbucks.co.uk                  origin-amazon.com
15                      app.starbucks.com  buckeye-retail-website.amazon.com
16                        fr.starbucks.ca                 huddles.amazon.com
17                    fr.app.starbucks.ca                          amazon.de
18                                                          origin-amazon.de
19                                                              amazon.co.jp
20                                                                 amazon.jp
21                                                       origin-amazon.co.jp
22                                                            aa.peg.a2z.com
23                                                            ab.peg.a2z.com
24                                                            ac.peg.a2z.com
25                                                      origin-amazon.com.au
26                                                             amazon.com.au
27                                                            bz.peg.a2z.com

[+] Contents dumped into CSV file: subdomains.csv
```

You can save the results into a CSV or JSON file, the program will format the output based on the file extension.

## Contributors
* [**Djerfy**](https://github.com/djerfy) - **JSON output**.

## Contribution Guidelines
Contribution is welcome, just remember:
* **Fork** the repo.
* Make changes to the **_develop_** branch.
* Make a **Pull Request.**

## Support this project

<a href="https://www.paypal.me/orozcofranccesco">
  <img height="32" src="assets/paypal_badge.png" />
</a> <a href="https://www.buymeacoffee.com/franccesco" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/white_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a> <a href='https://ko-fi.com/V7V8AXFE' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://az743702.vo.msecnd.net/cdn/kofi2.png?v=0' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>

## More Information

```
 _____ _____ _____ _____
|   __|   __|  _  |   | |
|  |  |__   |     | | | |
|_____|_____|__|__|_|___| v4.1.2

Author:  Franccesco Orozco
Email:   franccesco@codingdose.info
Website: https://codingdose.info
```
