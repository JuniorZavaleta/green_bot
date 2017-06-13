# -*- coding: utf-8 -*-
import telegram
from telegram.ext import (Updater, CommandHandler, ConversationHandler,
                          CallbackQueryHandler, MessageHandler, Filters)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from emoji import emojize
from models import *
from gmaps import GMaps, LimaException
from datetime import datetime
import config

bot = telegram.Bot(token=config.TELEGRAM_TOKEN)
updater = Updater(config.TELEGRAM_TOKEN)

# Utils
def build_menu(buttons, n_cols):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    return menu

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

    message = u'Puedes comenzar un caso de contaminación usando el comando /reportar'

    update.message.reply_text(message)

def ask_for_new_case(bot, update):
    keyboard = [[InlineKeyboardButton('Si :)', callback_data='ask_for_cont_type'),
                 InlineKeyboardButton('NO :(', callback_data='nothing')]]

    update.message.reply_text(u'¿Deseas reportar un caso de contaminación? :o',
        reply_markup=InlineKeyboardMarkup(keyboard))

def ask_for_cont_type(bot, update):
    keyboard = []

    message = u'¡Genial! Primero necesito que selecciones el tipo de contaminación que más se parece a lo que deseas reportar :)'
    for cont_type in ContaminationType.all():
        keyboard.append(
            InlineKeyboardButton(u'{}'.format(cont_type.description),
                callback_data='new_case {}'.format(cont_type.id))
        )

    update.callback_query.message.reply_text(message,
        reply_markup=InlineKeyboardMarkup(build_menu(keyboard, n_cols=2)))

    return NEW_CASE

def new_case(bot, update):
    query = update.callback_query
    chat_id = query.message.chat.id
    data = query.data.split()

    citizen = Citizen.where_has('channels',
        lambda ch: ch.where('account_id', chat_id)
                     .where('communication_type_id', CommunicationType.TELEGRAM)
    ).first()

    complaint = Complaint()
    complaint.citizen_id = citizen.id
    complaint.type_contamination_id = data[1]
    complaint.type_communication_id = CommunicationType.TELEGRAM
    complaint.complaint_status_id = ComplaintState.INCOMPLETE
    complaint.save()

    message = u'¡Excelente! Ahora necesito una foto sobre el caso de contaminación, si tienes más mejor :D pero solo puedo guardar hasta 3 :). Por favor, envia de uno en uno.'
    query.message.reply_text(message)

    return PHOTO_1

def add_image(bot, update):
    chat_id = update.message.chat.id
    file_id = update.message.photo[-1].file_id
    photo_file = bot.get_file(file_id)
    file_path = 'static/telegram_images/{}.jpg'.format(file_id)
    photo_file.download(file_path)

    citizen = Citizen.where_has('channels',
        lambda ch: ch.where('account_id', chat_id)
                     .where('communication_type_id', CommunicationType.TELEGRAM)
    ).first()
    incomplete_complaint = citizen.complaints().incomplete().first()
    incomplete_complaint.images().save(ComplaintImage(img=file_path))

def add_image_1(bot, update):
    add_image(bot, update)
    keyboard = [[InlineKeyboardButton('Si', callback_data='add_image_2'),
                 InlineKeyboardButton('No' , callback_data='add_location')]]
    update.message.reply_text(u'¿Deseas agregar otra imagen?',
        reply_markup=InlineKeyboardMarkup(keyboard))

    return ASK_PHOTO_2

def wait_photo_2(bot, update):
    update.callback_query.message.reply_text(u'Ok, adjunta la imagen :)')
    return PHOTO_2

def add_image_2(bot, update):
    add_image(bot, update)
    keyboard = [[InlineKeyboardButton('Si', callback_data='add_image_3'),
                 InlineKeyboardButton('No' , callback_data='add_location')]]
    update.message.reply_text(u'¿Deseas agregar otra imagen?',
        reply_markup=InlineKeyboardMarkup(keyboard))
    return ASK_PHOTO_3

def wait_photo_3(bot, update):
    update.callback_query.message.reply_text(u'Ok, adjunta la imagen :)')
    return PHOTO_3

def add_image_3(bot, update):
    add_image(bot, update)
    message = u'¡Sigamos! Ahora necesito que envies la localización del lugar donde tomaste la foto. Si estas ahi selecciona ubicación actual :D'
    update.message.reply_text(message)

    return LOCATION

def wait_location(bot, update):
    message = u'¡Sigamos! Ahora necesito que envies la localización del lugar donde tomaste la foto. Si estas ahi selecciona ubicación actual :D'
    update.callback_query.message.reply_text(message)
    return LOCATION

def add_location(bot, update):
    chat_id = update.message.chat.id
    citizen = Citizen.where_has('channels',
        lambda ch: ch.where('account_id', chat_id)
                     .where('communication_type_id', CommunicationType.TELEGRAM)
    ).first()
    complaint = citizen.complaints().incomplete().first()

    try:
        coordinates = update.message.location
        complaint.latitude = coordinates.latitude
        complaint.longitude = coordinates.longitude

        district_name = GMaps.get_district_name(coordinates.latitude, coordinates.longitude)
        district = District.where('name', district_name).first()

        if district is not None:
            complaint.district_id = district.id
            complaint.save()

            message = u'¡Ya falta poco! Me gustaría saber más sobre el caso :) Me ayudarías mucho si agregas un comentario. ¿Deseas agregar un comentario al caso?'
            keyboard = [[
                InlineKeyboardButton('Si :D',
                    callback_data='add_comment'),
                InlineKeyboardButton('No, Gracias' ,
                    callback_data='report {}'.format(complaint.id))
            ]]
            update.message.reply_text(message,
                reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            message = u'No hay autoridad para el distrito localizado :\'('
            update.message.reply_text(message)

        return REPORT
    except LimaException as e:
        update.message.reply_text(e.message)

def add_comment(bot, update):
    chat_id = update.message.chat.id
    citizen = Citizen.where_has('channels',
        lambda ch: ch.where('account_id', chat_id)
                     .where('communication_type_id', CommunicationType.TELEGRAM)
    ).first()
    complaint = citizen.complaints().incomplete().first()

    if complaint is not None:
        if complaint.latitude is not None and complaint.longitude is not None:
            complaint.commentary = update.message.text
            complaint.save()

            make_report(complaint, update.message)

    return ConversationHandler.END

def make_report(complaint, sender):
    citizen = Citizen.where_has('channels',
        lambda ch: ch.where('account_id', sender.chat.id)
                     .where('communication_type_id', CommunicationType.TELEGRAM)
    ).first()

    complaint.complaint_status_id = ComplaintState.COMPLETE
    complaint.created_at = datetime.now()
    complaint.updated_at = datetime.now()
    complaint.date_status_updated = datetime.now()
    complaint.save()

    message = u'Te enviaré actualizaciones sobre las actividades que realice la municipalidad :) asi que por favor no borres este chat :D'
    sender.reply_text(message)
    message = u'Para futuros reportes de contaminación puedes usar el menú o escribe "reportar" ;)'
    sender.reply_text(message)

def report(bot, update):
    query = update.callback_query
    chat_id = query.message.chat.id
    data = query.data.split()
    make_report(Complaint.find(data[1]), query.message)

    return ConversationHandler.END

def cancel(bot, update):
    return ConversationHandler.END

(NEW_CASE, PHOTO_1, ASK_PHOTO_2, PHOTO_2,
 ASK_PHOTO_3, PHOTO_3 , LOCATION, REPORT) = range(8)
# Handlers
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('reportar', ask_for_new_case))
updater.dispatcher.add_handler(ConversationHandler(
    entry_points=[CallbackQueryHandler(ask_for_cont_type, pattern='ask_for_cont_type')],
    states={
        NEW_CASE: [CallbackQueryHandler(new_case, pattern='new_case [0-9]')],
        PHOTO_1: [MessageHandler(Filters.photo, add_image_1)],
        ASK_PHOTO_2: [CallbackQueryHandler(wait_photo_2, pattern='add_image_2'),
                      CallbackQueryHandler(wait_location, pattern='add_location')],
        PHOTO_2: [MessageHandler(Filters.photo, add_image_2)],
        ASK_PHOTO_3: [CallbackQueryHandler(wait_photo_3, pattern='add_image_3'),
                      CallbackQueryHandler(wait_location, pattern='add_location')],
        PHOTO_3: [MessageHandler(Filters.photo, add_image_3)],
        LOCATION: [MessageHandler(Filters.location, add_location)],
        REPORT: [MessageHandler(Filters.text, add_comment), CallbackQueryHandler(report, pattern='report [0-9]+')],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
))
