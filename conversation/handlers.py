from .states import States
from .constants import *
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
from db import *
from memes import get_meme, get_anecdot
from .payment import noSubscription

from os import environ

def start(update, context):
    chat_id = update.message.chat_id
    update.message.reply_text(
        (
            "Мы рады тебе.)\nпройди lampa-тест, чтобы мы могли почувствовать твой current mood(настроение и состояние)"
        ),
        reply_markup=ReplyKeyboardMarkup(keyboard=start_kb, resize_keyboard=True),
    )
    context.user_data[str(chat_id)] = []

    # check if user honorable enough or paid to use the bot
    if str(update.message.chat.username) in environ["ADMIN"]:
        return States.FRUIT
    # elif DB.userIsSubscribed(chat_id) or DB.haveFreePass(chat_id):
    #     return States.FRUIT
    else:
        return noSubscription(update, context)


def fruit(update, context):
    update.message.reply_text(
        "Какой ты сейчас фрукт?",
        reply_markup=ReplyKeyboardMarkup(keyboard = fruit_kb, resize_keyboard=True),
    )

    return States.SOUND


def sound(update, context):
    update.message.reply_text(
        "Какой ты сейчас звук?",
        reply_markup=ReplyKeyboardMarkup(keyboard = sound_kb, resize_keyboard=True),
    )
    context.user_data[str(update.message.chat_id)].append(update.message.text)

    return States.ANIMAL


def animal(update, context):
    update.message.reply_text(
        "Какое ты сейчас животное?",
        reply_markup=ReplyKeyboardMarkup(keyboard = animal_kb, resize_keyboard=True),
    )
    context.user_data[str(update.message.chat_id)].append(update.message.text)

    #If not first time
    # if DB.checkFreePass(update.message.chat_id):
    #     stickers(update, context)
    return States.STICKERS
    # else:
    #     return States.CONSENT


def consent(update, context):
    update.message.reply_text(
        "Я буду внимательно, этично и тепло относиться к человеку на том конце чата.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard = consent_kb, resize_keyboard=True, one_time_keyboard=True
        ),
    )
    context.user_data[str(update.message.chat_id)].append(update.message.text)

    return States.IN_CONNECTION


def stickers(update, context):
    if False:
        res = update.message.reply_text(
            "Пока я соединяю тебя с собеседником, хочешь самые милые на свете стикеры?",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard = stickers_kb, resize_keyboard=True, one_time_keyboard=True
            ),
        )
        return States.STICKERS_ANSW
    else:
        return consent(update, context)


def stickers_yes(update, context):
    update.message.reply_sticker(
        "CAACAgIAAxkBAAPDXrleZo93jyMgBneJBJ9ejDfX9IUAAiUAA0R8oRMzVew1dDSXuhkE"
    )
    return consent(update, context)


def stickers_no(update, context):
    return consent(update, context)


def current_mood(update, context):
    reply_keyboard = current_mood_kb

    update.message.reply_text(
        "Как сейчас твое настроение?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return States.FUNNY


def why_leave(update, context):
    reply_keyboard = why_leave_kb
    update.message.reply_text(
        "Почему ты сейчас уходишь из чата?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return States.IDLE


def error(update, context):
    update.message.reply_text("Ой, что-то пошло не так. Попробуй позже еще раз",)


def funny(update, context):
    reply_keyboard = funny_kb

    update.message.reply_text(
        "Что бы ты хотел?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return States.FUNNY_ANSW


def meme(update, context):
    update.message.reply_photo(get_meme())
    return States.IDLE


def anecdot(update, context):
    update.message.reply_text(get_anecdot())
    return States.IDLE
