"""
Gets Subject Alternative Names from requested host.

Thanks to Cato- for this piece of code:
https://gist.github.com/cato-/6551668
"""

import ssl
import OpenSSL
from colorama import init
from termcolor import colored
from pyasn1.codec.der import decoder
from ndg.httpsclient.subj_alt_name import SubjectAltName
from gsan.sub_operations import clean_san_list
from gsan.crt_sh import search_crt

# starting Colorama
init()


def get_san(hostname, port, xml_parse=False, crt_sh=False, match=False):
    """Get Subject Alternative Names from target."""
    subdomains = []
    general_names = SubjectAltName()

    # Tries to connect to server, exits on error unless Traceback is requested
    try:
        cert = ssl.get_server_certificate((hostname, port))
    except Exception as e:
        if xml_parse:
            return []
        err = colored('FATAL: Could not connect to server.', 'white', 'on_red')
        e.strerror = err
        raise e

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
    if crt_sh:
        crt_subdomains = search_crt(hostname, crt_sh)
        if crt_subdomains is not False:
            subdomains = list(subdomains) + list(crt_subdomains)

    # return a unique set of subdomains without wildcards
    filtered_domains = clean_san_list(subdomains, hostname, match)
    return set(sorted(filtered_domains))
