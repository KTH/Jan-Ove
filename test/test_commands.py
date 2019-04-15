__author__ = 'tinglev@kth.se'

import os
import unittest
from unittest.mock import MagicMock
from modules import commands

class TestCommands(unittest.TestCase):

    def setUp(self):
        commands.get_commands = MagicMock()
        commands.get_commands.return_value = [
            {
                'name': 'active-cmd',
                'params': 1,
                'param_names': '@slack-name',
                'help_text': 'Registers a slack user for play',
                'func': None,
                'active': True
            },
            {
                'name': 'not-active-cmd',
                'params': 0,
                'param_names': '',
                'help_text': 'List all registered players',
                'func': None,
                'active': False
            }
        ]

    def test_active_command(self):
        self.assertTrue(commands.is_valid_command('active-cmd'))

    def test_inactive_command(self):
        self.assertFalse(commands.is_valid_command('not-active-cmd'))

    def test_bad_commands(self):
        self.assertFalse(commands.is_valid_command('cmd-that-doesnt-exist'))
