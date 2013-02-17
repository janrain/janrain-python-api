""" Command-line utility for interfacing with the Janrain API. """
# pylint: disable=C0301,W0142
import sys
import argparse
import json
from janrain.capture import Api, config, ApiResponseError

def parse_args():
    """
    Return populated argument parser namespace.
    """
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-c', '--cluster',
                        help="Use the client_id and client_secret defined in the .apidrc file.")
    parser.add_argument('-i', '--client-id',
                        help="The client_id to use when making the API call.")
    parser.add_argument('-s', '--client-secret',
                        help="The client_secret to use when making the API call.")
    parser.add_argument('api_url', 
                        help="The full URL to the apid server.")
    parser.add_argument('api_call', 
                        help="The API endpoint to call.")
    parser.add_argument('-p', '--parameters', nargs='*', metavar="parameter=value",
                        help="parameters passed on to the API call")
    return parser.parse_args()
    
def main():
    """
    Main entry point for CLI. This may be called by running the module directly
    or by an executable installed onto the system path.
    """
    args = parse_args()
    
    # Get authentication which should either be a cluster defined in the 
    # .apidrc or an explicity passed client_id and client_secret
    if args.cluster:
        try:
            defaults = config.cluster(args.cluster)
        except KeyError as error:
            sys.exit(str(error))
    elif args.client_id and args.client_secret:
        defaults = {
            'client_id': args.client_id, 
            'client_secret': args.client_secret
        }
    else:
        sys.exit("You must pass --cluster as defined in the .apidrc file " \
                 "or pass --client-id and --client-secret.")   
    api = Api(args.api_url, defaults)
    
    # map list of parameters from command line into a dict for use as kwargs
    kwargs = {}
    if args.parameters:
        kwargs = dict((key, value) for key, value in [s.split("=", 1) 
                      for s in args.parameters])
    
    try:
        data = api.call(args.api_call, **kwargs)
    except ApiResponseError as error:
        sys.exit("Error {} - {}\n".format(error.code, error.message))
    except Exception as error:
        sys.exit("Error - {}\n".format(error))
    
    print(json.dumps(data, indent=2, sort_keys=True))
    
    sys.exit()

if __name__ == "__main__":
    main()
