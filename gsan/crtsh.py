import json

import click
import pandas as pd
import requests

from gsan.clean_df import strip_chars


def get_crtsh(domain, timeout=30):
    try:
        crt_req = requests.get(f"https://crt.sh/?dNSName={domain}&output=json", timeout=timeout).json()
    except requests.exceptions.ConnectionError:
        click.secho("Failed to connect to CRT.SH, Try again.", bold=True, fg="red")
    crt_json = json.dumps(crt_req)

    if crt_json == "[]":
        empty_df = pd.DataFrame(columns={domain: ""})
        return empty_df

    subdomain_df = pd.read_json(crt_json)["name_value"]
    subdomain_df.replace(r"\n.*", "", regex=True, inplace=True)
    subdomain_df = strip_chars(subdomain_df)
    return subdomain_df
