"""Parse https://crt.sh/ results to acquire more subdomains."""

import json
import requests
from tldextract import extract
from colorama import init
from termcolor import colored

# starting Colorama
init()


def search_crt(domain, timeout=10):
    """Search subdomain on crt.sh to retrieve additional subdomains."""
    full_domain = extract(domain)
    domain = '{}.{}'.format(full_domain.domain, full_domain.suffix)
    subdomain_list = []
    request_url = 'https://crt.sh/?q=%.{}&output=json'.format(domain)

    # try to reach crt.sh, sometimes it takes too long
    # to process a request and end up throwing a 404
    try:
        request_json = requests.get(request_url, timeout=timeout)
    except requests.exceptions.ReadTimeout as e:
        timeout_msg = colored('FATAL: crt.sh timed out.', 'white', 'on_red')
        print(timeout_msg, end='\n')
        print(('Sometimes crt.sh takes too long trying to process '
               'large data sets and returns a \'404\' instead. This is beyond '
               'my power to fix, try another server, you might get lucky.'))
        exit(1)

    # crt.sh has JSON output currently broken, replacing endings like "}{"
    # with "},{" and enclosing the whole JSON in "[]" seems to fix it.
    request_json = request_json.text.replace('}{', '},{')
    fixed_json = json.loads(request_json)

    # loops through a list of dictionaries and extracts 'name_value' contents
    for extension_id, value in enumerate(fixed_json):
        subdomain = fixed_json[extension_id]['name_value']
        subdomain_list.append(subdomain)

    return set(sorted(subdomain_list))
