#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from flask import Flask, request
import telegram
from telegram.ext import Updater, CommandHandler
from emoji import emojize

logging.basicConfig(level=logging.DEBUG,
                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger()

#Environment
TELEGRAM_TOKEN = "TELEGRAM_TOKEN_BOT"
SITE_URL = "NGROL_HTTPS"

global bot, updater
bot = telegram.Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)
updater = Updater(TELEGRAM_TOKEN)

# Commands
def start(bot, update):
    update.message.reply_text(u'Hola!, Soy Hojita {}'.format(
        emojize(':grinning_face:', use_aliases=True)))

# Handlers
updater.dispatcher.add_handler(CommandHandler('start', start))

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
    if bot.setWebhook(SITE_URL + '/telegram'):
        return "webhook setup ok"
    else:
        return "webhook setup failed"

@app.route('/')
def index():
    return 'Flask running'

if __name__ == '__main__':
    app.run(debug=True)
