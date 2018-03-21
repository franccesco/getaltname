#!/usr/bin/env python3
# Author: Franccesco Orozco.
# Version: 1.3.1
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


import argparse
from tqdm import tqdm
from colorama import init
from os.path import isfile
from termcolor import colored

# GAN Modules
from modules.get_san import get_san
from modules.clipboard import clipboard_output
from modules.nmap_parsing import parse_nmap
from modules.report import output, report_single, collect_report

# starting Colorama
init()

# CLI argumentation
parser = argparse.ArgumentParser(
    formatter_class=lambda
    prog: argparse.HelpFormatter(prog, max_help_position=100))
parser.add_argument('hostname', type=str, help='Host or Nmap XML to analyze.')
parser.add_argument('-p', '--port', type=int,
                    default=443, help='Destiny port (default 443)')
parser.add_argument('-s', '--search-crt', metavar='timeout',
                    help='Retrieve subdomains found in crt.sh',
                    nargs='?', type=int, const=5)
parser.add_argument('-m', '--match-domain',
                    help='Show match domain name only', action='store_true')
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
                    help='Print version information.', version='1.3.1')
args = parser.parse_args()


"""
    if GAN detects the 'hostname' is actually a file, then it assumes
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
    report_single(sans, args.hostname, args.format)

    if args.clipboard:
        clipboard_output(sans, args.clipboard)

    if args.output:
        output(sans, args.format, args.output)

else:
    hosts = parse_nmap(args.hostname)

    # if no hosts are found in XML then exits
    if not any(hosts):
        message = 'No hosts found in {}'.format(args.hostname)
        print(colored(message, 'white', 'on_red'))
        exit()

    full_report = []
    for host, ports in tqdm(hosts.items()):
        for port in ports:
            sans = get_san(host, port, xml_parse=True)
            full_report.append(collect_report(sans, host, port))
    for report in full_report:
        if report is not False:
            print(report)
