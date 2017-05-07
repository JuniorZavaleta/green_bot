## Filename messenger_handler.py
# -*- coding: utf-8 -*-

import requests
from messenger import Messenger

class MessengerHandler(object):
    chat_id = None

    def __init__(self, chat_id):
        self.chat_id = chat_id

    def handle_bot(self, messaging):
        if 'postback' in messaging:
            self.handle_postback(messaging['postback']['payload'])
        elif 'message' in messaging:
            self.handle_message(messaging['message'])
        return 'ok'

    def handle_postback(self, payload):
        if payload == 'start':
            self.start()

        return 'ok'

    def handle_message(self, message):
        if 'quick_reply' in message:
            payload = message['quick_reply']['payload']

        elif 'message' in message:
            return 'ok'

    def start(self):
        user = Messenger.get_user_data(self.chat_id)

        Messenger.send_text(self.chat_id,
            u'Hola {}, Soy Hojita. Acá puedes realizar reclamos sobre casos de contaminación'.format(
            user['first_name']))
