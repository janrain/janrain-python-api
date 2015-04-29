Contributing
============

Testing
-------

If you are using a **virtualenv** run the following before running tests::

    python setup.py install

To run all tests::

    python setup.py nosetests --with-doctest

To run only doctests::

    python setup.py nosetests --doctest-tests

To run one specific test suite::

    python setup.py nosetests --tests janrain.capture.test.test_api

To run a specific unit test::

    python setup.py nosetests \
        --tests janrain.capture.test.test_api:TestApi.test_api_encode
