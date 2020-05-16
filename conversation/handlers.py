from .states import States
from .constants import *
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
from db import *
from memes import get_meme, get_anecdot
from .payment import noSubscription
from os import environ
import logging
from spreadsheet import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)



def start(update, context):
    chat_id = update.message.chat_id
    update.message.reply_text(
        (
            "Мы рады тебе.)\nпройди lampa-тест, чтобы мы могли почувствовать твой current mood(настроение и состояние)"
        ),
        reply_markup=ReplyKeyboardMarkup(keyboard=start_kb, resize_keyboard=True),
    )

    logger.info("User %s: press /start;", chat_id)
    return States.FRUIT

def fruit(update, context):
    chat_id = update.message.chat_id
    # check if user honorable enough or paid to use the bot
    admin = str(update.message.chat.username) in environ["ADMIN"]
    if not admin:
        if not (DB.userIsSubscribed(chat_id) or DB.haveFreePass(chat_id)):
            return noSubscription(update, context)
    context.user_data[str(chat_id)] = []

    update.message.reply_text(
        "Какой ты сейчас фрукт?",
        reply_markup=ReplyKeyboardMarkup(keyboard = fruit_kb, resize_keyboard=True),
    )
    logger.info("User %s: fruit func;", chat_id)
    return States.SOUND

# ХУЛИ ОРЕШЬ?
def sound(update, context):
    chat_id = update.message.chat_id
    update.message.reply_text(
        "Какой ты сейчас звук?",
        reply_markup=ReplyKeyboardMarkup(keyboard = sound_kb, resize_keyboard=True),
    )
    context.user_data[str(update.message.chat_id)].append(update.message.text)
    logger.info("User %s: sound func;", chat_id)
    return States.ANIMAL

# ТЫ СУКА ПЕС?
def animal(update, context):
    chat_id = update.message.chat_id
    update.message.reply_text(
        "Какое ты сейчас животное?",
        reply_markup=ReplyKeyboardMarkup(keyboard = animal_kb, resize_keyboard=True),
    )
    context.user_data[str(update.message.chat_id)].append(update.message.text)

    logger.info("User %s: animal func;", chat_id)
    return States.STICKERS


def stickers(update, context):
    chat_id = update.message.chat_id
    logger.info("User %s: stickers func;", chat_id)
    if DB.firstTimeEntry(chat_id):
        reply_markup=ReplyKeyboardMarkup(
                keyboard = stickers_kb, 
                resize_keyboard=True, 
                one_time_keyboard=True
            )
        res = update.message.reply_text(
            "Пока я соединяю тебя с собеседником, хочешь самые милые на свете стикеры?",
            reply_markup=reply_markup
        )
        return States.STICKERS_ANSW
    else:
        return consent(update, context)


def consent(update, context):
    chat_id = update.message.chat_id
    update.message.reply_text(
        "Я буду внимательно, этично и тепло относиться к человеку на том конце чата.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard = consent_kb, resize_keyboard=True, one_time_keyboard=True
        ),
    )
    context.user_data[str(update.message.chat_id)].append(update.message.text)

    logger.info("User %s: consent func;", chat_id)
    return States.IN_CONNECTION


def stickers_yes(update, context):
    update.message.reply_sticker(
        "CAACAgIAAxkBAAPDXrleZo93jyMgBneJBJ9ejDfX9IUAAiUAA0R8oRMzVew1dDSXuhkE"
    )
    chat_id = update.message.chat_id
    logger.info("User %s: stickers_yes func;", chat_id)
    return consent(update, context)


def stickers_no(update, context):
    chat_id = update.message.chat_id
    logger.info("User %s: stickers_no func;", chat_id)
    return consent(update, context)


def current_mood(update, context):
    message_text = update.message.text
    context.user_data[str(update.message.chat_id)].append(message_text)

    reply_markup = ReplyKeyboardMarkup(keyboard = current_mood_kb, 
                                       one_time_keyboard=True, 
                                       resize_keyboard=True)
    update.message.reply_text(text = current_mood_text, 
                              reply_markup=reply_markup)

    chat_id = update.message.chat_id
    logger.info("User %s: current_mood func;", chat_id)
    return States.CURRENT_MOOD


def to_google_sheet(update, context):
    message_text = update.message.text
    context.user_data[str(update.message.chat_id)].append(message_text)
    answers = context.user_data[str(update.message.chat_id)]
    answers = [google_answers['why_leave'][answers[-2]],  
               google_answers['current_mood'][answers[-1]]]
    
    # ask for mems
    text = "Анекдот или мем напоследок?"
    reply_markup=ReplyKeyboardMarkup(keyboard=funny_kb, 
                                     one_time_keyboard=True, 
                                     resize_keyboard=True)
    update.message.reply_text(text = text,
                              reply_markup=reply_markup
    )

    # save to google_answers
    after_chat(*answers)
    return States.FUNNY_ANSW


def meme(update, context):
    update.message.reply_photo(photo = open(get_meme(),"rb"))
    return start(update, context)


def anecdot(update, context):
    update.message.reply_text(get_anecdot())
    return start(update, context)




def error(update, context):
    update.message.reply_text("Ой, что-то пошло не так. Попробуй позже еще раз",)
