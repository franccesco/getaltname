import pandas as pd


def strip_chars(subdomain_df):
    """Strip *.'s and www.'s"""
    subdomain_df = subdomain_df.str.lower()
    subdomain_df = subdomain_df.str.replace("www.", "")
    subdomain_df = subdomain_df.str.replace("\*.", "")
    return subdomain_df


def filter_domain(subdomain_df, domain):
    """Filter subdomains that don't match the domain name."""
    subdomain_df = subdomain_df[subdomain_df.str.endswith(f".{domain}")]
    return subdomain_df


def reindex_df(subdomain_df):
    """Reindex subdomain dataframe and starts at indice 1."""
    subdomain_df.drop_duplicates(inplace=True)
    subdomain_df.reset_index(drop=True, inplace=True)
    subdomain_df.index += 1
    return subdomain_df


def concat_dfs(subdomain_dfs, headers):
    """Concatenate, fill N/A's and rename columns."""
    concat_df = pd.concat(subdomain_dfs, axis="columns")
    concat_df.columns = [header.upper() for header in headers]
    concat_df.dropna(axis=1, how="all", inplace=True)
    return concat_df
