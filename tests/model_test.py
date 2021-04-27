import unittest
from json import loads
from domainavailability import DomainInfo, ErrorMessage


_json_response_ok_unavailable = '''{
   "DomainInfo": {
      "domainAvailability": "UNAVAILABLE",
      "domainName": "google.com"
   }
}'''

_json_response_ok_available = '''{
    "DomainInfo": {
        "domainAvailability": "AVAILABLE",
        "domainName": "dsajkdhksajhdkjsahdkjshakjdhsakdhksajhdsakdsadjksahdkjas.com"
    }
}'''

_json_response_error = '''{
    "code": 403,
    "messages": "Access restricted. Check credits balance or enter the correct API key."
}'''


class TestModel(unittest.TestCase):

    def test_response_parsing(self):
        response = loads(_json_response_ok_available)
        parsed = DomainInfo(response['DomainInfo'])
        assert parsed.domain_name == 'dsajkdhksajhdkjsahdkjshakjdhsakdhksajhdsakdsadjksahdkjas.com'
        assert parsed.domain_availability == 'AVAILABLE'
        assert parsed.is_available()

        response = loads(_json_response_ok_unavailable)
        parsed = DomainInfo(response['DomainInfo'])
        assert parsed.domain_name == 'google.com'
        assert parsed.domain_availability == 'UNAVAILABLE'
        assert parsed.is_available() is False

    def test_error_parsing(self):
        error = loads(_json_response_error)
        parsed_error = ErrorMessage(error)
        assert parsed_error.code == 403
        assert parsed_error.message == 'Access restricted. Check credits balance or enter the correct API key.'
