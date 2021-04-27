import copy
from .base import BaseModel


def _string_value(values: dict, key: str) -> str:
    if key in values:
        return str(values[key])
    return ''


def _int_value(values: dict, key: str) -> int:
    if key in values:
        return int(values[key])
    return 0


def _list_value(values: dict, key: str) -> list:
    if key in values and type(values[key]) is list:
        return copy.deepcopy(values[key])
    return []


def _list_of_objects(values: dict, key: str, classname: str) -> list:
    r = []
    if key in values and type(values[key]) is list:
        r = [globals()[classname](x) for x in values[key]]
    return r


class DomainInfo(BaseModel):
    domain_availability: str
    domain_name: str

    __AVAILABLE = 'AVAILABLE'
    __UNAVAILABLE = 'UNAVAILABLE'

    def __init__(self, values):
        super().__init__()

        self.domain_availability = ''
        self.domain_name = ''

        if values is not None:
            self.domain_name = _string_value(values, 'domainName')
            self.domain_availability = _string_value(
                values, 'domainAvailability')

    def is_available(self) -> bool or None:
        """
        :returns: True if available, else False.
            If there is no value will return None.
        """
        if self.domain_availability == '':
            return None

        return self.domain_availability == DomainInfo.__AVAILABLE


class ErrorMessage(BaseModel):
    code: int
    message: str

    def __init__(self, values):
        super().__init__()

        self.int = 0
        self.message = ''

        if values is not None:
            self.code = _int_value(values, 'code')
            self.message = _string_value(values, 'messages')
