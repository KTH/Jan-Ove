__author__ = 'tinglev@kth.se'

import unittest
from modules import util

class TestUtil(unittest.TestCase):

    def test_3_words_normal_quotes(self):
        test_data = 'new-season "name of season"'
        result = util.args_to_commands(test_data)
        self.assertEqual(len(result), 2)
        self.assertEqual(result, ['new-season', 'name of season'])

    def test_curly_quotes(self):
        test_data = 'new-season “name of season”'
        result = util.args_to_commands(test_data)
        self.assertEqual(len(result), 2)
        self.assertEqual(result, ['new-season', 'name of season'])

    def test_1_word_normal_quotes(self):
        test_data = 'new-season "season"'
        result = util.args_to_commands(test_data)
        self.assertEqual(len(result), 2)
        self.assertEqual(result, ['new-season', 'season'])

    def test_2_words_normal_quotes(self):
        test_data = 'new-season "season 1"'
        result = util.args_to_commands(test_data)
        self.assertEqual(len(result), 2)
        self.assertEqual(result, ['new-season', 'season 1'])

    def test_multiple_args_no_quotes(self):
        test_data = 'register-result @tinglev @hoyce 10 0'
        result = util.args_to_commands(test_data)
        self.assertEqual(len(result), 5)
        self.assertEqual(result, ['register-result',
                                  '@tinglev',
                                  '@hoyce',
                                  '10',
                                  '0'])
