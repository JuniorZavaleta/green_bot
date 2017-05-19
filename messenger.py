##Filename: messenger.py
import requests
import config

class Messenger(object):
    token = config.PAGE_TOKEN
    graph = 'https://graph.facebook.com/v2.6'

    @staticmethod
    def send_text(chat_id, text, quick_replies = []):
        message = {
            'text': text
        }

        if (quick_replies):
            message.update({
                'quick_replies': quick_replies
            })

        data = {
            'recipient': {'id': chat_id},
            'message': message
        }

        Messenger.send_message(data)

    @staticmethod
    def send_template(chat_id, elements):
        data = {
            'recipient': {'id': chat_id},
            'message': {
                'attachment': {
                    'type': 'template',
                    'payload': {
                        'template_type': 'generic',
                        'elements': elements
                    }
                }
            }
        }

        Messenger.send_message(data)

    @staticmethod
    def send_message(data):
        requests.post('{}/me/messages?access_token={}'.format(
            Messenger.graph, Messenger.token), json=data)

    @staticmethod
    def get_user_data(chat_id):
        return requests.get('{}/{}?access_token={}'.format(
            Messenger.graph, chat_id, Messenger.token)).json()
