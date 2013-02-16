import yaml
import os

def load_config_file():
    yaml_file = os.path.join(os.path.expanduser("~"), ".apidrc")
    
    with open(yaml_file) as stream:
        config = yaml.load(stream.read())
    
    return config
        
def default(auth_only=True):
    config = load_config_file()
    return config['clients'][config['defaults']['default_client']]
        
    
