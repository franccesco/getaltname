import re


def parse_host_port(host_string):
    """Parse host:port into a tuple."""
    regex = re.compile(r"((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9])(:\d*)?", re.X)
    m = regex.match(host_string)
    addr, port = m.group(1, 2)
    try:
        return (addr, int(port[1:]))
    except TypeError:
        # port is None
        return (addr, None)
