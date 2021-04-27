import os
import unittest
from domainavailability import Client
from domainavailability import ParameterError, ApiAuthError


class TestClient(unittest.TestCase):
    """
    Final integration tests without mocks.

    Active API_KEY is required.
    """
    def test_get_correct_data(self):
        client = Client(os.getenv("API_KEY"))

        domain = 'whoisxmlapi.com'
        result = client.data(domain)
        assert result.domain_name == domain
        assert result.domain_availability == 'UNAVAILABLE'
        assert not result.is_available()
        result = client.data(
            domain,
            mode=Client.DNS_AND_WHOIS_MODE,
            credits_type=Client.WHOIS_CREDITS)
        assert not result.is_available()

    def test_get_raw_data(self):
        client = Client(os.getenv("API_KEY"))
        raw = client.raw_data(
            'whoisxmlapi.com', output_format=Client.XML_FORMAT)
        assert raw.startswith('<?xml')

    def test_get_auth_error(self):
        client = Client('at_00000000000000000000000000000')
        self.assertRaises(ApiAuthError, client.data, 'whoisxmlapi.com')
        try:
            client.data('whoisxmlapi.com')
        except ApiAuthError as error:
            parsed = error.parsed_message
            assert parsed.code == 403

    def test_get_parameter_error(self):
        client = Client(os.getenv('API_KEY'))
        domain = 'whoisxmlapi.com'
        self.assertRaises(ParameterError, client.data, 'incorrect-domain')

        with self.assertRaises(ParameterError):
            client.raw_data(domain, output_format='pdf')
        with self.assertRaises(ParameterError):
            client.data(domain, mode='full')
        with self.assertRaises(ParameterError):
            client.data(domain, credits_type='drs')


if __name__ == '__main__':
    unittest.main()
