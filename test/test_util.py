__author__ = 'tinglev@kth.se'

import unittest
from modules import util

class TestUtil(unittest.TestCase):

    def test_args_to_commands(self):
        test_data = 'new-season "name of season"'
        result = util.args_to_commands(test_data)
        self.assertEqual(len(result), 2)
        self.assertEqual(result, ['new-season', 'name of season'])
        test_data = 'register-result @tinglev @hoyce 10 0'
        result = util.args_to_commands(test_data)
        self.assertEqual(len(result), 5)
        self.assertEqual(result, ['register-result',
                                  '@tinglev',
                                  '@hoyce',
                                  '10',
                                  '0'])
