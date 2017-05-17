## Filename messenger_handler.py
# -*- coding: utf-8 -*-

import requests
from messenger import Messenger
from models import ContaminationType, Citizen, Complaint, ComplaintState, CommunicationType

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
            args = payload.split()

            if args[0] == 'ask_for_cont_type':
                self.ask_for_cont_type()
            elif args[0] == 'new_case':
                self.new_case(args[1])

        elif 'text' in message:
            if message['text'] == 'reportar':
                self.ask_for_new_case()
            return 'ok'

    def start(self):
        # Check if messenger's chat id already exists
        citizen = Citizen.where_has('channels',
            lambda ch: ch.where('account_id', self.chat_id)).first()

        # If not create the citizen
        if citizen is None:
            user = Messenger.get_user_data(self.chat_id)

            Citizen.createForMessenger(self.chat_id, user)
            message = u'Hola {}, Soy Hojita :D y te ayudaré a reportar casos de contaminación de forma anónima ;)'.format(
                user['first_name'])
        # Else change the welcome message
        else:
            message = u'Hola {} :D'.format(citizen.name)

        Messenger.send_text(self.chat_id, message)

        self.ask_for_new_case()

    def ask_for_new_case(self):
        quick_replies = [
            {'content_type': 'text', 'title': 'Si :D', 'payload': 'ask_for_cont_type'},
            {'content_type': 'text', 'title': 'No :(', 'payload': 'nothing'}
        ]

        Messenger.send_text(self.chat_id,
            u'¿Deseas reportar un caso de contaminación? :o', quick_replies)

    def ask_for_cont_type(self):
        quick_replies = []
        text = 'Genial! Primero necesito que selecciones el tipo de contaminación que más se parece a lo que deseas reportar :)'

        for contamination_type in ContaminationType.all():
            quick_replies.append({
                'content_type': 'text',
                'title': contamination_type.description,
                'payload': 'new_case {}'.format(contamination_type.id)})

        Messenger.send_text(self.chat_id, text, quick_replies)

    def new_case(self, cont_type):
        citizen = Citizen.where_has('channels',
            lambda ch: ch.where('account_id', self.chat_id)).first()

        complaint = Complaint()
        complaint.citizen_id = citizen.id
        complaint.type_contamination_id = cont_type
        complaint.type_communication_id = CommunicationType.MESSENGER
        complaint.complaint_state_id = ComplaintState.INCOMPLETE
        complaint.save()

        Messenger.send_text(self.chat_id,
            u'¡Excelente! Ahora necesito una foto sobre el caso de contaminación, si tienes más mejor :D pero solo puedo guardar hasta 3 :)')
