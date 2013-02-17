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
    

Quick Start
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
``.apidrc`` file. This provides a simple way to authenticate API calls without
having to hard-code client_id and client_secret values.

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




----

Copyright © 2013 Janrain, Inc. All Rights Reserved.
