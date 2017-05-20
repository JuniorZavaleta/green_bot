# -*- coding: utf-8 -*-
import telegram
from telegram.ext import Updater, CommandHandler
from emoji import emojize
from models import *
import config

bot = telegram.Bot(token=config.TELEGRAM_TOKEN)
updater = Updater(config.TELEGRAM_TOKEN)

# Commands
def start(bot, update):
    # Check if messenger's chat id already exists
    chat_id = update.message.chat.id
    _from = update.message.from_user

    citizen = Citizen.where_has('channels',
        lambda ch: ch.where('account_id', chat_id)
                     .where('communication_type_id', CommunicationType.TELEGRAM)
    ).first()

    # If not create the citizen
    if citizen is None:
        Citizen.createForTelegram(chat_id, _from.first_name)
        message = u'Hola {}, Soy Hojita {} y te ayudaré a reportar casos de contaminación de forma anónima {}'.format(
            _from.first_name, emojize(':grinning_face:'), emojize(':winking_face:'))
    else:
        message = u'Hola {} {}'.format(citizen.name, emojize(':grinning_face:'))

    update.message.reply_text(message)

# Handlers
updater.dispatcher.add_handler(CommandHandler('start', start))
