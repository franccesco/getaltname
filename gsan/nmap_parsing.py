"""
Process Nmap XML Report.

Parse Nmap XML Output, the option '-sV' on Nmap
is necessary to detect SSL tunnels.
"""

import xml.etree.ElementTree as ET


def parse_nmap(nmap_xml):
    """Return hosts with HTTPS ports."""
    report = ET.parse(nmap_xml)
    hosts_to_scan = {}
    for host in report.iter('host'):
        ports = []
        for port in host[3].findall('port'):
            # find every port running a http + ssl service
            if 'http' and 'ssl' in port[1].attrib.values():
                # append every found port to a address
                ports.append(port.attrib['portid'])
                hosts_to_scan[host[1].attrib['addr']] = ports
    return hosts_to_scan
