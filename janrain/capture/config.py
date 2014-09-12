""" Utilities for working with the Janrain API configuration file. """
import yaml
import os
from janrain.capture.exceptions import JanrainConfigError

def get_settings_at_path(dot_path):
    """
    Get the settings for the specified YAML path.

    Args:
        dot_path - A YAML path string in dot-notation (Eg. "clusters.dev")

    Returns:
        A dictionary containing the settings at the specified path.

    Raises:
        KeyError if the path does not exist
    """
    yaml_dict = read_config_file()
    current = yaml_dict
    for chunk in dot_path.split('.'):
        current = current[chunk]
    merge_cluster(current)
    return current

def default_client():
    """
    Get the settings for the default client defined in the config file.

    Returns:
        A dictionary containing the default client settings.
    """
    return get_client(read_config_file()['defaults']['default_client'])

def unittest_client():
    """
    Get the settings for the unittest client defined in the config file.

    Returns:
        A dictionary containing the default client settings.
    """
    return get_client(read_config_file()['defaults']['unittest_client'])

def client(client_name):
    """ DEPRECATED """
    return get_client(client_name)

def get_client(client_name):
    """
    Get the settings defined for the specified client.

    Args:
        client_name - The name of the client defined in the the config file

    Returns:
        A dictionary containing the client settings.
    """
    client = get_settings_at_path("clients." + client_name)
    merge_cluster(client)

    return client

def cluster(cluster_name):
    """ DEPRECATED """
    return get_cluster(cluster_name)

def get_cluster(cluster_name):
    """
    Get the settings defined for the specified cluster.

    Args:
        cluster_name - The name of the cluster defined in the config file
                       (Eg. "prod" or "eu_staging")

    Returns:
        A dictionary containing the cluster settings.
    """
    return get_settings_at_path("clusters." + cluster_name)

def get_clusters():
    """
    Get the list of all clusters.

    Returns:
        A dictionary containing the cluster settings.
    """
    return get_settings_at_path("clusters")

def get_config_file():
    """
    Get the full path to the config file. By default, this is a YAML file named
    `.janrain-capture`` located in the user's home directory. Override the
    default file by specifying a full path to a YAML file in the JANRAIN_CONFIG
    environment variable.
    """
    try:
        return os.environ['JANRAIN_CONFIG']
    except KeyError:
        return os.path.join(os.path.expanduser("~"), ".janrain-capture")

def merge_cluster(settings):
    """
    Merge the cluster settings into the dictionary if a 'clusters' key exists.

    Args:
        settings - The settings to dictionary to merge cluster setings into.
    """
    if 'cluster' in settings:
        # merge in cluster values
        settings.update(get_cluster(settings['cluster']))

def read_config_file():
    """
    Parse the YAML configuration file into Python types.

    Returns:
        A Python dictionary representing the YAML.
    """
    file = get_config_file()
    with open(file) as stream:
        yaml_dict = yaml.load(stream.read())
    return ConfigDict(file, yaml_dict)

from collections import MutableMapping

class ConfigDict(MutableMapping):
    def __init__(self, file, values={ }, root = ''):
        self.file = file
        self.root = root
        self.values = { }
        for key, value in values.items():
            try:
                self.values[key] = ConfigDict(file, value, self.get_key_path(key))
            except:
                self.values[key] = value

    def __len__(self):
        return len(self.values)

    def __iter__(self):
        return iter(self.values)

    def __getitem__(self, key):
        try:
            return self.values[key]
        except KeyError:
            raise JanrainConfigError(key=self.get_key_path(key), file=self.file)

    def __contains__(self, key):
        return key in self.values

    def __setitem__(self, key, value):
        self.values[key] = value

    def __delitem__(self, key):
        del self.values[key]

    def get_key_path(self, key):
        return self.root + '.' + key if self.root else key
