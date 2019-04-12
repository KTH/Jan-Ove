__author__ = 'tinglev@kth.se'

import re
import datetime
import modules.slack as slack
import modules.database as database

def is_valid_command(command):
    for cmd in get_commands():
        if command == cmd['name']:
            return cmd
    return None

def cmd_top_3(split_commands):
    results = database.get_leaderboard()
    if not results or len(results) < 3:
        return 'Not enough data'
    output = 'The current top 3 players are:\n'
    output += f':trophy: {results[0].name}\n'
    output += f':second_place_medal: {results[1].name}\n'
    output += f':third_place_medal: {results[2].name}\n'
    return output

def cmd_register_user(split_commands):
    slack_mention = split_commands[1]
    slack_user_id = slack.mention_to_user_id(slack_mention)
    if not slack_user_id:
        return 'Invalid slack user id. Did you use a @ ?'
    if database.player_exists(slack_user_id):
        return 'A player with that name is already registered'
    database.register_player(slack_user_id)
    return f'The player "{slack_mention}" is now registered for play'

def cmd_register_result(split_commands):
    p1_slack_mention = split_commands[1]
    p2_slack_mention = split_commands[2]
    p1_score = split_commands[3]
    p2_score = split_commands[4]
    p1_row = database.get_player(p1_slack_mention)
    p2_row = database.get_player(p2_slack_mention)
    if not p1_row:
        return f'Player "{p1_slack_mention}" is not registered for play'
    if not p2_row:
        return f'Player "{p2_slack_mention}" is not registered for play'
    database.register_result(p1_row.playerid, p2_row.playerid, p1_score,
                             p2_score, datetime.datetime.now())
    return 'Result registered!'

def cmd_list_players(split_commands):
    players = database.get_all_players()
    if not players:
        return 'Not enough data'
    output = create_header_row([('Name', 20),
                                ('Slack handle', 20)])
    for player in players:
        output += create_row([(player.name, 20),
                              (f'{slack.user_id_to_mention(player.slackuserid)}', 20)])
    return output + '```\n'

def cmd_last_5_results(split_commands):
    results = database.get_last_5_results()
    if not results:
        return 'Not enough data'
    output = create_header_row([('Date', 20),
                                ('Player1', 20),
                                ('Player2', 20),
                                ('Result', 15)])
    for result in results:
        playedat = result.playedat.strftime('%Y-%m-%d %H:%M')
        output += create_row([(playedat, 20),
                              (result.p1_name, 20),
                              (result.p2_name, 20),
                              (f'{result.p1_score}-{result.p2_score}', 15)])
    return output + '```\n'

def cmd_leaderboard(split_commands):
    results = database.get_leaderboard()
    if not results:
        return 'Not enough data'
    output = create_header_row([('Name', 20),
                                ('Score', 10),
                                ('Games', 10),
                                ('Wins', 10),
                                ('Losses', 10),
                                ('Difference', 15)])
    for result in results:
        output += create_row([(result.name, 20),
                              (result.score, 10),
                              (result.games, 10),
                              (result.wins, 10),
                              (result.games - result.wins, 10),
                              (f'{result.wonpoints}-{result.lostpoints}', 15)])
    return output + '```\n'

def cmd_help(split_commands):
    help_text = 'Hi! These are commands that I understand:```'
    help_text += create_header_row([('Command', 20),
                                    ('Parameters', 60),
                                    ('Description', 0)])
    help_text += create_row([('register-player', 20),
                             ('slack_handle', 60),
                             ('Registers a slack user for play', 0)])
    help_text += create_row([('register-result', 20),
                             ('p1_slack_handle p2_slack_handle p1_score p2_score', 60),
                             ('Registers a played match', 0)])
    help_text += create_row([('list-players', 20),
                             ('', 60),
                             ('Lists all registered players', 0)])
    help_text += create_row([('last-5-results', 20),
                             ('', 60),
                             ('Lists the last 5 played games', 0)])
    help_text += create_row([('leaderboard', 20),
                             ('', 60),
                             ('Show the current leaderboard', 0)])
    help_text += create_row([('top-3', 20),
                             ('', 60),
                             ('Show the current top 3 players', 0)])
    return help_text + '```'

def create_row(tuple_array):
    row = '\n'
    for info in tuple_array:
        row += '{}'.format(info[0]).ljust(info[1])
    return row

def create_header_row(tuple_array):
    row = '```\n'
    row += create_row(tuple_array)
    row += create_separator_row(len(row))
    return row

def create_separator_row(width):
    return '\n' + ''.join(['-'] * width)

def get_commands():
    return [
        {
            'name': 'register-player',
            'params': 1,
            'func': cmd_register_user
        },
        {
            'name': 'list-players',
            'params': 0,
            'func': cmd_list_players
        },
        {
            'name': 'last-5-results',
            'params': 0,
            'func': cmd_last_5_results
        },
        {
            'name': 'register-result',
            'params': 4,
            'func': cmd_register_result
        },
        {
            'name': 'leaderboard',
            'params': 0,
            'func': cmd_leaderboard
        },
        {
            'name': 'top-3',
            'params': 0,
            'func': cmd_top_3
        },
        {
            'name': 'help',
            'params': 0,
            'func': cmd_help
        }
    ]
