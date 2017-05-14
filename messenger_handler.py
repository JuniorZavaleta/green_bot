## Filename messenger_handler.py
# -*- coding: utf-8 -*-

import requests
from messenger import Messenger
from models import ContaminationType

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

            if payload == 'new_case':
                self.new_case()

        elif 'text' in message:
            if message['text'] == 'reportar':
                self.ask_for_new_case()
            return 'ok'

    def start(self):
        user = Messenger.get_user_data(self.chat_id)

        Messenger.send_text(self.chat_id,
            u'Hola {}, Soy Hojita :D y te ayudaré a reportar casos de contaminación de forma anónima ;)'.format(
            user['first_name']))

        self.ask_for_new_case()

    def ask_for_new_case(self):
        quick_replies = [
            {'content_type': 'text', 'title': 'Si :D', 'payload': 'new_case'},
            {'content_type': 'text', 'title': 'No :(', 'payload': 'nothing'}
        ]

        Messenger.send_text(self.chat_id,
            u'¿Deseas reportar un caso de contaminación? :o', quick_replies)

    def new_case(self):
        quick_replies = []
        text = 'Genial! Primero necesito que selecciones el tipo de contaminación que más se parece a lo que deseas reportar :)'

        for contamination_type in ContaminationType.all():
            quick_replies.append({
                'content_type': 'text',
                'title': contamination_type['name'],
                'payload': 'add_type {}'.format(contamination_type['id'])})

        Messenger.send_text(self.chat_id, text, quick_replies)
