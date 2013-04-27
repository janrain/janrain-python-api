import unittest
import os
from janrain.capture import Api, config

class TestConfig(unittest.TestCase):
    def setUp(self):
        # use the config file in this directory for config tests
        this_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(this_dir, "janrain-config")
        self.old_env = None
        if 'JANRAIN_CONFIG' in os.environ:
            self.old_env = os.environ['JANRAIN_CONFIG']
        os.environ['JANRAIN_CONFIG'] = config_file
    
    def test_clusters(self):
        # test referencing clusters
        cluster = config.get_cluster("dev")
        self.assertIn('client_id', cluster)
        
        # get_client() should merge the cluster if it is referenced instead of
        # an explicit client_id and client_secret
        client = config.get_client("cluster-client")
        self.assertEqual(client['client_id'], cluster['client_id'])
        
    def test_defaults(self):
        # test convenience funcitons for getting defaults
        clients = []
        clients.append(config.default_client())
        clients.append(config.unittest_client())
        for client in clients:
            self.assertIn('client_id', client)
            self.assertIn('client_secret', client)
            self.assertIn('apid_uri', client)
    
    def test_resolving_keys(self):
        # test resolving keys using dot-notation
        client = config.get_settings_at_path("some.arbitrary.path")
        self.assertEqual(client['foo'], "bar")
        
        with self.assertRaises(KeyError):
            config.get_settings_at_path("foo.bar")
        
    def tearDown(self):
        # restore environment vars for remaining tests
        del os.environ['JANRAIN_CONFIG']
        if self.old_env:
            os.environ['JANRAIN_CONFIG'] = self.old_env
        
        

