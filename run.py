__author__ = 'tinglev@kth.se'

import time
import logging
import log as log_module
from requests.exceptions import ReadTimeout
from modules import slack, database, commands

def handle_command(slack_client, command, channel, user):
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
        command = commands.is_valid_command(cmd)
        if command:
            if (len(split_commands) - 1) != command['params']:
                response = (
                    f'Wrong number of arguments for command. '
                    f'Should be {command["params"]} '
                    f'but was {len(split_commands) - 1}'
                )
            else:
                response = command['func'](slack_client, split_commands)

    except ReadTimeout as error:
        log.error('Error while handling command: %s', error)
        response = ('Sorry, the :whale: refused to do as it was told. Try again ...\n'
                    '```{}```'.format(error))
    slack.send_message(slack_client, channel, response, default_response)

def read_and_handle_rtm(slack_client):
    log = logging.getLogger(__name__)
    log.debug('Checking for new messages')
    rtm_read_delay_secs = 1
    rtm_messages = []
    try:
        rtm_messages = slack.get_rtm_messages(slack.rtm_read(slack_client))
    except Exception:
        log.warning('Timeout when reading from Slack')
    if rtm_messages:
        log.debug('Got %s messages since last update',
                   len(rtm_messages))
    for message in rtm_messages:
        log.debug('Handling message "%s"', message)
        command, user, channel = slack.message_is_command(message)
        if command:
            handle_command(slack_client, command, channel, user)
    time.sleep(rtm_read_delay_secs)

def main():
    log = logging.getLogger(__name__)
    try:
        slack_client = slack.init()
        if slack_client and database.init():
            log.info("Jan-Ove connected and running!")
            while True:
                read_and_handle_rtm(slack_client)
        else:
            log.error("Connection to Slack failed!")
    except Exception as err:
        #slack.send_message('#team-pipeline', ('Oh :poop:, I died and had to restart myself. '
        #                                      '\n```{}```'.format(err)))
        raise

if __name__ == "__main__":
    log_module.init_logging()
    main()
