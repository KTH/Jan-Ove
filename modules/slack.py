__author__ = 'tinglev@kth.se'

import os
import re
import logging
from slackclient import SlackClient

RTM_READ_DELAY = 1
CLIENT = None
BOT_ID = None
TRIGGER_TEXT = '!pingis'

def init():
    global CLIENT, BOT_ID
    log = logging.getLogger(__name__)
    CLIENT = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
    auth_test = CLIENT.api_call("auth.test")
    log.debug('Auth test response: %s', auth_test)
    BOT_ID = auth_test["user_id"]
    log.debug('Bot ID is "%s"', BOT_ID)
    return CLIENT.rtm_connect(with_team_state=False, auto_reconnect=True)

def mention_to_user_id(mention):
    mention_regex = r'^<@(.+)>$'
    matches = re.search(mention_regex, mention)
    if matches:
        return matches.group(1)
    return None

def user_id_to_mention(user_id):
    return f'<@{user_id}>'

def get_rtm_messages(events):
    messages = []
    for event in events:
        if event["type"] == "message":
            messages.append(event)
    return messages

def message_is_command(message):
    try:
        log = logging.getLogger(__name__)
        trigger_regex = r'^{0} (.+)'.format(TRIGGER_TEXT)
        matches = re.search(trigger_regex, message['text'])
        if matches and matches.group(1):
            return matches.group(1).strip(), message['user'], message['channel']
    except Exception as err:
        log.debug('Edited message ignored "%s". Error: "%s".', message, err)
    return (None, None, None)

def message_is_direct_mention(message):
    try:
        log = logging.getLogger(__name__)
        mention_regex = r'^<@(|[WU].+?)>(.*)'
        matches = re.search(mention_regex, message['text'])
        if matches and matches.group(1) == BOT_ID and 'subtype' not in message:
            return matches.group(2).strip(), message['user'], message['channel']
    except Exception as err:
        log.debug('Edited message ignored "%s". Error: "%s".', message, err)
    return (None, None, None)

def send_ephemeral(channel, user, message, default_message=None):
    log = logging.getLogger(__name__)
    log.debug('Sending eph to ch "%s" user "%s" msg "%s"', channel, user, message)
    CLIENT.api_call(
        "chat.postEphemeral",
        channel=channel,
        user=user,
        text=message or default_message
    )

def get_user_info(slack_handle):
    result = CLIENT.api_call(
                'users.info',
                user=slack_handle
                )
    print('Result: ', result)
    return result

def send_message(channel, message, default_message=None):
    log = logging.getLogger(__name__)
    log.debug('Sending msg to ch "%s" msg "%s"', channel, message)
    CLIENT.api_call(
        "chat.postMessage",
        channel=channel,
        text=message or default_message
    )

def rtm_read():
    return CLIENT.rtm_read()
