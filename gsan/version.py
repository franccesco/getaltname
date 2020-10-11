import click

banner = click.style(
    """
 _____ _____ _____ _____
|   __|   __|  _  |   | |
|  |  |__   |     | | | |
|_____|_____|__|__|_|___|""",
    bold=True,
    fg="red",
)

version = click.style(" v4.2.3\n\n", bold=True, fg="green")
author = click.style("Author:  ", bold=True) + "Franccesco Orozco\n"
email = click.style("Email:   ", bold=True) + "franccesco@codingdose.info\n"
website = click.style("Website: ", bold=True) + "https://codingdose.info"
about_message = banner + version + author + email + website
