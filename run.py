__author__ = 'tinglev@kth.se'

import time
import logging
import log as log_module
from requests.exceptions import ReadTimeout

from modules import slack, database, commands
from modules.commands import (cmd_register_result,
                              cmd_register_user,
                              cmd_list_players,
                              cmd_last_5_results,
                              cmd_leaderboard,
                              cmd_top_3,
                              cmd_help)

log_module.init_logging()

def handle_command(command, channel, user):
    try:
        log = logging.getLogger(__name__)
        log.info(
            'Handling cmd "%s" on ch "%s" and user "%s"',
            command, channel, user
        )
        default_response = 'Not sure what you mean. Use *@Jan-Ove help* for help'
        split_commands = command.split(' ')
        cmd = split_commands[0]
        response = None
        if commands.is_valid_command(cmd):
            if (len(split_commands) - 1) != commands.get_command_arguments(cmd):
                response = (
                    f'Wrong number of arguments for command. '
                    f'Should be {commands.get_command_arguments(cmd)} '
                    f'but was {len(split_commands) - 1}'
                )
            elif cmd == 'register-player':
                response = cmd_register_user(split_commands[1])
            elif cmd == 'register-result':
                response = cmd_register_result(
                    split_commands[1], split_commands[2],
                    split_commands[3], split_commands[4]
                )
            elif cmd == 'list-players':
                response = cmd_list_players()
            elif cmd == 'last-5-results':
                response = cmd_last_5_results()
            elif cmd == 'leaderboard':
                response = cmd_leaderboard()
            elif cmd == 'top-3':
                response = cmd_top_3()
            elif cmd == 'help':
                response = cmd_help()

    except ReadTimeout as error:
        log.error('Error while handling command: %s', error)
        response = ('Sorry, the :whale: refused to do as it was told. Try again ...\n'
                    '```{}```'.format(error))
    slack.send_message(channel, response, default_response)

def main():
    log = logging.getLogger(__name__)
    try:
        if slack.init() and database.init():
            log.info("Jan-Ove connected and running!")
            while True:
                log.debug('Checking for new messages')
                rtm_messages = []
                try:
                    rtm_messages = slack.get_rtm_messages(slack.rtm_read())
                except Exception:
                    log.warning('Timeout when reading from Slack')
                if rtm_messages:
                    log.debug('Got %s messages since last update',
                              len(rtm_messages))
                for message in rtm_messages:
                    log.debug('Handling message "%s"', message)
                    command, user, channel = slack.message_is_command(message)
                    if command:
                        handle_command(command, channel, user)
                time.sleep(slack.RTM_READ_DELAY)
        else:
            log.error("Connection to Slack failed!")
    except Exception as err:
        #slack.send_message('#team-pipeline', ('Oh :poop:, I died and had to restart myself. '
        #                                      '\n```{}```'.format(err)))
        raise

if __name__ == "__main__":
    main()
