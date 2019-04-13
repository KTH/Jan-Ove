__author__ = 'tinglev@kth.se'

import os
import re
import logging
from slackclient import SlackClient

def init():
    #global CLIENT, BOT_ID
    log = logging.getLogger(__name__)
    client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
    auth_test = client.api_call("auth.test")
    log.debug('Auth test response: %s', auth_test)
    bot_id = auth_test["user_id"]
    log.debug('Bot ID is "%s"', bot_id)
    return client.rtm_connect(with_team_state=False, auto_reconnect=True)

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
        trigger_text = os.environ.get('BOT_TRIGGER') or '!pingis'
        log = logging.getLogger(__name__)
        trigger_regex = r'^{0} (.+)'.format(trigger_text)
        matches = re.search(trigger_regex, message['text'])
        if matches and matches.group(1):
            return matches.group(1).strip(), message['user'], message['channel']
    except Exception as err:
        log.debug('Edited message ignored "%s". Error: "%s".', message, err)
    return (None, None, None)

def send_ephemeral(channel, user, message, default_message=None):
    log = logging.getLogger(__name__)
    log.debug('Sending eph to ch "%s" user "%s" msg "%s"', channel, user, message)
    client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
    client.api_call(
        "chat.postEphemeral",
        channel=channel,
        user=user,
        text=message or default_message
    )

def get_user_info(slack_handle):
    client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
    result = client.api_call(
                'users.info',
                user=slack_handle
                )
    print('Result: ', result)
    return result

def send_message(channel, message, default_message=None):
    log = logging.getLogger(__name__)
    log.debug('Sending msg to ch "%s" msg "%s"', channel, message)
    client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
    client.api_call(
        "chat.postMessage",
        channel=channel,
        text=message or default_message
    )

def rtm_read():
    client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
    return client.rtm_read()
