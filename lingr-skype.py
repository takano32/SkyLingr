# -*- coding: utf-8 -*-
from bottle import post, run, request, response
import re
import json

import os
os.environ['DISPLAY'] = ":64"
os.environ['XAUTHORITY'] = "/home/takano32/.Xauthority"

from configobj import ConfigObj
global config
config_path = '/home/takano32/workspace/skype-bridge/Skype4Py/skype-bridge.conf'
config = ConfigObj(config_path)


def handler(msg, event):
    pass

import Skype4Py
global skype
skype = Skype4Py.Skype()
skype.OnMessageStatus = handler
skype.Attach()


def send_message(room, text):
    room.SendMessage(text)


def event_handler(event):
    if not('message' in event):
        return
    for key in config:
        if key == 'lingr' or key == 'skype' or key == 'irc':
            continue
        if not('lingr' in config[key]):
            continue
        if not('skype' in config[key]):
            continue
        if not event['message']['room'] == config[key]['lingr']:
            continue
        event_handler_each(event, key)


def event_handler_each(event, key):
        text = event['message']['text']
        name = event['message']['nickname']
        if re.compile(u'荒.*?川.*?智.*?則').match(name):
            name = event['message']['speaker_id']
        if len(name) > 16:
            name = event['message']['speaker_id']
        room = config[key]['skype']
        try:
            room = skype.Chat(room)
        except Skype4Py.SkypeError:
            return
        for line in text.splitlines():
            msg = '%s: %s' % (name, line)
            send_message(room, msg)


@post('/skype')
def post_from_lingr():
    body = request.body.read()
    from_lingr = json.JSONDecoder().decode(body)
    if not('events' in from_lingr):
        response.status = 200
        return
    for event in from_lingr['events']:
        event_handler(event)
    response.status = 200
    return

run(host='0.0.0.0', port=8006)
