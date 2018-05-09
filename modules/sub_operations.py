"""
Clean subdomains extracted from certificates.

List operations to aid in domain matching,
strip wildcards, and return a list of unique items.
"""

import re
from tldextract import extract


def match_domain_only(subdomain_list, hostname):
    """Return a list with the specified domain only."""
    match_list = []
    full_domain = extract(hostname)
    matching_domain = '{}.{}'.format(full_domain.domain, full_domain.suffix)
    for domain in subdomain_list:
        pattern = r'.*\.{}$'.format(matching_domain)
        matched_domain = re.search(pattern, domain)
        if matched_domain is None:
            continue
        subdomain_found = matched_domain.group(0)
        match_list.append(subdomain_found)
    return set(match_list)


def clean_san_list(subdomain_list, hostname, match_domain=False):
    """Clean wildcards such as '*.' and returns a unique set."""
    for domain in subdomain_list:
        item_index = subdomain_list.index(domain)

        # strip wildcards and unnecesary 'www'
        if '*.' in domain:
            subdomain_list[item_index] = domain[2:]
        elif 'www.' in domain:
            subdomain_list[item_index] = domain[4:]

    # if '-m' flag is True, then match domains only
    if match_domain:
        match_list = match_domain_only(subdomain_list, hostname)
        return match_list

    return set(sorted(subdomain_list))
