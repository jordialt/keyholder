import unittest
from unittest.mock import patch, mock_open
import os
import sys

import main

class TestKeyholder(unittest.TestCase):

    @patch('main.CONFIG_PATH', '/tmp/.keyholder_test.json')
    def setUp(self):
        self.test_json_path = '/tmp/.keyholder_test.json'
        if os.path.exists(self.test_json_path):
            os.remove(self.test_json_path)
            
        # Ensure we're using the mock path for all main module calls in these tests
        main.CONFIG_PATH = self.test_json_path

    def tearDown(self):
        if os.path.exists(self.test_json_path):
            os.remove(self.test_json_path)

    def test_set_and_load_keys(self):
        main.set_key('test_service', 'test_key_123')
        keys = main.load_keys()
        self.assertIn('test_service', keys)
        self.assertEqual(keys['test_service'], 'test_key_123')

    @patch('pyperclip.copy')
    def test_get_key(self, mock_copy):
        main.set_key('test_service', 'test_key_123')
        main.get_key('test_service')
        mock_copy.assert_called_once_with('test_key_123')

    def test_get_key_not_found(self):
        with self.assertRaises(SystemExit) as cm:
            main.get_key('nonexistent_service')
        self.assertEqual(cm.exception.code, 1)

    def test_remove_key(self):
        main.set_key('s1', 'k1')
        main.set_key('s2', 'k2')
        main.remove_key('s1')
        keys = main.load_keys()
        self.assertNotIn('s1', keys)
        self.assertIn('s2', keys)

if __name__ == '__main__':
    unittest.main()
