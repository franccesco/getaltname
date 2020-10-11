import json
import click
import pandas as pd


def dump_filename(filename, subdomain_df):
    """Output to CSV, JSON or Clipboard."""
    filename = filename.lower()
    if filename.endswith(".json"):
        click.secho(f"\n[+] Contents dumped into JSON file: {filename}", bold=True)
        with open(filename, "w+") as file_object:
            file_object.write(json.dumps(subdomain_df.to_dict(orient="list")))
    elif filename.endswith(".csv"):
        click.secho(f"\n[+] Contents dumped into CSV file: {filename}", bold=True)
        subdomain_df.to_csv(filename, index=False)
    elif filename == "cb":
        click.secho(f"\n[+] Contents dumped into clipboard.", bold=True)
        subdomain_df.to_clipboard(index=False)
    elif filename.endswith(".txt"):
        melted_df = pd.melt(subdomain_df).value.tolist()
        subdomains = [subdomain for subdomain in melted_df if str(subdomain) != "nan"]
        with open(filename, "w") as file_object:
            for subdomain in subdomains:
                file_object.write(f"{subdomain}\n")
        click.secho(f"\n[+] Contents dumped into a text file: {filename}", bold=True)
    else:
        click.secho("\n[!] Extension not recognized, dumping using CSV format.", bold=True)
        subdomain_df.to_csv(filename, index=False)
