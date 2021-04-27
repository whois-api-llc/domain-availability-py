.. image:: https://img.shields.io/badge/License-MIT-green.svg
    :alt: domain-availability-py license
    :target: https://opensource.org/licenses/MIT

.. image:: https://img.shields.io/pypi/v/domain-availability.svg
    :alt: domain-availability-py release
    :target: https://pypi.org/project/domain-availability

.. image:: https://github.com/whois-api-llc/domain-availability-py/workflows/Build/badge.svg
    :alt: domain-availability-py build
    :target: https://github.com/whois-api-llc/domain-availability-py/actions

========
Overview
========

The client library for
`Domain Availability API <https://domain-availability.whoisxmlapi.com/>`_
in Python language.

The minimum Python version is 3.6.

Installation
============

.. code-block:: shell

    pip install domain-availability

Examples
========

Full API documentation available `here <https://domain-availability.whoisxmlapi.com/api/documentation/making-requests>`_

Create a new client
-------------------

.. code-block:: python

    from domainavailability import *

    client = Client('Your API key')

Make basic requests
-------------------

.. code-block:: python

    # Get parsed records as a model instance.
    result = client.data('whoisxmlapi.com')
    print(result.domain_availability)
    if result.is_available() is True:
        print('This domain name is available.')

    # Get raw API response
    raw_result = client.raw_data('whoisxmlapi.com')

Advanced usage
-------------------

Extra request parameters

.. code-block:: python

    result = client.data(
        'whoisxmlapi.com',
        mode=Client.DNS_AND_WHOIS_MODE,
        credits_type=Client.DOMAIN_AVAILABILITY_CREDITS)

    raw_result = client.raw_data(
        'whoisxmlapi.com',
        mode=Client.DNS_ONLY_MODE,
        credits_type=Client.WHOIS_CREDITS,
        output_format=Client.XML_FORMAT)
