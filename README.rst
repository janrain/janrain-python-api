Janrain Python API
==================

Python interface to the 
`Janrain Capture <http://janrain.com/products/capture/>`_ API.


Install
-------

Download the package by cloning the git repository::

    git clone https://github.com/janrain/janrain-python-api.git
    cd janrain-python-api

Then install it using ``setup.py``::

    python setup.py install
    

Basic Usage
-----------

Low-Level API Calls
~~~~~~~~~~~~~~~~~~~

Use ``janrain.capture.Api`` to make low-level calls to the API. 

.. code-block:: python

    import janrain.capture.Api
    
    defaults = {
        'client_id': "YOUR_CLIENT_ID", 
        'client_secret': "YOUR_CLIENT_SECRET"
    }
    
    api = janrain.capture.Api("http://YOUR_APP.janraincapture.com", defaults)
    result = api.call("entity.count", type_name="user")
    print(result)

Configuration File
~~~~~~~~~~~~~~~~~~

The ``config`` module includes utilities for reading configuration data from the 
``.janrain-capture`` file. This provides a simple way to authenticate API calls 
without having to hard-code client_id and client_secret values.

.. code-block:: python

    from janrain.capture import Api, config
    
    client = config.default_client()
    api = Api(client['apid_uri'], {
        'client_id': client['client_id'],
        'client_secret': client['client_secret']
    })
    result = api.call("entity.count", type_name="user")
    print(result)

Exceptions
~~~~~~~~~~

Exceptions are derived from ``JanrainApiException`` which includes error 
responses from the API. A try/catch bock should wrap any functions or methods 
that call the Janrain API.

.. code-block:: python

    try:
        result = api.call("entity.find", type_name="user")
    except janrain.capture.InvalidApiCallError as error:
        # 404 error
        sys.exit("Invalid API Endpoint: " + error.message)
    except janrain.capture.ApiResponseError as error:
        # API returned an error response
        sys.exit("API Error: " + message)


Command-Line Utility
--------------------

The package installs an executable named ``capture-api`` for accessing making
API calls from the command-line. 

If you have the ``.janrain-capture`` configuration file, you can specify the client using
the ``--client`` argument. Otherwise you will need to specify ``--api-url``,
``--client-id``, and ``--client-secret``. 

All parameters should be passed as key=value pairs after the ``--parameters``
argument. 

Examples
~~~~~~~~

Using the client defined in ``.janrain-capture`` file::
 
    capture-api --client=demo entity.count --parameters type_name=user

Passing the authentication credentials::

    capture-api --api-url=[YOUR_CAPTURE_URL] \
                --client-id=[YOUR_CLIENT_ID] \
                --client-secret=[YOUR_CLIENT_SECRET] \
                entity.count --parameters type_name=user

Enclose JSON values in single outer-quotes and double inner-quotes::

    capture-api --client=demo entity.find --parameters type_name=user \
                attributes='["displayName","email"]'

Enclose filters in double outer-quotes and single inner-quotes::

    capture-api --client=demo entity.find --parameters type_name=user \
                filter="email = 'demo@janrain.com' and birthday is null"

----

Copyright © 2013 Janrain, Inc. All Rights Reserved.
