__author__ = 'tinglev@kth.se'

import time
import logging
import log as log_module
from modules import slack
from modules import database
from requests.exceptions import ReadTimeout

from modules.commands import cmd_register_result
from modules.commands import cmd_register_user
from modules.commands import cmd_help

log_module.init_logging()
log = logging.getLogger(__name__)

def handle_command(command, channel, user):
    try:
        log.info(
            'Handling cmd "%s" on ch "%s" and user "%s"',
            command, channel, user
        )
        default_response = 'Not sure what you mean. Use *@Jan-Ove help* for help'
        split_commands = command.split(' ')
        cmd = split_commands[0]
        response = None
        if cmd in database.commands:
            if cmd == 'register-player':
                response = cmd_register_user(channel, user, split_commands[1])
            if cmd == 'register-result':
                response = cmd_register_result(
                    channel, user, split_commands[1], split_commands[2], split_commands[3], split_commands[4]
                )
            if cmd == 'help':
                response = cmd_help()

    except (ReadTimeout) as error:
        log.error('Error while handling command: %s', error)
        response = ('Sorry, the :whale: refused to do as it was told. Try again ...\n'
                    '```{}```'.format(error))
    slack.send_ephemeral(channel, user, response, default_response)

def main():
    try:
        if slack.init() and database.init():
            log.info("Jan-Ove connected and running!")
            while True:
                log.info('Checking for new messages')
                rtm_messages = []
                try:
                    rtm_messages = slack.get_rtm_messages(slack.rtm_read())
                except Exception:
                    log.warn('Timeout when reading from Slack')
                if len(rtm_messages) > 0:
                    log.debug('Got %s messages since last update',
                              len(rtm_messages))
                for message in rtm_messages:
                    log.debug('Handling message "%s"', message)
                    command, user, channel = slack.message_is_direct_mention(message)
                    if command:
                        handle_command(command, channel, user)
                time.sleep(slack.rtm_read_delay)
        else:
            log.error("Connection to Slack failed!")
    except Exception as err:
        #slack.send_message('#team-pipeline', ('Oh :poop:, I died and had to restart myself. '
        #                                      '\n```{}```'.format(err)))
        raise

if __name__ == "__main__":
    main()