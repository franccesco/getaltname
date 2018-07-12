import io
import sys
import json
import unittest
from os import remove
from gsan.banner import banner
from gsan.get_san import get_san
from gsan.crt_sh import search_crt
from gsan.report import output, report_single, collect_report, nmap_output
from gsan.nmap_parsing import parse_nmap


class TestGetAltName(unittest.TestCase):
    """Tests if GSAN's modules works correctly."""

    def setUp(self):
        """Set up default values for tests."""
        self.hostname = 'starbucks.com'
        self.port = 443
        self.subdomain_set = get_san(self.hostname, self.port)
        self.example_xml = 'gsan/tests/test_nmap.xml'

    def test_get_san_single_host(self):
        """Test get_san() when invoked with a single host and port."""
        self.assertIsInstance(self.subdomain_set, set)
        self.assertTrue(self.hostname in self.subdomain_set)

    def test_get_san_failed(self):
        """Test if get_san() exits correctly with non-existant domain."""
        captured_text = io.StringIO()
        sys.stdout = captured_text
        with self.assertRaises(Exception):
            get_san(hostname='123oaenf.comasd', port=443)
        sys.stdout = sys.__stdout__

    def test_get_san_crt_sh_integration(self):
        """Test if get_san() returns domains from crt.sh."""
        subdomain_set = get_san(
            hostname=self.hostname,
            port=self.port,
            crt_sh=True,
            match=True
        )

        self.assertIsInstance(subdomain_set, set)
        self.assertTrue(len(subdomain_set) > 100)

    def test_get_san_return_empty_list(self):
        """Returns empty list if host from Nmap XML returned no SAN's."""
        subdomain_set = get_san(hostname='123oaenf.comasd',
                                port=self.port, xml_parse=True)
        self.assertIsInstance(subdomain_set, list)

    def test_crt_sh_timeout(self):
        """Test if timeout and message are displayed correctly."""
        captured_text = io.StringIO()
        sys.stdout = captured_text
        with self.assertRaises(SystemExit) as cm:
            print('Testing timeout in crt.sh:')
            search_crt('google.com', timeout=5)
        sys.stdout = sys.__stdout__
        exception = cm.exception
        self.assertEqual(exception.code, 1)

    def test_subdomain_output(self):
        """Test if subdomain list is output correctly."""
        output(subdomains=self.subdomain_set,
               format_output='text', destination='data.out',
               hostname=self.hostname)
        with open('data.out', 'r') as raw_data:
            subdomains_output = raw_data.read()
            # strip last '\n' from loaded file
            subdomains_output = subdomains_output[:-1]

        self.assertEqual(subdomains_output, '\n'.join(
            map(str, list(self.subdomain_set))))
        remove('data.out')

    def test_subdomain_output_json(self):
        """Test if subdomain output is in JSON."""
        output('', self.subdomain_set, 'json', 'data.out')
        with open('data.out', 'r') as json_data:
            self.assertTrue(json.load(json_data))
        remove('data.out')

    def test_subdomain_report(self):
        """Test if list output is correct."""
        captured_text = io.StringIO()
        sys.stdout = captured_text
        report_single(self.subdomain_set, self.hostname, 'text')
        sys.stdout = sys.__stdout__

    def test_subdomain_report_json(self):
        """Validates JSON output to stdout."""
        captured_text = io.StringIO()
        sys.stdout = captured_text
        report_single(self.subdomain_set, self.hostname, 'json')
        sys.stdout = sys.__stdout__
        json_data = json.dumps(captured_text.getvalue())
        self.assertTrue(json.loads(json_data))

    def test_report_no_sans_found(self):
        """Test if 'no sans found' message its displayed correctly."""
        captured_text = io.StringIO()
        sys.stdout = captured_text
        report_single([], '', 'text')
        sys.stdout = sys.__stdout__
        message = banner + "\n\x1b[41m\x1b[37mNo SAN's were found.\x1b[0m\n\n"
        self.assertEqual(captured_text.getvalue(), err_message)

    def test_collect_report(self):
        """Test nmap report method collect_report()."""
        report = collect_report(
            self.subdomain_set, self.hostname, self.port)
        self.assertIsInstance(report, str)

    def test_collect_report_empty(self):
        """Test if report return False on empty list."""
        report = collect_report([], self.hostname, self.port)
        self.assertFalse(report)

    def test_nmap_parsing(self):
        """Test if nmap XML output is parsed correctly."""
        hosts_dict = parse_nmap(self.example_xml)
        self.assertIsInstance(hosts_dict, dict)

    def test_nmap_output(self):
        """Test if output from nmap scan was successful."""
        domains = {}
        domains[self.hostname] = {'count': len(self.subdomain_set),
                                  'subdomains': list(self.subdomain_set)}
        nmap_output(domains, 'data.out')
        with open('data.out', 'r') as data:
            report = json.dumps(data.read())
        self.assertTrue(json.loads(report))
