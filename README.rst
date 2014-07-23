Janrain Python API
==================

[![Build Status](https://travis-ci.org/janrain/janrain-python-api.png?branch=master)](https://travis-ci.org/janrain/janrain-python-api)

Python interface to the
`Janrain Capture <http://janrain.com/products/capture/>`_ API.


Install
-------

Download and install the most recent stable version using ``pip``::

    pip install janrain-python-api


To use the unstable developement version, download the package by cloning the git repository::

    git clone https://github.com/janrain/janrain-python-api.git
    cd janrain-python-api
    python setup.py install


Basic Usage
-----------

Low-Level API Calls
~~~~~~~~~~~~~~~~~~~

Use ``janrain.capture.Api`` to make low-level calls to the API.

.. code-block:: python

    from janrain.capture import Api

    defaults = {
        'client_id': "YOUR_CLIENT_ID",
        'client_secret': "YOUR_CLIENT_SECRET"
    }

    api = Api("https://YOUR_APP.janraincapture.com", defaults)
    result = api.call("entity.count", type_name="user")
    print(result)


Exceptions
~~~~~~~~~~

Exceptions are derived from ``JanrainApiException`` which includes error
responses from the API. A try/catch bock should wrap any functions or methods
that call the Janrain API.

.. code-block:: python

    from janrain.capture import Api, ApiResponseError
    from requests import HTTPError

    defaults = {
        'client_id': "YOUR_CLIENT_ID",
        'client_secret': "YOUR_CLIENT_SECRET"
    }

    api = Api("https://YOUR_APP.janraincapture.com", defaults)

    try:
        result = api.call("entity.find", type_name="user")
    except janrain.capture.ApiResponseError as error:
        # Janrain API returned an error response
        sys.exit(str(error))
    except HTTPError as error:
        # Python 'requests' library returned an error
        sys.exit(str(error))


Argument Parser
~~~~~~~~~~~~~~~

The library includes a subclass of the Python
`argparse <https://docs.python.org/dev/library/argparse.html>`_ configured to
accept credentials for authenticating with the Janrain API. This can be used to
simplify passing in credentials in custom command-line scripts.

.. code-block:: python

    from janrain.capture import cli

    parser = cli.ApiArgumentParser()
    args = parser.parse_args()
    api = parser.init_api()

Which can then invoke from the command-line as follows::

    python myscript.py  --api-url=[YOUR_CAPTURE_URL] \
                        --client-id=[YOUR_CLIENT_ID] \
                        --client-secret=[YOUR_CLIENT_SECRET] \


Command-Line Utility
--------------------

The package installs an executable named ``capture-api`` for making
API calls from the command-line.

Authenticate with the API by passing ``--api-url``, ``--client-id``,
and ``--client-secret``, then pass the API call, and then any parameters to
send to the API as key=value pairs after the ``--parameters`` argument.

Examples
~~~~~~~~

Passing the authentication credentials::

    capture-api --api-url=[YOUR_CAPTURE_URL] \
                --client-id=[YOUR_CLIENT_ID] \
                --client-secret=[YOUR_CLIENT_SECRET] \
                entity.count --parameters type_name=user

Enclose JSON values in single outer-quotes and double inner-quotes::

    capture-api --api-url=[YOUR_CAPTURE_URL] \
                --client-id=[YOUR_CLIENT_ID] \
                --client-secret=[YOUR_CLIENT_SECRET] \
                entity.find --parameters type_name=user \
                attributes='["displayName","email"]'

Enclose filters in double outer-quotes and single inner-quotes::

    capture-api --api-url=[YOUR_CAPTURE_URL] \
                --client-id=[YOUR_CLIENT_ID] \
                --client-secret=[YOUR_CLIENT_SECRET] \
                entity.find --parameters type_name=user \
                filter="email = 'demo@janrain.com' and birthday is null"

----

Versioning
----------
This software follows Semantic Versioning convention.
http://semver.org/


Copyright © 2014 Janrain, Inc. All Rights Reserved.
