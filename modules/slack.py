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
    client.rtm_connect(with_team_state=False, auto_reconnect=True)
    return client

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

def send_ephemeral(slack_client, channel, user, message, default_message=None):
    log = logging.getLogger(__name__)
    log.debug('Sending eph to ch "%s" user "%s" msg "%s"', channel, user, message)
    slack_client.api_call(
        "chat.postEphemeral",
        channel=channel,
        user=user,
        text=message or default_message
    )

def get_user_info(slack_client, slack_user_id):
    log = logging.getLogger(__name__)
    log.debug('Calling "users.info" on slack api')
    user = slack_client.api_call(
        'users.info',
        user=slack_user_id
    )
    log.debug('Got user %s', user)
    return user

def get_user_list(slack_client):
    log = logging.getLogger(__name__)
    log.debug('Calling "users.list" on slack api')
    result = slack_client.api_call(
        'users.list'
    )
    #log.debug('Response from api was: %s', result)
    return result

def get_user_from_user_list(user_list, user_id):
    log = logging.getLogger(__name__)
    if not 'members' in user_list:
        return None
    for user in user_list['members']:
        if 'id' in user and user['id'] == user_id:
            log.debug('Found user %s in user_list', user_id)
            return user
    return None

def get_user_image_url(user):
    imv_version = 'image_192'
    log = logging.getLogger(__name__)
    if 'user' in user and 'profile' in user['user']:
        if imv_version in user['user']['profile']:
            log.debug('Found user image for user %s', user['user']['id'])
            return user['user']['profile'][imv_version]
    return None

def send_message(slack_client, channel, message, default_message=None):
    log = logging.getLogger(__name__)
    log.debug('Sending msg to ch "%s" msg "%s"', channel, message)
    response = slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=message or default_message
    )
    log.debug('Response from api was: %s', response)

def send_block_message(slack_client, channel, blocks):
    log = logging.getLogger(__name__)
    log.debug('Sending block message to ch "%s" blocks  "%s"', channel, blocks)
    response = slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        blocks=blocks
    )
    log.debug('Response from api was: %s', response)

def rtm_read(slack_client):
    return slack_client.rtm_read()
