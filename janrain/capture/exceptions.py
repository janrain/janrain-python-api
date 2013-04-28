""" Exceptions for the Janrain API library. """

class JanrainApiException(Exception):
    """ Base class for all Janrain API exceptions. """
    pass

class JanrainCredentialsError(Exception):
    """ Exception for credential errors (eg. Missing credentials) """
    pass

class JanrainConfigError(Exception):
    """ Exception for credential configuration file errors """
    pass
    
class InvalidApiCallError(JanrainApiException):
    """ Request for a non-existing API call. """
    def __init__(self, api_call, status):
        message = "Invalid API call: {} ({})".format(api_call, status)
        JanrainApiException.__init__(self, message)

class JanrainInvalidUrlError(JanrainApiException):
    """ Invalid URL. """
    pass
    
class ApiResponseError(JanrainApiException):
    """ An error response from the capture API. """
    def __init__(self, code, error, error_description, response):
        JanrainApiException.__init__(self, error_description)
        self.code = code
        self.error = error
        self.response = response
