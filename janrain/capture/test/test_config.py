import unittest
import os
from janrain.capture import Api, config, JanrainConfigError

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
        """ Configuration can be referenced by cluster key """
        cluster = config.get_cluster("dev")
        self.assertTrue(isinstance(cluster, dict))
        self.assertIn('client_id', cluster)

    def test_merging(self):
        """ Cluster configuration gets merged into client configuration """
        client = config.get_client("cluster-client")
        self.assertTrue(isinstance(client, dict))
        self.assertEqual(client['client_id'], 'dev client_id')
        # client settings should not be overwritten
        self.assertEqual(client['apid_uri'], 'https://cluster.example.com')

    def test_defaults(self):
        """ Configuration files may have a default configuration """
        clients = []
        clients.append(config.default_client())
        for client in clients:
            self.assertTrue(isinstance(client, dict))
            self.assertIn('client_id', client)
            self.assertIn('client_secret', client)
            self.assertIn('apid_uri', client)

    def test_settings(self):
        """ Configuration can be referenced by cluster or by client """
        settings = config.get_settings('dev')
        self.assertTrue(isinstance(settings, dict))
        self.assertEqual(settings['client_id'], "dev client_id")
        with self.assertRaises(JanrainConfigError):
            config.get_settings_at_path("foobar")

        # test looking up clusters or clients with dot-notation
        settings = config.get_settings('clusters.dev')
        self.assertTrue(isinstance(settings, dict))
        self.assertEqual(settings['client_id'], "dev client_id")
        with self.assertRaises(JanrainConfigError):
            config.get_settings_at_path("foo.bar")

    def test_resolving_keys(self):
        """ Configuration can be referenced with dot-notation """
        client = config.get_settings_at_path("some.arbitrary.path")
        self.assertTrue(isinstance(client, dict))
        self.assertEqual(client['foo'], "bar")

        with self.assertRaises(JanrainConfigError):
            config.get_settings_at_path("foo.bar")

    def tearDown(self):
        # restore environment vars for remaining tests
        del os.environ['JANRAIN_CONFIG']
        if self.old_env:
            os.environ['JANRAIN_CONFIG'] = self.old_env
