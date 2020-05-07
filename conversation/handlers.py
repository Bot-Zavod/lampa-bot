from . import States
from .constants import *


def start(update, context):
    reply_keyboard = start_kb

    update.message.reply_text(
        """
            Мы рады тебе.)
            пройди lampa-тест, чтобы мы могли почувствовать твой current mood
            (настроение и состояние)
        """,
        reply_keyboard,
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
        reply_keyboard,
    )

    return States.SOUND


def sound(update, context):
    reply_keyboard = sound_kb

    update.message.reply_text(
        """
        Какой ты сейчас звук?
        """,
        reply_keyboard,
    )

    return States.ANIMAL


def animal(update, context):
    reply_keyboard = animal_kb

    update.message.reply_text(
        """
        Какое ты сейчас животное?
        """,
        reply_keyboard,
    )

    return States.CONSENT


def consent(update, context):
    reply_keyboard = consent_kb

    update.message.reply_text(
        """
        Сейчас мы соединим тебя с человеком,
         который чувствует себя тем же фруктом, звуком и животным, что и ты…\n
        Ты не увидишь ни фото, ни имени, но ты почувствуешь,
         что где-то в мире есть человек, которому не все равно, как твои дела)\n
        Этому человеку сейчас тоже грустно.
         В такие моменты очень важно чувствовать, что ты не один.\n
        Попробуй узнать, что у него случилось и немного поддержать. Он поддержит тебя тоже,
         и вам обоим станет немного теплее, светлее и радостнее )
        """,
        reply_keyboard,
    )
    if True:  # is_first_time():
        return States.STICKERS
    else:
        return States.IN_CONNECTION


def stickers(update, context):
    reply_keyboard = stickers_kb

    update.message.reply_text(
        """
        Пока я соединяю тебя с собеседником, хочешь самые милые на свете стикеры?
        """,
        reply_keyboard,
    )

    return States.IN_CONNECTION


def current_mood(update, context):
    reply_keyboard = current_mood_kb

    update.message.reply_text(
        """
        Как сейчас твое настроение?
        """,
        reply_keyboard,
    )

    return States.WHY_LEAVE


def why_leave(update, context):
    reply_keyboard = why_leave_kb
    update.message.reply_text(
        """
        Почему ты сейчас уходишь из чата?
        """,
        reply_keyboard,
    )

    return States.IDLE


def error(update, context):
    update.message.reply_text(
        """
        Ой, что-то пошло не так. Попробуй позже еще раз
        """,
    )
