__author__ = 'tinglev@kth.se'

import re
import logging
import datetime
import modules.slack as slack
import modules.database as database

def is_valid_command(command):
    for cmd in get_commands():
        if command == cmd['name']:
            return cmd
    return None

def cmd_list_seasons(slack_client, split_commands):
    seasons = database.get_all_seasons()
    if not seasons:
        return 'Not enough data'
    output = create_header_row([('Name', 20),
                                ('Started at', 20),
                                ('Ended at', 20)])
    for season in seasons:
        startedat = season.startedat.strftime('%Y-%m-%d %H:%M')
        if season.endedat:
            endedat = season.endedat.strftime('%Y-%m-%d %H:%M')
        else:
            endedat = 'Current'
        output += create_row([(season.name, 20),
                              (startedat, 20),
                              (endedat, 20)])

    return output + '```\n'

def cmd_undo_last_result(slack_client, split_commands):
    latest_result = database.get_latest_result()
    if not latest_result:
        return 'Not enough data'
    database.delete_result(latest_result.resultid)
    return 'Latest result deleted'

def cmd_top_3(slack_client, split_commands):
    results = database.get_leaderboard()
    if not results or len(results) < 3:
        return 'Not enough data'
    output = 'The current top 3 players are:\n'
    output += f':trophy: {results[0].name}\n'
    output += f':second_place_medal: {results[1].name}\n'
    output += f':third_place_medal: {results[2].name}\n'
    return output

def cmd_register_user(slack_client, split_commands):
    log = logging.getLogger(__name__)
    slack_mention = split_commands[1]
    slack_user_id = slack.mention_to_user_id(slack_mention)
    if not slack_user_id:
        return 'Invalid slack user id. Did you use a @ ?'
    if database.player_exists(slack_user_id):
        return 'A player with that name is already registered'
    log.debug('Registering user "%s"', slack_user_id)
    database.register_player(slack_client, slack_user_id)
    return f'The player "{slack_mention}" is now registered for play'

def cmd_register_result(slack_client, split_commands):
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
    error = database.register_result(p1_row.playerid, p2_row.playerid, p1_score,
                                     p2_score, datetime.datetime.now())
    if error:
        return error
    return 'Result registered!'

def cmd_list_players(slack_client, split_commands):
    players = database.get_all_players()
    if not players:
        return 'Not enough data'
    output = create_header_row([('Name', 20),
                                ('Slack handle', 20)])
    for player in players:
        output += create_row([(player.name, 20),
                              (f'{slack.user_id_to_mention(player.slackuserid)}', 20)])
    return output + '```\n'

def cmd_last_5_results(slack_client, split_commands):
    (results, error) = database.get_last_5_results()
    if error:
        return error
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

def get_trophy_emoji(placement):
    if placement == 1:
        return ':trophy:'
    elif placement == 2:
        return ':second_place_medal:'
    elif placement == 3:
        return ':third_place_medal:'
    else:
        return ''

def cmd_leaderboard(slack_client, split_commands):
    log = logging.getLogger(__name__)
    if (len(split_commands) == 2):
        (results, error) = database.get_leaderboard(split_commands[1])
    else:
        (results, error) = database.get_leaderboard()
    if error:
        return error
    log.debug('Leaderboard result is %s long', len(results))
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Showing the leaderboard for season *{results[0].season}*"
            }
        }
    ]
    blocks.append({"type": "divider"})
    for placement, result in enumerate(results, 1):
        trophy_emoji = get_trophy_emoji(placement)
        leaderboard_row = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (f"{trophy_emoji}*{result.player_name}*\n```{result.score} points\n"
                         f"W/L {result.wins}-{result.games-result.wins} "
                         f"Diff {result.wonpoints}-{result.lostpoints}```")
            }
        }
        if result.image_url:
            leaderboard_row['accessory'] = {
                "type": "image",
                "image_url": f"{result.image_url}",
                "alt_text": f"{result.player_name}"
            }
        blocks.append(leaderboard_row)
        blocks.append({"type": "divider"})

    return blocks

def cmd_help(slack_client, split_commands):
    column_widths = [20, 60, 0]
    help_text = 'Hi! These are commands that I understand:\n'
    help_text += create_header_row([('Command', 20),
                                    ('Parameters', 60),
                                    ('Description', 0)])
    for command in get_commands():
        help_text += create_row(
            [
                (command['name'], column_widths[0]),
                (command['param_names'], column_widths[1]),
                (command['help_text'], column_widths[2])
            ]
        )
    return help_text + '```'

def cmd_create_new_season(slack_client, split_commands):
    database.create_new_season(split_commands[1])
    return f'The new season "{split_commands[1]}" has started!'

def cmd_recreate_database(slack_client, split_commands):
    database.drop_and_create_tables()
    return 'Tables were dropped and recreated'

def create_row(tuple_array):
    row = '\n'
    for info in tuple_array:
        row += '{}'.format(info[0]).ljust(info[1])
    return row

def create_header_row(tuple_array, prefix='```\n'):
    row = prefix
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
            'param_names': '@slack-name',
            'help_text': 'Registers a slack user for play',
            'func': cmd_register_user
        },
        {
            'name': 'list-players',
            'params': 0,
            'param_names': '',
            'help_text': 'List all registered players',
            'func': cmd_list_players
        },
        {
            'name': 'new-season',
            'params': 1,
            'param_names': '"Season name in quotes"',
            'help_text': 'Create a new season, starting now',
            'func': cmd_create_new_season
        },
        {
            'name': 'list-seasons',
            'params': 0,
            'param_names': '',
            'help_text': 'List all seasons',
            'func': cmd_list_seasons
        },
        {
            'name': 'last-5-results',
            'params': 0,
            'param_names': '',
            'help_text': 'List the result of the last 5 played games',
            'func': cmd_last_5_results
        },
        {
            'name': 'register-result',
            'params': 4,
            'param_names': '@player1-name @player2-name p1_score p2_score',
            'help_text': 'Register the result of a game',
            'func': cmd_register_result
        },
        {
            'name': 'leaderboard',
            'params': 0,
            'param_names': '',
            'help_text': 'Shows the current leaderboard',
            'func': cmd_leaderboard
        },
        {
            'name': 'old-leaderboard',
            'params': 1,
            'param_names': '"season name in quotes"',
            'help_text': 'Shows the leaderboard for the given season',
            'func': cmd_leaderboard
        },
        {
            'name': 'undo-last-result',
            'params': 0,
            'param_names': '',
            'help_text': 'Deletes the last registered result',
            'func': cmd_undo_last_result
        },
        {
            'name': 'help',
            'params': 0,
            'param_names': '',
            'help_text': 'Shows this help',
            'func': cmd_help
        },
        {
            'name': 'initialize-database',
            'params': 0,
            'param_names': '',
            'help_text': 'WARNING! Drops the entire database and recreates it',
            'func': cmd_recreate_database
        }
    ]
