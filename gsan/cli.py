import ssl
from sys import exit
from os.path import isfile
from datetime import datetime

import OpenSSL
import click
from socket import setdefaulttimeout
import pandas as pd
from ndg.httpsclient.subj_alt_name import SubjectAltName
from pyasn1.codec.der import decoder

from gsan.clean_df import concat_dfs
from gsan.clean_df import filter_domain
from gsan.clean_df import reindex_df
from gsan.clean_df import strip_chars
from gsan.crtsh import get_crtsh
from gsan.output import dump_filename
from gsan.version import about_message
from gsan.extract_host_port import parse_host_port


@click.group()
@click.version_option(version="4.2.2", message=about_message)
def cli():
    """Get subdomain names from SSL Certificates."""
    pass


@cli.command()
@click.argument("domains", nargs=-1)
@click.option("-m", "--match-domain", is_flag=True, help="Match domain name only")
@click.option("-o", "--output", help="Output to path/filename")
@click.option("-t", "--timeout", default=30, type=int, help="Set timeout for CRT.SH")
def crtsh(domains, match_domain, output, timeout):
    """Get domains from crt.sh"""
    subdomains_data = []
    for domain in domains:
        click.secho(f"[+] Getting subdomains for {domain}", bold=True)
        subdomain_df = get_crtsh(domain, timeout)
        if match_domain:
            subdomain_df = filter_domain(subdomain_df, domain)
        subdomain_df = reindex_df(subdomain_df)
        subdomains_data.append(subdomain_df)
    merged_subdomains = concat_dfs(subdomains_data, domains)
    click.secho("[+] Results:", bold=True)
    print(merged_subdomains.to_string())
    if output:
        dump_filename(output, merged_subdomains)


@cli.command("scan")
@click.argument("hostnames", nargs=-1)
@click.option("-o", "--output", help="Output to path/filename")
@click.option("-m", "--match-domain", is_flag=True, help="Match domain name only")
@click.option("-c", "--crtsh", is_flag=True, help="Include results from CRT.SH - SLOW!")
@click.option("-t", "--timeout", default=3, help="Set timeout [default: 3]")
@click.option("-s", "--suppress", is_flag=True, help="Suppress output")
def scan_site(hostnames, match_domain, output, crtsh, timeout, suppress):
    """Scan domains from input or a text file, format is HOST[:PORT].

    e.g: gsan scan domain1.com domain2.com:port

    You can also pass a text file instead, just replace the first domain argument
    for a file. eg: gsan scan filename.txt

    If no ports are defined, then gsan assumes the port 443 is available."""
    subdomains_data = []
    subjaltname = SubjectAltName()

    if isfile(hostnames[0]):
        with open(hostnames[0], "r") as host_file:
            hostnames = [host.rstrip("\n") for host in host_file]
        hostnames = [parse_host_port(host) for host in hostnames]
    else:
        hostnames = [parse_host_port(host) for host in hostnames]

    bad_hosts = []
    for hostname in hostnames:
        click.secho(f"[+] Getting subdomains for {hostname[0]}", bold=True)
        subdomains = []
        port = hostname[1] if hostname[1] else 443
        setdefaulttimeout(timeout)
        try:
            cert = ssl.get_server_certificate((hostname[0], port))
        except Exception:
            click.secho(f"[!] Unable to connect to host {hostname[0]}", bold=True, fg="red")
            bad_hosts.append(hostname[0])
            continue

        # Thanks to Cato- for this piece of code:
        # https://gist.github.com/cato-/6551668
        # get all extensions from certificate and iterate until we find a SAN entry
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
        for extension_id in range(0, x509.get_extension_count()):
            ext = x509.get_extension(extension_id)
            ext_name = ext.get_short_name().decode("utf-8")
            if ext_name == "subjectAltName":
                ext_data = ext.get_data()
                decoded_dat = decoder.decode(ext_data, asn1Spec=subjaltname)
                for name in decoded_dat:
                    if isinstance(name, SubjectAltName):
                        for entry in range(len(name)):
                            component = name.getComponentByPosition(entry)
                            subdomains.append(str(component.getComponent()))
        subdomain_df = pd.Series(subdomains)

        if crtsh:
            crtsh_results = get_crtsh(hostname[0])
            if crtsh_results.empty:
                pass
            else:
                subdomain_df = pd.concat([subdomain_df, crtsh_results])

        if subdomains:
            subdomain_df = strip_chars(subdomain_df)
        if match_domain:
            if subdomain_df.any():
                subdomain_df = filter_domain(subdomain_df, hostname[0])
        subdomain_df = reindex_df(subdomain_df)
        subdomains_data.append(subdomain_df)

    column_names = [name[0] for name in hostnames]
    for name in bad_hosts:
        column_names.remove(name)
    try:
        concat_df = concat_dfs(subdomains_data, column_names)
    except ValueError:
        click.secho(f"[!] No subdomains where found", bold=True, fg="yellow")
    else:
        if not suppress:
            click.secho("[+] Results:\n", bold=True)
            for column_name in concat_df:
                click.secho(column_name, bold=True, underline=True)
                domains = concat_df[column_name].dropna(how="all").to_list()
                for domain in domains:
                    arrow = click.style("↳ ", bold=True, fg="green")
                    print(arrow, end="")
                    print(f"{domain}")
                print("")
            if output:
                dump_filename(output, concat_df)
        elif suppress and not output:
            filename = datetime.now().strftime("subdomains-%Y-%m-%d-%H-%M-%S.csv")
            click.secho("[!] Suppress was active but no output was defined", bold=True, fg="yellow")
            click.secho(f"[!] Output was automatically generated", bold=True, fg="yellow")
            dump_filename(filename, concat_df)
        elif suppress and output:
            dump_filename(output, concat_df)


if __name__ == "__main__":
    cli()
