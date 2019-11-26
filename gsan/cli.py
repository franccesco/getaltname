import json
import ssl
from sys import exit

import OpenSSL
import click
import pandas as pd
from ndg.httpsclient.subj_alt_name import SubjectAltName
from pyasn1.codec.der import decoder

from gsan.crtsh import get_crtsh
from gsan.clean_df import reindex_df
from gsan.clean_df import concat_dfs
from gsan.output import dump_filename
from gsan.version import about_message
from gsan.clean_df import filter_domain


@click.group()
@click.version_option(version="4.0.0", message=about_message)
def cli():
    """Get subdomain names from SSL Certificates."""
    pass


@cli.command()
@click.argument("domains", nargs=-1)
@click.option("-m", "--match-domain", is_flag=True, help="Match domain name only.")
@click.option("-o", "--output", help="Output to path/filename.")
@click.option("-t", "--timeout", type=int, help="Set timeout for CRT.SH")
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
def scan_site(hostnames, port, match_domain, output):
    """Get domains directly from HTTPS server"""
    subdomains_data = []
    subjaltname = SubjectAltName()

    for hostname in hostnames:
        click.secho(f"[+] Getting subdomains for {hostname}", bold=True)
        subdomains = []
        try:
            cert = ssl.get_server_certificate((hostname, port))
        except Exception:
            click.secho(f"\n[!] Unable to connect to host {hostname}.", bold=True, fg="red")
            exit(1)

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
        subdomain_df = subdomain_df.str.lower()
        subdomain_df = subdomain_df.str.replace("www.", "")
        subdomain_df = subdomain_df.str.replace("\*.", "")
        subdomain_df.drop_duplicates(inplace=True)
        if match_domain:
            subdomain_df = subdomain_df[subdomain_df.str.endswith(f".{hostname}")]
        subdomain_df.reset_index(drop=True, inplace=True)
        subdomain_df.index += 1
        subdomains_data.append(subdomain_df)

    concat_df = pd.concat(subdomains_data, axis="columns")
    concat_df.fillna("", inplace=True)
    concat_df.columns = [header.upper() for header in hostnames]

    click.secho("[+] Results:", bold=True)
    print(concat_df.to_string())

    if output:
        dump_filename(output, concat_df)


if __name__ == "__main__":
    cli()
