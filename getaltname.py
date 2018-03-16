#!/usr/bin/env python3
# Author: Franccesco Orozco.
# Version: 1.0.0
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

import re
import ssl
import json
import OpenSSL
import requests
import argparse
import pyperclip
import xml.etree.ElementTree as ET

from tqdm import tqdm
from colorama import init
from os.path import isfile
from termcolor import colored
from tldextract import extract
from pyasn1.codec.der import decoder
from ndg.httpsclient.subj_alt_name import SubjectAltName

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
parser.add_argument('-m', '--matching-domain',
                    help='Show matching domain name only', action='store_true')
parser.add_argument('-o', '--output', type=str,
                    help='Set output filename')
parser.add_argument('-c', '--clipboard',
                    help='Copy the output to the clipboard as a List \
                    or a Single string', choices=['l', 's'])
parser.add_argument('-d', '--debug',
                    help='Set debug enable', action='store_true')
args = parser.parse_args()


def match_domain_only(subdomain_list):
    """Returns a list with the specified domain only."""
    match_list = []
    full_domain = extract(args.hostname)
    matching_domain = '{}.{}'.format(full_domain.domain, full_domain.suffix)
    for domain in subdomain_list:
        pattern = '.*\.{}$'.format(matching_domain)
        matched_domain = re.search(pattern, domain)
        if matched_domain is None:
            continue
        subdomain_found = matched_domain.group(0)
        match_list.append(subdomain_found)
    return set(match_list)


def clean_san_list(subdomain_list, domain_only=False):
    """Clean wildcards such as '*.' and returns a unique set."""
    for domain in subdomain_list:
        item_index = subdomain_list.index(domain)

        # strip wildcards and unnecesary 'www'
        if '*.' in domain:
            subdomain_list[item_index] = domain[2:]
        elif 'www.' in domain:
            subdomain_list[item_index] = domain[4:]

    # if '-m' flag is True, then match domains only
    if domain_only:
        match_list = match_domain_only(subdomain_list)
        return match_list

    return set(sorted(subdomain_list))


def get_san(hostname, port, xml_parse=False):
    """Gets Subject Alternative Names from requested host.
    Thanks to Cato- for this piece of code:
    https://gist.github.com/cato-/6551668"""

    subdomains = []
    general_names = SubjectAltName()

    # Tries to connect to server, exits on error unless Traceback is requested
    try:
        cert = ssl.get_server_certificate((hostname, port))
    except Exception as e:
        if xml_parse:
            return []
        err = colored('FATAL: Could not connect to server.', 'white', 'on_red')
        print(err, end='\n\n')
        exit(1)

    # requesting certificate
    x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)

    # get all extensions from certificate and iterate until we find a SAN entry
    for extension_id in range(0, x509.get_extension_count()):
        ext = x509.get_extension(extension_id)

        # decode the shortname to UTF-8 to be able to compare strings
        ext_name = ext.get_short_name().decode('utf-8')
        if ext_name == 'subjectAltName':

            # get_data() returns a heavily coded byte string
            ext_data = ext.get_data()
            decoded_dat = decoder.decode(ext_data, asn1Spec=general_names)

            # decoding SANS with magic sauce, please explain this to me.
            for name in decoded_dat:
                if isinstance(name, SubjectAltName):
                    for entry in range(len(name)):
                        component = name.getComponentByPosition(entry)
                        subdomains.append(str(component.getComponent()))

    # merge list results from crt.sh if found.
    if args.search_crt:
        crt_subdomains = search_crt(hostname)
        if crt_subdomains is not False:
            subdomains = list(subdomains) + list(crt_subdomains)

    # return a unique set of subdomains without wildcards
    filtered_domains = clean_san_list(subdomains, args.matching_domain)
    return set(sorted(filtered_domains))


def search_crt(domain):
    """Search subdomain on crt.sh to retrieve additional subdomains."""

    # strip subdomain from request
    full_domain = extract(domain)
    domain = '{}.{}'.format(full_domain.domain, full_domain.suffix)
    subdomain_list = []
    request_url = 'https://crt.sh/?q=%.{}&output=json'.format(domain)

    # try to reach crt.sh, sometimes it takes too long
    # to process a request and end up throwing a 404
    try:
        request_json = requests.get(request_url, timeout=args.search_crt)
    except requests.exceptions.ReadTimeout as e:
        timeout_msg = colored('FATAL: crt.sh timed out.', 'white', 'on_red')
        print(timeout_msg, end='\n')

        # explain why a timeout is needed
        print(('Sometimes crt.sh takes too long trying to process '
               'large data sets and returns a \'404\' instead. This is beyond '
               'my power to fix, try another server, you might get lucky.'))
        exit(1)

    # if returned status is not 'OK' then return 'False' and move on
    if request_json.status_code != 200:
        return False

    # crt.sh has JSON output currently broken, replacing endings like "}{"
    # with "},{" and enclosing the whole JSON in "[]" seems to fix it.
    request_json = request_json.text.replace('}{', '},{')
    fixed_json = json.loads('[{}]'.format(request_json))

    # loops through a list of dictionaries and extracts'name_value' contents
    for extension_id, value in enumerate(fixed_json):
        subdomain = fixed_json[extension_id]['name_value']
        subdomain_list.append(subdomain)

    return set(sorted(subdomain_list))


def parse_nmap(nmap_xml):
    """Returns hosts with HTTPS ports."""
    report = ET.parse(nmap_xml)
    hosts_to_scan = {}
    for host in report.iter('host'):
        ports = []
        for port in host[3].findall('port'):
            # find every port running a http + ssl service
            if 'http' and 'ssl' in port[1].attrib.values():
                # append every found port to a address
                ports.append(port.attrib['portid'])
                hosts_to_scan[host[1].attrib['addr']] = ports
            else:
                continue
    return hosts_to_scan


def output(subdomains, destination):
    """Writes the subdomain list to a destination."""
    with open(destination, 'w') as file_object:
        for line in subdomains:
            file_object.write('{}\n'.format(line))


def report_single(subdomain_list, hostname=args.hostname):
    """Reports if subdomains were found."""
    if len(subdomain_list) > 0:
        # print discovery report and a separator ('—') as long as the message
        message = "{} SAN's found from {}\n".format(len(sans), hostname)
        separator = '—' * (len(message) - 1)
        print(colored(message + separator, 'green'))

        # print each subdomain found
        for subject in sorted(sans):
            print(colored('>> ', 'green') + subject)
        print('\n', end='')
    else:
        print(colored("No SAN's were found.", 'white', 'on_red'))
        print('\n', end='')


def collect_report(subdomain_list, hostname, port):
    if len(subdomain_list) > 0:
        message = "\n{} SAN's found from {}:{}\n".format(
            len(sans), hostname, port
        )
        separator = '—' * (len(message) - 1)
        san_report = colored(message + separator, 'green')

        for subject in sorted(sans):
            san_report += colored('\n>> ', 'green') + subject
        return(san_report)
    else:
        return False


def clipboard_output(subdomain_list, output_style=args.clipboard):
    """Copy to clipboard, 's' for string and 'l' for list."""
    if output_style == 's':
        pyperclip.copy(' '.join(subdomain_list))
    elif output_style == 'l':
        pyperclip.copy('\n'.join(subdomain_list))


if not isfile(args.hostname):
    sans = get_san(args.hostname, args.port, args.debug)
    report_single(sans)

    if args.output:
        output(sans, args.output)

    if args.clipboard:
        clipboard_output(sans, args.clipboard)

else:
    hosts = parse_nmap(args.hostname)
    full_report = []
    for host, ports in tqdm(hosts.items()):
        for port in ports:
            sans = get_san(host, port, xml_parse=True)
            full_report.append(collect_report(sans, host, port))
    for report in full_report:
        if report is not False:
            print(report)
