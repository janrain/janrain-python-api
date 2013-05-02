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
        current = current.get(chunk, {})
    if not current:
        raise JanrainConfigError("Could not find key '{}' in '{}'." \
                                 .format(dot_path, get_config_file()))
    merge_cluster(current)                   
    return current
    
def default_client():
    """
    Get the settings for the default client defined in the config file.
    
    Returns:
        A dictionary containing the default client settings.
    """
    config = read_config_file()
    try:
        client_name = config['defaults']['default_client']
    except KeyError:
        message = "Could not find key 'default_client' in '{}'." \
                  .format(get_config_file())
        raise JanrainConfigError(message)
                       
    return get_client(client_name)

def unittest_client():
    """
    Get the settings for the unittest client defined in the config file.
    
    Returns:
        A dictionary containing the default client settings.
    """
    config = read_config_file()
    try:
        client_name = config['defaults']['unittest_client']
    except KeyError:
        message = "Could not find key 'unittest_client' in '{}'." \
                  .format(get_config_file())
        raise JanrainConfigError(message)
                       
    return get_client(client_name)

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
        cluster = get_cluster(settings['cluster'])
        settings.update(cluster)
        
def read_config_file():
    """
    Parse the YAML configuration file into Python types. 
    
    Returns:
        A Python dictionary representing the YAML.
    """
    with open(get_config_file()) as stream:
        config = yaml.load(stream.read())
    return config
