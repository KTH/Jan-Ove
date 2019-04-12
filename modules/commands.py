__author__ = 'tinglev@kth.se'

import re
import datetime
import modules.slack as slack
import modules.database as database

def get_commands():
    return [('register-player', 1),
            ('register-result', 4),
            ('list-players', 0),
            ('last-5-results', 0),
            ('leaderboard', 0),
            ('top-3', 0),
            ('help', 0)]

def is_valid_command(command):
    for (cmd, _) in get_commands():
        if command == cmd:
            return True
    return False

def get_command_arguments(command):
    for (cmd, args) in get_commands():
        if command == cmd:
            return args
    return -1

def cmd_top_3():
    tuplelist = add_score_to_leaderboard(database.get_leaderboard())
    if not tuplelist:
        return 'Not enough data'
    cols = get_leaderboard_cols()
    output = 'The current top 3 players are:\n'
    for index, player in enumerate(tuplelist, 1):
        if index == 1:
            output += f':trophy: {player[cols["name"]]}\n'
        elif index == 2:
            output += f':second_place_medal: {player[cols["name"]]}\n'
        elif index == 3:
            output += f':third_place_medal: {player[cols["name"]]}\n'
    return output

def cmd_register_user(slack_mention):
    slack_user_id = slack.mention_to_user_id(slack_mention)
    if not slack_user_id:
        return 'Invalid slack user id. Did you use a @ ?'
    if database.player_exists(slack_user_id):
        return 'A player with that name is already registered'
    database.register_player(slack_user_id)
    return f'The player "{slack_mention}" is now registered for play'

def cmd_register_result(p1_slack_mention, p2_slack_mention, p1_score, p2_score):
    p1_row = database.get_player(p1_slack_mention)
    p2_row = database.get_player(p2_slack_mention)
    if not p1_row:
        return f'Player "{p1_slack_mention}" is not registered for play'
    if not p2_row:
        return f'Player "{p2_slack_mention}" is not registered for play'
    database.register_result(p1_row[0], p2_row[0], p1_score,
                             p2_score, datetime.datetime.now())
    return 'Result registered!'

def cmd_list_players():
    players = database.get_all_players()
    if not players:
        return 'Not enough data'
    output = '```\n'
    output += create_header_row([('Name', 20),
                                 ('Slack handle', 20)])
    for player in players:
        output += create_row([(player[1], 20),
                              (f'{slack.user_id_to_mention(player[2])}', 20)])
    output += '```'
    return output

def cmd_last_5_results():
    results = database.get_last_5_results()
    if not results:
        return 'Not enough data'
    output = '```\n'
    output += create_header_row([('Date', 20),
                                 ('Player1', 20),
                                 ('Player2', 20),
                                 ('Result', 15)])
    for result in results:
        playedat = result[4].strftime('%Y-%m-%d %H:%M')
        output += create_row([(playedat, 20),
                              (result[0], 20),
                              (result[1], 20),
                              (f'{result[2]}-{result[3]}', 15)])
    output += '```'
    return output

def add_score_to_leaderboard(leaderboard):
    if not leaderboard:
        return None
    cols = get_leaderboard_cols()
    tuplelist = []
    for player in leaderboard:
        tuplelist.append((player[0], player[1], player[2], player[3], player[4],))
    for index, data in enumerate(tuplelist):
        losses = data[cols['games']] - data[cols['wins']]
        tuplelist[index] += ((losses * -0.5) + data[cols['wins']],)
    tuplelist.sort(key=lambda p: p[cols['score']], reverse=True)
    return tuplelist

def get_leaderboard_cols():
    return {
        'name': 0, 'games': 1, 'wins': 2,
        'p_won': 3, 'p_lost': 4, 'score': 5
    }

def cmd_leaderboard():
    tuplelist = add_score_to_leaderboard(database.get_leaderboard())
    if not tuplelist:
        return 'Not enough data'
    cols = get_leaderboard_cols()
    output = '```\n'
    output += create_header_row([('Name', 20),
                                 ('Score', 10),
                                 ('Games', 10),
                                 ('Wins', 10),
                                 ('Losses', 10),
                                 ('Difference', 15)])
    for player in tuplelist:
        output += create_row([(player[cols['name']], 20),
                              (player[cols['score']], 10),
                              (player[cols['games']], 10),
                              (player[cols['wins']], 10),
                              (player[cols['games']]-player[cols['wins']], 10),
                              (f'{player[cols["p_won"]]}-{player[cols["p_lost"]]}', 15)])
    output += '```\n'
    return output

def cmd_help():
    help_text = 'Hi! These are commands that I understand:```'
    help_text += create_header_row([('Command', 20),
                                    ('Parameters', 40),
                                    ('Description', 0)])
    help_text += create_row([('register-player', 20),
                             ('slack_handle', 40),
                             ('Registers a slack user for play', 0)])
    help_text += create_row([('register-result', 20),
                             ('p1_slack_handle p2_slack_handle p1_score p2_score', 40),
                             ('Registers a played match', 0)])
    help_text += create_row([('list-players', 20),
                             ('', 40),
                             ('Lists all registered players', 0)])
    help_text += create_row([('last-5-results', 20),
                             ('', 40),
                             ('Lists the last 5 played games', 0)])
    help_text += create_row([('leaderboard', 20),
                             ('', 40),
                             ('Show the current leaderboard', 0)])
    help_text += create_row([('top-3', 20),
                             ('', 40),
                             ('Show the current top 3 players', 0)])
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
