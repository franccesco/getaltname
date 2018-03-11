#!/usr/bin/env python3
# Author: Franccesco Orozco.
# Version: 0.2.1
# This program extracts Subject Alternative Names from SSL Certificates.
# It can disclose virtual names (subdomains) that the server has... so stop
# doing so many dns brute force for the love of god.
#
# Usage: getaltname.py -p [ssl_port] [host]
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

import ssl
import OpenSSL
import argparse
import colorama
import pyperclip
from ndg.httpsclient.subj_alt_name import SubjectAltName
from pyasn1.codec.der import decoder

# starting Colorama
colorama.init()

# CLI argumentation
parser = argparse.ArgumentParser()
parser.add_argument('hostname', type=str, help='Host to analyze.')
parser.add_argument('-p', '--port', type=int,
                    default=443, help='Destiny port (default 443)')
parser.add_argument('-o', '--output', type=str,
                    help='Set output filename')
parser.add_argument('-c', '--clipboard',
                    help='Copy the output to the clipboard as a List \
                    or a Single string', choices=['l', 's'])
parser.add_argument('-d', '--debug',
                    help='Set debug enable', action='store_true')
args = parser.parse_args()


def clean_san_list(subdomain_list):
    """Clean wildcards such as '*.' and returns a unique set."""
    for domain in subdomain_list:
        item_index = subdomain_list.index(domain)
        if '*.' in domain:
            subdomain_list[item_index] = domain[2:]
        elif 'www.' in domain:
            subdomain_list[item_index] = domain[4:]
    return set(subdomain_list)


def get_san(hostname, port, debug=False):
    """Gets Subject Alternative Names from requested host.
    Thanks to Cato- for this piece of code:
    https://gist.github.com/cato-/6551668"""

    subdomains = []
    general_names = SubjectAltName()

    # Tries to connect to server, exits on error unless Traceback is requested
    try:
        cert = ssl.get_server_certificate((args.hostname, args.port))
    except Exception as e:
        print('FATAL: Could not connect to server.')
        if debug:
            raise e
        exit()

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

    # return a unique set of subdomains without wildcards
    filtered_domains = clean_san_list(subdomains)
    return filtered_domains


def output(subdomains, destination):
    """Writes the subdomain list to a destination."""
    with open(destination, 'w') as file_object:
        for line in subdomains:
            file_object.write('{}\n'.format(line))


sans = get_san(args.hostname, args.port, args.debug)

# print discovery report and a separator ('=') as long as the message
message = "{} SAN's found from {}".format(len(sans), args.hostname)
print(message)
print('=' * len(message))

# print each subdomain found
for subject in sans:
    print(subject)

# write to output file
if args.output:
    output(sans, args.output)

# copy to clipboard, 's' for string and 'l' for list
if args.clipboard == 's':
    pyperclip.copy(' '.join(sans))
elif args.clipboard == 'l':
    pyperclip.copy('\n'.join(sans))
