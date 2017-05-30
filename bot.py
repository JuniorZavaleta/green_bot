# -*- coding: utf-8 -*-
import logging
from flask import Flask, request, send_from_directory
import telegram
from messenger_handler import MessengerHandler
from telegram_handler import bot, updater
import config

logging.basicConfig(level=logging.DEBUG,
                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger()

app = Flask(__name__)

# Routes
@app.route('/telegram', methods=['POST'])
def handle_telegram_request():
    if request.method == "POST":
        # retrieve the message in JSON and then transform it to Telegram object
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        updater.dispatcher.process_update(update)
    return 'ok'

@app.route('/set', methods=['GET', 'POST'])
def set_webhook():
    if bot.setWebhook(config.SITE_URL + '/telegram'):
        return "webhook setup ok"
    else:
        return "webhook setup failed"

@app.route('/')
def index():
    return 'Flask running'

@app.route('/messenger', methods=['GET'])
def handle_verification():
    return request.args['hub.challenge']

@app.route('/messenger', methods=['POST'])
def handle_messenger_request():
    data = request.json
    messaging = data['entry'][0]['messaging'][0]
    chat_id = messaging['sender']['id']
    handler = MessengerHandler(chat_id)

    return handler.handle_bot(messaging)

@app.route('/<path:filename>')
def send_telegram_image(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True)
