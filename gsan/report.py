"""Module to report an output in JSON, HTML, and List."""

import json
from .banner import banner
from colorama import init
from termcolor import colored
# starting Colorama
init()


def output(subdomains, hostname, format_output, destination):
    """Write a subdomain list to a destination."""
    with open(destination, 'w') as file_object:
        if format_output == 'json':
            file_object.write('{}'.format(json_format(subdomains, hostname)))
        else:
            for line in subdomains:
                file_object.write('{}\n'.format(line))


def nmap_output(report, destination):
    """Output NMAP XML results to a json or list file."""
    with open(destination, 'w') as file_object:
        file_object.write(str(report))


def json_format(subdomains, hostname):
    """Output JSON format."""
    listdomains = {'count': len(subdomains), 'domains': list(subdomains)}
    return json.dumps(listdomains, indent=2, sort_keys=True)


def report_single(subdomain_list, hostname, format, quiet=False):
    """Report if subdomains were found."""
    if format == 'json':
        if not quiet:
            print(banner)
            print(json_format(subdomain_list, hostname))
    else:
        if not quiet:
            print(banner)
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
    Look for targets in a XML Nmap report.

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
