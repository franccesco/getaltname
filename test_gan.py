import unittest
from modules.get_san import get_san


class TestGetAltName(unittest.TestCase):
    """Tests if GAN's modules works correctly"""

    def setUp(self):
        """Set up default values for tests."""
        self.hostname = 'starbucks.com'
        self.port = 443

    def test_get_san_single_host(self):
        """Test get_san() when invoked with a single host and port."""
        subdomain_set = get_san(hostname=self.hostname, port=self.port)
        self.assertIsInstance(subdomain_set, set)
        self.assertTrue(self.hostname in subdomain_set)

    def test_get_san_failed(self):
        """Test if get_san() exits correctly with non-existant domain."""
        with self.assertRaises(SystemExit) as cm:
            print('Testing non-existant domain name:')
            get_san(hostname='123oaenf.comasd', port=443)
        exception = cm.exception
        self.assertEqual(exception.code, 1)

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


if __name__ == '__main__':
    unittest.main()
