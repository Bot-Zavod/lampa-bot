from states import States
from constants import *
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)


def start(update, context):
    reply_keyboard = start_kb

    update.message.reply_text(
        """
            Мы рады тебе.)
            пройди lampa-тест, чтобы мы могли почувствовать твой current mood
            (настроение и состояние)
        """,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True),
    )
    if True:  # is_admin():
        return States.FRUIT
    else:
        return States.IN_PAYMENT


def fruit(update, context):
    reply_keyboard = fruit_kb

    update.message.reply_text(
        """
        Какой ты сейчас фрукт?
        """,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True),
    )

    return States.SOUND


def sound(update, context):
    reply_keyboard = sound_kb

    update.message.reply_text(
        """
        Какой ты сейчас звук?
        """,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True),
    )

    return States.ANIMAL


def animal(update, context):
    reply_keyboard = animal_kb

    update.message.reply_text(
        """
        Какое ты сейчас животное?
        """,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True),
    )

    return States.CONSENT


def consent(update, context):
    reply_keyboard = consent_kb

    update.message.reply_text('Я буду внимательно, этично и тепло относиться к человеку на том конце чата.',
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))

    if False:  # is_first_time():
        return States.STICKERS
    else:
        return States.IN_CONNECTION

def stickers(update, context):
    reply_keyboard = stickers_kb

    update.message.reply_text(
        """
        Пока я соединяю тебя с собеседником, хочешь самые милые на свете стикеры?
        """,
        reply_keyboard=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return States.IN_CONNECTION


def current_mood(update, context):
    reply_keyboard = current_mood_kb

    update.message.reply_text(
        """
        Как сейчас твое настроение?
        """,
        reply_keyboard=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return States.WHY_LEAVE


def why_leave(update, context):
    reply_keyboard = why_leave_kb
    update.message.reply_text(
        """
        Почему ты сейчас уходишь из чата?
        """,
        reply_keyboard=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return States.IDLE


def error(update, context):
    update.message.reply_text(
        """
        Ой, что-то пошло не так. Попробуй позже еще раз
        """,
    )
