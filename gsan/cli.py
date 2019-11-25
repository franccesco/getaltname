import json
import ssl
from sys import exit

import OpenSSL
import click
import pandas as pd
import requests
from ndg.httpsclient.subj_alt_name import SubjectAltName
from pyasn1.codec.der import decoder

from gsan.version import about_message

# TODO: Create methods to DRY code (cleaning df's)
# TODO: Integrate site method with crt.sh


@click.group()
@click.version_option(version="4.0.0", message=about_message)
def cli():
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
        crt_req = requests.get(f"https://crt.sh/?dNSName=%25{domain}&output=json", timeout=timeout).json()
        crt_json = json.dumps(crt_req)

        if crt_json == "[]":
            empty_df = pd.DataFrame(columns={domain: ""})
            subdomains_data.append(empty_df)
            continue
        subdomain_df = pd.read_json(crt_json)["name_value"]
        subdomain_df = subdomain_df.str.lower()
        subdomain_df = subdomain_df.str.replace("www.", "")
        subdomain_df = subdomain_df.str.replace("\*.", "")
        subdomain_df.drop_duplicates(inplace=True)

        if match_domain:
            subdomain_df = subdomain_df[subdomain_df.str.endswith(f".{domain}")]
        subdomain_df.reset_index(drop=True, inplace=True)
        subdomain_df.index += 1
        subdomains_data.append(subdomain_df)

    concat_df = pd.concat(subdomains_data, axis="columns")
    concat_df.fillna("", inplace=True)
    concat_df.columns = [header.upper() for header in domains]

    click.secho("[+] Results:", bold=True)
    print(concat_df.to_string())

    if output:
        output = output.lower()
        if output.endswith(".json"):
            click.secho(f"\n[+] Contents dumped into JSON file: {output}", bold=True)
            with open(output, "w+") as file_object:
                file_object.write(json.dumps(concat_df.to_dict(orient="list")))
        elif output.endswith(".csv"):
            click.secho(f"\n[+] Contents dumped into CSV file: {output}", bold=True)
            concat_df.to_csv(output, index=False)
        elif output == "cb":
            click.secho(f"\n[+] Contents dumped into clipboard.", bold=True)
            concat_df.to_clipboard(index=False)
        else:
            click.secho("\n[!] Extension not recognized, dumping using CSV format.", bold=True)
            concat_df.to_csv(output, index=False)


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
        except Exception as e:
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
        output = output.lower()
        if output.endswith(".json"):
            click.secho(f"\n[+] Contents dumped into JSON file: {output}", bold=True)
            with open(output, "w+") as file_object:
                file_object.write(json.dumps(concat_df.to_dict(orient="list")))
        elif output.endswith(".csv"):
            click.secho(f"\n[+] Contents dumped into CSV file: {output}", bold=True)
            concat_df.to_csv(output, index=False)
        elif output == "cb":
            click.secho(f"\n[+] Contents dumped into clipboard.", bold=True)
            concat_df.to_clipboard(index=False)
        else:
            click.secho("\n[!] Extension not recognized, dumping using CSV format.", bold=True)
            concat_df.to_csv(output, index=False)


@click.command()
def about():
    """Information and version number."""
    pass


if __name__ == "__main__":
    cli()
