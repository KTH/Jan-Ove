__author__ = 'tinglev@kth.se'

import os
import unittest
from modules import slack

class TestSlack(unittest.TestCase):

    def test_mention_to_user_id(self):
        test_data = '<@U11351>'
        result = slack.mention_to_user_id(test_data)
        self.assertEqual(result, 'U11351')

    def test_user_id_to_mention(self):
        test_data = 'U11ABC'
        result = slack.user_id_to_mention(test_data)
        self.assertEqual(result, '<@U11ABC>')

    def test_message_is_command(self):
        test_data = {
            'text': 'Not a command',
            'user': 'U12345',
            'channel': '#test'
        }
        result = slack.message_is_command(test_data)
        self.assertEqual(result, (None, None, None))
        test_data['text'] = '!pingis test'
        result = slack.message_is_command(test_data)
        self.assertEqual(result, ('test', 'U12345', '#test'))
        os.environ['BOT_TRIGGER'] = '€new_trigger'
        test_data['text'] = '€new_trigger test2'
        result = slack.message_is_command(test_data)
        self.assertEqual(result, ('test2', 'U12345', '#test'))
