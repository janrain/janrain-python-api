from janrain.capture.api import Api
from janrain.capture.exceptions import *

VERSION = (0, 2, 3)

def get_version():
    return "%s.%s.%s" % (VERSION[0], VERSION[1], VERSION[2])

__version__ = get_version()
