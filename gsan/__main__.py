#!/usr/bin/env python3
# Author: Franccesco Orozco.
# This program extracts Subject Alternative Names from SSL Certificates.
# It can disclose virtual names (subdomains) that the server has... so stop
# doing so many dns brute force for the love of god.
#
# Usage: ./getaltname.py [host]
#
# MIT License
#
# Copyright (c) [2018] [Franccesco Orozco]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import argparse
from tqdm import tqdm
from colorama import init
from os.path import isfile
from termcolor import colored

# GSAN Modules
from .version import version
from .banner import banner_usage
from gsan.get_san import get_san
from gsan.nmap_parsing import parse_nmap
from gsan.clipboard import clipboard_output
from gsan.report import output, report_single, collect_report, nmap_output


def main():
    """Command Line Interface."""
    # starting Colorama
    init()

    # CLI argumentation
    parser = argparse.ArgumentParser(
        formatter_class=lambda
        prog: argparse.HelpFormatter(prog, max_help_position=100),
        usage=banner_usage)
    parser.add_argument('hostname', type=str,
                        help='Host or Nmap XML to analyze.')
    parser.add_argument('-p', '--port', type=int,
                        default=443, help='Destiny port (default 443)')
    parser.add_argument('-s', '--search-crt', metavar='timeout',
                        help='Retrieve subdomains found in crt.sh',
                        nargs='?', type=int, const=5)
    parser.add_argument('-m', '--match-domain',
                        help='Matching domain names only', action='store_true')
    parser.add_argument('-q', '--quiet', help='Supress output.',
                        action='store_true')
    parser.add_argument('-o', '--output', type=str,
                        help='Set output filename')
    parser.add_argument('-f', '--format', type=str,
                        help='Set output format', choices=['json', 'text'])
    parser.add_argument('-c', '--clipboard',
                        help='Copy the output to the clipboard as a List \
                        or a Single string', choices=['l', 's'])
    parser.add_argument('-d', '--debug',
                        help='Set debug enable', action='store_true')
    parser.add_argument('-V', '--version', action='version',
                        help='Print version information.', version=version)
    args = parser.parse_args()

    """
        if GSAN detects the 'hostname' is actually a file, then it assumes
        that it's an NMAP XML output and try to parse it. If it's not a file,
        then it asummes that it is actually a hostname.
    """

    if not isfile(args.hostname):

        sans = get_san(
            hostname=args.hostname,
            port=args.port,
            xml_parse=False,
            crt_sh=args.search_crt,
            match=args.match_domain
        )
        report_single(sans, args.hostname, args.format, args.quiet)

        if args.clipboard:
            clipboard_output(sans, args.clipboard)

        if args.output:
            output(sans, args.hostname, args.format, args.output)

    else:
        print(colored('[*] Scanning hosts from Nmap XML output\n', 'yellow'))
        hosts = parse_nmap(args.hostname)

        # if no hosts are found in XML then exits
        if not any(hosts):
            message = f'No hosts found in {args.hostname}'
            print(colored(message, 'white', 'on_red'))
            print(('Use -sV (service scan) flag in '
                   'Nmap to detect https services.'))
            exit()

        full_report = []
        domains = []
        if not args.format == 'json':
            for host, ports in tqdm(hosts.items()):
                for port in ports:
                    sans = get_san(host, port, xml_parse=True)
                    for san in sans:
                        domains.append(san)
                    report = collect_report(sans, host, port)
                    full_report.append(report)
            for report in full_report:
                if report is not False:
                    if not args.quiet:
                        print(report)
            if args.output:
                output(domains, 'host', 'text', args.output)
        else:
            domains = {}
            for host, ports in tqdm(hosts.items()):
                for port in ports:
                    sans = get_san(host, port, xml_parse=True)
                    count = len(sans)
                    domains[host] = {'count': count, 'subdomains': list(sans)}
            json_report = json.dumps(domains, indent=2, sort_keys=True)
            if not args.quiet:
                print(json_report)

            if args.output:
                nmap_output(json_report, args.output)


if __name__ == '__main__':
    main()
