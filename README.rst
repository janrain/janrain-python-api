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


Exceptions
~~~~~~~~~~

Exceptions are derived from ``JanrainApiException`` which includes error 
responses from the API. A try/catch bock should wrap any functions or methods 
that call the Janrain API.

.. code-block:: python

    try:
       result = api.call("entity.find", type_name="user")
    except janrain.capture.JanrainApiException as error:
       sys.exit(error.message)




----

Copyright © 2013 Janrain, Inc. All Rights Reserved.
