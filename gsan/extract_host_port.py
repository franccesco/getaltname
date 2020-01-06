import re


def parse_host_port(host_string):
    """Parse host:port into a tuple."""
    regex = re.compile(r"(\[[:a-fA-F0-9]+\]|(?:\d{1,3}\.){3}\d{1,3}|[a-zA-Z0-9.]+)(?::(\d+))?", re.X)
    m = regex.match(host_string)
    addr, port = m.group(1, 2)
    try:
        return (addr, int(port))
    except TypeError:
        # port is None
        return (addr, None)
