__author__ = 'tinglev@kth.se'

import os
import re
import random
import logging
from slackclient import SlackClient

rtm_read_delay = 1
mention_regex = r'^<@(|[WU].+?)>(.*)'
client = None
bot_id = None

log = logging.getLogger(__name__)

def init():
    global client, bot_id
    client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
    auth_test = client.api_call("auth.test")
    log.debug('Auth test response: %s', auth_test)
    bot_id = auth_test["user_id"]
    log.debug('Bot ID is "%s"', bot_id)
    return client.rtm_connect(with_team_state=False, auto_reconnect=True)

def get_rtm_messages(events):
    messages = []
    for event in events:
        if event["type"] == "message":
            messages.append(event)
    return messages

def message_is_direct_mention(message):
    try: 
        matches = re.search(mention_regex, message['text'])
        if matches and matches.group(1) == bot_id and 'subtype' not in message:
            return matches.group(2).strip(), message['user'], message['channel']
    except Exception as err:
        log.debug("Edited message ignored {}. Error: {}.".format(message, err))

    return (None, None, None)

def send_ephemeral(channel, user, message, default_message=None):
    log.debug('Sending eph to ch "%s" user "%s" msg "%s"', channel, user, message)
    client.api_call(
        "chat.postEphemeral",
        channel=channel,
        user=user,
        text=message or default_message
    )

def send_message(channel, message, default_message=None):
    log.debug('Sending msg to ch "%s" msg "%s"', channel, message)
    client.api_call(
        "chat.postMessage",
        channel=channel,
        text=message or default_message
    )

def rtm_read():
    return client.rtm_read()
