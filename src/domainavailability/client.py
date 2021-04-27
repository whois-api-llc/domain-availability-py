from json import loads, JSONDecodeError
import re

from .net.http import ApiRequester
from .models.response import DomainInfo
from .exceptions.error import ParameterError, EmptyApiKeyError, \
    UnparsableApiResponseError


class Client:
    __default_url = "https://domain-availability.whoisxmlapi.com/api/v1"
    __parsable_format = 'json'
    _api_requester: ApiRequester or None
    _api_key: str
    _mode: str
    _credits_type: str

    _re_api_key = re.compile(r'^at_[a-z0-9]{29}$', re.IGNORECASE)
    _re_output_format = re.compile(r'^(json)|(xml)$', re.IGNORECASE)
    _re_domain_name = re.compile(
        r'^(?:[0-9a-z_](?:[0-9a-z-_]{0,62}(?<=[0-9a-z-_])[0-9a-z_])?\.)+'
        + r'[0-9a-z][0-9a-z-]{0,62}[a-z0-9]$', re.IGNORECASE)

    DNS_AND_WHOIS_MODE = 'DNS_AND_WHOIS'
    DNS_ONLY_MODE = 'DNS_ONLY'

    WHOIS_CREDITS = 'WHOIS'
    DOMAIN_AVAILABILITY_CREDITS = 'DA'

    JSON_FORMAT = 'JSON'
    XML_FORMAT = 'XML'

    def __init__(self, api_key: str, **kwargs):
        """
        :param api_key: str: Your API key.
        :param credits_type: :str: (optional)
        :param mode: :str: (optional)
        :param base_url: str: (optional) API endpoint URL.
        :param timeout: float: (optional) API call timeout in seconds
        """
        self._api_key = ''
        self._mode = Client.DNS_AND_WHOIS_MODE
        self._credits_type = Client.WHOIS_CREDITS

        self.api_key = api_key

        if 'base_url' not in kwargs:
            kwargs['base_url'] = Client.__default_url

        if 'credits_type' in kwargs:
            self.credits_type = kwargs['credits_type']
        if 'mode' in kwargs:
            self.mode = kwargs['mode']

        self.api_requester = ApiRequester(**kwargs)

    @property
    def api_key(self) -> str:
        return self._api_key

    @api_key.setter
    def api_key(self, value: str):
        self._api_key = Client._validate_api_key(value)

    @property
    def api_requester(self) -> ApiRequester or None:
        return self._api_requester

    @api_requester.setter
    def api_requester(self, value: ApiRequester):
        self._api_requester = value

    @property
    def base_url(self) -> str:
        return self._api_requester.base_url

    @base_url.setter
    def base_url(self, value: str or None):
        if value is None:
            self._api_requester.base_url = Client.__default_url
        else:
            self._api_requester.base_url = value

    @property
    def credits_type(self) -> str:
        return self._credits_type

    @credits_type.setter
    def credits_type(self, value: str):
        try:
            self._credits_type = Client._validate_credits_type(value)
        except ParameterError as e:
            raise ValueError(e.message)

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, value: str):
        try:
            self._mode = Client._validate_mode(value)
        except ParameterError as e:
            raise ValueError(e.message)

    @property
    def timeout(self) -> float:
        return self._api_requester.timeout

    @timeout.setter
    def timeout(self, value: float):
        self._api_requester.timeout = value

    def data(self, domain: str, **kwargs) -> DomainInfo:
        """

        :param domain: - :str|IPv4Address: - the domain name
        :param mode: (optional) :str: Mode - use constants DNS_ONLY_MODE
            and DNS_AND_WHOIS_MODE
        :param credits_type: (optional) :str: - use constants
            WHOIS_CREDITS and DOMAIN_AVAILABILITY_CREDITS
        :return: DomainInfo
        :raises:
        - base class is DomainAvailabilityApiError
          - EmptyApiKeyError
          - ResponseError -- response contains an error message
          - ApiAuthError -- Server returned 401, 402 or 403 HTTP code
          - BadRequestError - Server returned 400 or 422 HTTP code
          - HttpApiError -- HTTP code >= 300 and not equal to above codes from
          - UnparsableApiResponseError -- the response couldn't be parsed
          - ParameterError -- invalid parameter's value
        - ConnectionError
        """

        kwargs['output_format'] = Client.__parsable_format

        response = self.raw_data(domain, **kwargs)
        try:
            parsed = loads(str(response))
            if 'DomainInfo' in parsed:
                return DomainInfo(parsed['DomainInfo'])
            raise UnparsableApiResponseError(
                "Could not find the correct root element.", None)
        except JSONDecodeError as error:
            raise UnparsableApiResponseError("Could not parse API response", error)

    def raw_data(self, domain: str, **kwargs) -> str:
        """

        :param domain: - :str|IPv4Address: - the domain name
        :param mode: (optional) :str: Mode - use constants DNS_ONLY_MODE
            and DNS_AND_WHOIS_MODE
        :param credits_type: (optional) :str: - use constants
            WHOIS_CREDITS and DOMAIN_AVAILABILITY_CREDITS
        :param output_format: - (optional) :str: use constants JSON_FORMAT
            and XML_FORMAT
        :return: str
        :raises
        - base class is domainavailability.exceptions.ReverseIpApiError
          - ResponseError -- response contains an error message
          - ApiAuthError -- Server returned 401, 402 or 403 HTTP code
          - BadRequestError - Server returned 400 or 422 HTTP code
          - HttpApiError -- HTTP code >= 300 and not equal to above codes
          - ParameterError -- invalid parameter's value
        - ConnectionError
        """
        if self.api_key == '':
            raise EmptyApiKeyError('')

        domain = Client._validate_domain_name(domain)

        if 'credits_type' in kwargs:
            credits_type = Client._validate_credits_type(
                kwargs['credits_type'])
        else:
            credits_type = self.credits_type

        if 'output_format' in kwargs:
            output_format = Client._validate_output_format(
                kwargs['output_format'])
        else:
            output_format = Client.__parsable_format

        if 'mode' in kwargs:
            mode = Client._validate_mode(kwargs['mode'])
        else:
            mode = self.mode

        return self._api_requester.get(self._build_payload(
            domain, credits_type, mode, output_format
        ))

    @staticmethod
    def _validate_api_key(api_key):
        if Client._re_api_key.search(
                str(api_key)
        ) is not None:
            return str(api_key)
        else:
            raise ParameterError("Invalid API key format.")

    @staticmethod
    def _validate_mode(value: str):
        if value.upper() not in [Client.DNS_AND_WHOIS_MODE,
                                 Client.DNS_ONLY_MODE]:
            raise ParameterError('Incorrect value.')
        return value.upper()

    @staticmethod
    def _validate_credits_type(value: str):
        if value.upper() not in [Client.WHOIS_CREDITS,
                                 Client.DOMAIN_AVAILABILITY_CREDITS]:
            raise ParameterError('Incorrect value.')
        return value.upper()

    @staticmethod
    def _validate_domain_name(domain):
        if domain is not None and len(str(domain)) > 0:
            if Client._re_domain_name.match(domain) is not None:
                return domain
        raise ParameterError('Invalid domain name.')

    @staticmethod
    def _validate_output_format(_format):
        if Client._re_output_format.search(str(_format)) is not None:
            return str(_format)
        else:
            raise ParameterError(
                "Output format should be either JSON or XML.")

    def _build_payload(self, domain, credits_type, mode, output_format):
        return {
            'apiKey': self.api_key,
            'domainName': domain,
            'credits': credits_type,
            'mode': mode,
            'outputFormat': output_format
        }
