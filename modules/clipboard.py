"""
Copy the output to clipboard as a list or single string.

this is a handy way of pasting your newly found subdomains
into other tools that does not accept file input.
"""

import pyperclip


def clipboard_output(subdomain_list, output_style):
    """Copy to clipboard, 's' for string and 'l' for list."""
    if output_style == 's':
        pyperclip.copy(' '.join(subdomain_list))
    elif output_style == 'l':
        pyperclip.copy('\n'.join(subdomain_list))
