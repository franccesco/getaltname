import ssl
from sys import exit

import OpenSSL
import click
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


@click.group()
@click.version_option(version="4.0.0", message=about_message)
def cli():
    """Get subdomain names from SSL Certificates."""
    pass


@cli.command()
@click.argument("domains", nargs=-1)
@click.option("-m", "--match-domain", is_flag=True, help="Match domain name only.")
@click.option("-o", "--output", help="Output to path/filename.")
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


@cli.command("site")
@click.argument("hostnames", nargs=-1)
@click.option("-p", "--port", default=443)
@click.option("-o", "--output", help="Output to path/filename.")
@click.option("-m", "--match-domain", is_flag=True, help="Match domain name only.")
@click.option("-c", "--crtsh", is_flag=True, help="Include results from CRT.SH")
def scan_site(hostnames, port, match_domain, output, crtsh):
    """Get domains directly from HTTPS server"""
    subdomains_data = []
    subjaltname = SubjectAltName()

    for hostname in hostnames:
        click.secho(f"[+] Getting subdomains for {hostname}", bold=True)
        subdomains = []
        try:
            cert = ssl.get_server_certificate((hostname, port))
        except Exception:
            click.secho(f"[!] Unable to connect to host {hostname}", bold=True, fg="red")

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
            crtsh_results = get_crtsh(hostname)
            subdomain_df = pd.concat([subdomain_df, crtsh_results])
        if subdomains:
            subdomain_df = strip_chars(subdomain_df)
        if match_domain:
            subdomain_df = filter_domain(subdomain_df, hostname)
        subdomain_df = reindex_df(subdomain_df)
        subdomains_data.append(subdomain_df)

    concat_df = concat_dfs(subdomains_data, hostnames)
    click.secho("[+] Results:", bold=True)
    print(concat_df.to_string())

    if output:
        dump_filename(output, concat_df)


if __name__ == "__main__":
    cli()
