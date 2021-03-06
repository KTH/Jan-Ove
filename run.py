__author__ = 'tinglev@kth.se'

import os
import time
import logging
import log as log_module
from requests.exceptions import ReadTimeout
from modules import slack, database, commands, util
from flask import Flask

FLASK = Flask(__name__)

def handle_command(slack_client, args, channel, user):
    try:
        log = logging.getLogger(__name__)
        log.info(
            'Handling cmd "%s" on ch "%s" and user "%s"',
            args, channel, user
        )
        trigger_text = os.environ.get('BOT_TRIGGER') or '!pingis'
        default_response = f'Not sure what you mean. Use *{trigger_text} help* for help'
        split_args = util.args_to_commands(args)
        log.debug('split_args is "%s"', split_args)
        main_command = split_args[0]
        response = None
        command_json = commands.is_valid_command(main_command)
        if command_json:
            if (len(split_args) - 1) != command_json['params']:
                response = (
                    f'Wrong number of arguments for command. '
                    f'Should be {command_json["params"]} '
                    f'but was {len(split_args) - 1}'
                )
            else:
                response = command_json['func'](slack_client, split_args)

    except ReadTimeout as error:
        log.error('Error while handling command: %s', error)
        response = ('Sorry, the :whale: refused to do as it was told. Try again ...\n'
                    '```{}```'.format(error))
    if isinstance(response, list):
        slack.send_block_message(slack_client, channel, response)
    else:
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

def start_bot():
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


@FLASK.route('/jan-ove/', methods=['GET'])
def leaderboard():
    return f'200 {database.get_leaderboard()}'

def start_webserver():
    FLASK.run(host='0.0.0.0', port=3000, debug=False)

if __name__ == "__main__":
    log_module.init_logging()
    # This blocks the bot from running
    #start_webserver()
    start_bot()
