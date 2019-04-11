__author__ = 'tinglev@kth.se'

import datetime
import modules.slack as slack
import modules.database as database

commands = ['register-player', 'register-result', 'help']

def cmd_register_user(channel, user, player_name):
    if player_name:
        if database.player_exists(player_name):
            return 'A player with that name is already registered'
        database.register_player(player_name)
        return f'The player "{player_name}" is now registered for play'

def cmd_register_result(channel, user, p1_name, p2_name, p1_score, p2_score):
    p1 = database.get_player(p1_name)
    p2 = database.get_player(p2_name)
    if not p1 or not p2:
        return 'One or more of the players are not registered for play'
    database.register_result(p1[0], p2[0], p1_score,
                             p2_score, datetime.datetime.now())
    return 'Result was registered!'

def cmd_help():
    help_text = 'Hi! These are commands that I understand:```'
    help_text += create_header_row([('Command', 20),
                                            ('Parameters', 40),
                                            ('Description', 0)])
    help_text += create_row([('register-player', 20),
                                     ('player_name', 40),
                                     ('Registers a player', 0)])
    help_text += create_row([('register-result', 20),
                                     ('p1_name p2_name p1_score p2_score', 40),
                                     ('Registers a played match', 0)])
    return help_text + '```'

def create_row(tuple_array):
    row = '\n'
    for info in tuple_array:
        row += '{}'.format(info[0]).ljust(info[1])
    return row


def create_header_row(tuple_array):
    row = create_row(tuple_array)
    row += create_separator_row(len(row))
    return row

def create_separator_row(width):
    return '\n' + ''.join(['-'] * width)
