#!/usr/bin/env python3
# Author: Franccesco Orozco.
# Version: 0.1.0
# This program extracts Subject Alternative Names from SSL Certificates
# which it can disclose virtual names the server has... so stop doing so many
# dns brute force for the love of god. This can also provide you with email
# addresses, URI's and IP addresses.
#
# Usage: getaltname.py -h [host] -p [ssl_port]
#
# MIT License
#
# Copyright (c) [2017] [Franccesco Orozco]
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
import pyperclip
from ndg.httpsclient.subj_alt_name import SubjectAltName
from pyasn1.codec.der import decoder

# CLI argumentation
parser = argparse.ArgumentParser()
parser.add_argument('hostname', type=str, help='Host to analize.')
parser.add_argument('-p', '--port', type=int,
                    default=443, help='Destiny port (default 443)')
parser.add_argument('-o', '--output', type=str,
                    help='Set output filename')
parser.add_argument('-c', '--clipboard',
                    help='Copy the output to the clipboardin as a List \
                    or a Single string', choices=['l', 's'])
args = parser.parse_args()


def get_san(hostname, port):
    """Gets Subject Alternative Names from requested host.
    Thanks to Cato- for this piece of code:
    https://gist.github.com/cato-/6551668"""

    subdomains = []
    general_names = SubjectAltName()

    # requesting certificate
    cert = ssl.get_server_certificate((args.hostname, args.port))
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

    return subdomains


def output(subdomains, destination):
    """Writes the subdomain list to a destination."""
    with open(destination, 'w') as file_object:
        for line in subdomains:
            file_object.write('{}\n'.format(line))


# print each subdomain found
sans = get_san(args.hostname, args.port)
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
