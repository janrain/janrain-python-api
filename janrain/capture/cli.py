""" Command-line functions for interfacing with the Janrain API. """
# pylint: disable=C0301,W0142
import sys
import os
import json
import logging
from argparse import ArgumentParser, ArgumentError, HelpFormatter
from janrain.capture import Api, config, get_version, ApiResponseError, \
                            JanrainCredentialsError, JanrainConfigError

class ApiArgumentParser(ArgumentParser):
    """
    A subclass of the argparse.ArgumentParser in the standard library. Adds the
    common command-line options for authenticating with the Janrain API and 
    allows for an janrain.capture.Api instance to be initialized using those
    credentials.

    Example:

        parser = janrain.capture.cli.ApiArgumentParser()
        args = parser.parse_args()
        api = parser.init_api()

    """
    def __init__(self, *args, **kwargs):
        super(ApiArgumentParser, self).__init__(*args, **kwargs)
        self._parsed_args = None

        # credentials explicitly specified on the command line
        self.add_argument('-u', '--apid_uri',
                          help="Full URI to the Capture API domain")
        self.add_argument('-i', '--client-id',
                          help="authenticate with a specific client_id")
        self.add_argument('-s', '--client-secret',
                          help="authenticate with a specific client_secret")

        # credentials defined in config file at the specified path
        self.add_argument('-k', '--config-key',
                          help="authenticate using the credentials defined at "\
                               "a specific path in the configuration file "    \
                               "(eg. clients.demo)")

        # default client found in the configuration file
        self.add_argument('-d', '--default-client', action='store_true',
                          help="authenticate using the default client defined "\
                               "in the configuration file")

    def parse_args(self, args=None, namespace=None):
        # override to store the result which can later be used by init_api()
        args = super(ApiArgumentParser, self).parse_args(args, namespace)
        self._parsed_args = args
        return self._parsed_args

    def init_api(self, api_class=None):
        """
        Initialize a janrain.capture.Api() instance for the credentials that
        were specified on the command line or environment variables. This
        method will use the first credentials it finds, looking in the
        following order:

        1. A client_id and client_secret specified on the command line
        2. A configuration key specified on the command line
        3. The default client as specified with a flag on the command line
        4. The CAPTURE_CLIENT_ID and CAPTURE_CLIENT_SECRET environment vars

        Returns:
            A janrain.capture.Api instance

        """
        if not self._parsed_args:
            raise Exception("You must call the parse_args() method before " \
                            "the init_api() method.")

        args = self._parsed_args

        if args.client_id and args.client_secret:
            credentials = {
                'client_id': args.client_id,
                'client_secret': args.client_secret
            }

        elif args.config_key:
            credentials = config.get_settings(args.config_key)

        elif args.default_client:
            credentials = config.default_client()

        elif 'CAPTURE_CLIENT_ID' in os.environ \
            and 'CAPTURE_CLIENT_SECRET' in os.environ:
            credentials = {
                'client_id': os.environ['CAPTURE_CLIENT_ID'],
                'client_secret': os.environ['CAPTURE_CLIENT_SECRET']
            }

        else:
            message = "You did not specify credentials to authenticate " \
                      "with the Capture API."
            raise JanrainCredentialsError(message)

        if args.apid_uri:
            credentials['apid_uri'] = args.apid_uri

        elif 'apid_uri' not in credentials:
            if 'CAPTURE_APID_URI' in os.environ:
                credentials['apid_uri'] = os.environ['CAPTURE_APID_URI']
            else:
                message = "You did not specify the URL to the Capture API"
                raise JanrainCredentialsError(message)

        defaults = {k: credentials[k] for k in ('client_id', 'client_secret')}

        if api_class:
            return api_class(credentials['apid_uri'], defaults)
        else:
            return Api(credentials['apid_uri'], defaults)


def main():
    """
    Main entry point for CLI. This may be called by running the module directly
    or by an executable installed onto the system path.
    """
    parser = ApiArgumentParser(formatter_class=lambda prog: HelpFormatter(prog,max_help_position=30))
    parser.add_argument('api_call',
                        help="API endpoint expressed as a relative path " \
                             "(eg. /settings/get).")
    parser.add_argument('-p', '--parameters', nargs='*',
                        metavar="parameter=value",
                        help="parameters passed through to the API call")
    parser.add_argument('-v', '--version', action='version',
                        version="capture-api " + get_version())
    parser.add_argument('-x', '--disable-signed-requests', action='store_true',
                        help="sign HTTP requests")
    parser.add_argument('-b', '--debug', action='store_true',
                        help="log debug messages to stdout")
    args = parser.parse_args()

    try:
        api = parser.init_api()
    except (JanrainConfigError, JanrainCredentialsError) as error:
        sys.exit(str(error))

    if args.disable_signed_requests:
        api.sign_requests = False

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    # map list of parameters from command line into a dict for use as kwargs
    kwargs = {}
    if args.parameters:
        kwargs = dict((key, value) for key, value in [s.split("=", 1)
                      for s in args.parameters])

    try:
        data = api.call(args.api_call, **kwargs)
    except ApiResponseError as error:
        sys.exit("API Error {} - {}\n".format(error.code, str(error)))

    print(json.dumps(data, indent=2, sort_keys=True))

    sys.exit()

if __name__ == "__main__":
    main()
