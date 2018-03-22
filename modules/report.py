"""
    Module to report an output in JSON, HTML, and List.
"""

import json
from colorama import init
from termcolor import colored

# starting Colorama
init()


def output(subdomains, format_output, destination):
    """Writes the subdomain list to a destination."""
    with open(destination, 'w') as file_object:
        if format_output == 'json':
            file_object.write('{}'.format(json_format(subdomains)))
        else:
            for line in subdomains:
                file_object.write('{}\n'.format(line))


def json_format(subdomains):
    """Output JSON format."""
    listdomains = {'count': len(subdomains), 'domains': []}
    for domain in subdomains:
        listdomains['domains'].append(domain)
    return json.dumps(listdomains)


def report_single(subdomain_list, hostname, format):
    """Reports if subdomains were found."""

    if format == 'json':
        print(json_format(subdomain_list))
    else:
        if len(subdomain_list) > 0:
            # print discovery report and a separator ('—')
            message = "{} SAN's found from {}\n".format(
                len(subdomain_list), hostname)
            separator = '—' * (len(message) - 1)
            print(colored(message + separator, 'green'))

            # print each subdomain found
            for subject in sorted(subdomain_list):
                print(colored('→ ', 'green') + subject)
            print('\n', end='')
        else:
            print(colored("No SAN's were found.", 'white', 'on_red'))
            print('\n', end='')


def collect_report(subdomain_list, hostname, port):
    """
        A more specialized report for nmap parsing, it doesn't output anything
        to stdout, it returns a report (string) for each finding, if there's
        nothing to report, then return false.
    """
    if len(subdomain_list) > 0:
        message = "\n{} SAN's found from {}:{}\n".format(
            len(subdomain_list), hostname, port
        )
        separator = '—' * (len(message) - 1)
        san_report = colored(message + separator, 'green')

        for subject in sorted(subdomain_list):
            san_report += colored('\n→ ', 'green') + subject
        return(san_report)
    else:
        return False
