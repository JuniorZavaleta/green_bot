## Filename messenger_handler.py
# -*- coding: utf-8 -*-

import requests
from datetime import datetime
from messenger import Messenger
from gmaps import GMaps, LimaException
from models import *

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
            elif args[0] == 'nothing':
                self.nothing()
            elif args[0] == 'new_case':
                self.new_case(args[1])
            elif args[0] == 'wait_comment':
                self.wait_comment()
            elif args[0] == 'report':
                self.report(Complaint.find(args[1]))

        elif 'text' in message:
            if message['text'] == 'reportar':
                self.ask_for_new_case()
            elif message['text'] == 'start':
                self.start()
            else:
                self.add_comment(message['text'])

        elif 'attachments' in message:
            # Check if exists a incomplete complaint
            citizen = Citizen.where_has('channels',
                lambda ch: ch.where('account_id', self.chat_id)).first()
            incomplete_complaint = citizen.complaints().incomplete().first()

            if incomplete_complaint is not None:
                if message['attachments'][0]['type'] == 'location':
                    self.add_location(incomplete_complaint, message['attachments'][0]['payload']['coordinates'])
                elif message['attachments'][0]['type'] == 'image':
                    self.add_images(incomplete_complaint, message['attachments'])
                else:
                    message = u'Por favor, no ingrese tipos de archivo que no se le han solicitado.'

                    Messenger.send_text(self.chat_id, message)
            else:
                if message['attachments'][0]['type'] == 'image':
                    message = u'Veo que has subido una imagen, disculpa pero primero debes decirme si quieres reportar un caso de contaminación.'
                    Messenger.send_text(self.chat_id, message)
                    self.ask_for_new_case()

    def start(self):
        # Check if messenger's chat id already exists
        citizen = Citizen.where_has('channels',
            lambda ch: ch.where('account_id', self.chat_id)
                         .where('communication_type_id', CommunicationType.MESSENGER)
        ).first()

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
        message = u'¿Deseas reportar un caso de contaminación? :o'

        Messenger.send_text(self.chat_id, message, quick_replies)

    def ask_for_cont_type(self):
        quick_replies = []
        message = u'¡Genial! Primero necesito que selecciones el tipo de contaminación que más se parece a lo que deseas reportar :)'

        for contamination_type in ContaminationType.all():
            quick_replies.append({
                'content_type': 'text',
                'title': contamination_type.description,
                'payload': 'new_case {}'.format(contamination_type.id)})

        Messenger.send_text(self.chat_id, message, quick_replies)

    def nothing(self):
        message = u'Bueno :(, pero no te olvides de avisarme cuándo veas un caso de contaminación :D'
        Messenger.send_text(self.chat_id, message)

    def new_case(self, cont_type):
        citizen = Citizen.where_has('channels',
            lambda ch: ch.where('account_id', self.chat_id)
                         .where('communication_type_id', CommunicationType.MESSENGER)
        ).first()

        complaint = Complaint()
        complaint.citizen_id = citizen.id
        complaint.type_contamination_id = cont_type
        complaint.type_communication_id = CommunicationType.MESSENGER
        complaint.complaint_state_id = ComplaintState.INCOMPLETE
        complaint.save()

        message = u'¡Excelente! Ahora necesito una foto sobre el caso de contaminación, si tienes más mejor :D pero solo puedo guardar hasta 3 :)'
        Messenger.send_text(self.chat_id, message)

    def add_images(self, incomplete_complaint, attachments):
        images = []
        for attachment in attachments:
            if attachment['type'] == 'image':
                images.append(ComplaintImage(img=attachment['payload']['url']))

        incomplete_complaint.images().save_many(images)
        message = u'¡Sigamos! Ahora necesito que envies la localización del lugar donde tomaste la foto. Si estas ahi selecciona ubicación actual :D'
        ask_location = [{
            "content_type": "location",
        }]

        Messenger.send_text(self.chat_id, message, ask_location)

    def add_location(self, incomplete_complaint, coordinates):
        incomplete_complaint.latitude = coordinates['lat']
        incomplete_complaint.longitude = coordinates['long']

        try:
            district_name = GMaps.get_district_name(coordinates['lat'], coordinates['long'])
            district = District.where('name', district_name).first()

            if district is not None:
                authority = Authority.where('district_id', district.id).first()
                incomplete_complaint.authority_id = authority.id
                incomplete_complaint.save()

                message = u'¡Ya falta poco! Me gustaría saber más sobre el caso :) Me ayudarías mucho si agregas un comentario. ¿Deseas agregar un comentario al caso?'
                quick_replies = [
                    {
                        'content_type': 'text', 'title': 'Si :D',
                        'payload': 'wait_comment'},
                    {
                        'content_type': 'text', 'title': 'No, Gracias',
                        'payload': 'report {}'.format(incomplete_complaint.id)
                    }
                ]

                Messenger.send_text(self.chat_id, message, quick_replies)
            else:
                message = u'No hay autoridad para el distrito localizado :\'('
                Messenger.send_text(self.chat_id, message)
        except LimaException as e:
            Messenger.send_text(self.chat_id, e.message)

    def wait_comment(self):
        message = u'¡Excelente! Por favor escribe tu comentario en un solo mensaje ;). Si cambiaste de opinión y prefieres no comentar :(, mandame un like :\'(.'
        Messenger.send_text(self.chat_id, message)

    def add_comment(self, message):
        citizen = Citizen.where_has('channels',
            lambda ch: ch.where('account_id', self.chat_id)).first()
        complaint = citizen.complaints().incomplete().first()

        if complaint is not None:
            if complaint.latitude is not None and complaint.longitude is not None:
                complaint.commentary = message
                complaint.save()

                self.report(complaint)

    def report(self, complaint):
        complaint.complaint_state_id = ComplaintState.COMPLETE
        complaint.created_at = datetime.now()
        complaint.updated_at = datetime.now()
        complaint.date_status_updated = datetime.now()
        complaint.save()

        message = u'¡Gracias por tu ayuda! Acabó de registrar tu caso de contaminación :D'
        Messenger.send_text(self.chat_id, message)

        citizen = Citizen.where_has('channels',
                lambda ch: ch.where('account_id', self.chat_id)).first()

        if citizen.complaints.count() == 1:
            message = u'Te enviaré actualizaciones sobre las actividades que realice la municipalidad :) asi que por favor no borres este chat :D'
            Messenger.send_text(self.chat_id, message)
            message = u'Para futuros reportes de contaminación puedes usar el menú o escribe "reportar" ;)'
            Messenger.send_text(self.chat_id, message)
        else:
            message = u'Recuerda que te enviaré actualizaciones sobre tu caso :) asi que por favor no borres este chat :D'
            Messenger.send_text(self.chat_id, message)
