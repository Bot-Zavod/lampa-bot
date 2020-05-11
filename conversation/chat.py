#!/usr/bin/env python

from .twoWayDict import TwoWayDict
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)
from .helpers import to_regex
from .constants import *
from .states import States
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

users = TwoWayDict()
lobby = []

CONVERSATION = range(1)


def start(update, context):
    update.message.reply_text(connection_text, reply_markup=ReplyKeyboardRemove())
    if not update.message.chat_id in lobby:
        lobby.append(update.message.chat_id)
    if connect():
        msg_text = comrade_found_text
        update.message.reply_text(msg_text)
        context.bot.send_message(chat_id=users[update.message.chat_id], text=msg_text)
    print(lobby)

    return CONVERSATION


def connect():
    if len(lobby) > 1:
        users[lobby.pop()] = lobby.pop()
        return True
    return False


def answer(update, context):
    if update.message.chat_id in users:
        context.bot.send_message(
            chat_id=users[update.message.chat_id], text=update.message.text
        )
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Sorry, we didin`t find a companion for you yet",
        )
    return None


def stick_answer(update, context):
    sticker_id = update.message.sticker.file_id
    if update.message.chat_id in users:
        context.bot.send_sticker(
            chat_id=users[update.message.chat_id], sticker=sticker_id
        )
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Sorry, we didin`t find a companion for you yet",
        )
    return None


def done(update, context):
    chat_id = update.message.chat_id
    if chat_id in lobby:
        update.message.reply_text("leaving lobby")
        lobby.remove(chat_id)
    elif chat_id in users:
        update.message.reply_text(chat_finished_text)
        context.bot.send_message(chat_id=users[chat_id], text=comrade_left_text)
        del users[chat_id]
    else:
        update.message.reply_text(chat_finished_text)
    update.message.reply_text(
        why_leave_text,
        reply_markup=ReplyKeyboardMarkup(
            [list(map(str, range(1, 6)))], resize_keyboard=True
        ),
    )
    print(users, lobby)
    return ConversationHandler.END


chat_handler = ConversationHandler(
    allow_reentry=True,
    entry_points=[MessageHandler(Filters.regex(to_regex(consent_kb)), start)],
    states={
        CONVERSATION: [
            MessageHandler(Filters.text & (~Filters.command), answer),
            MessageHandler(Filters.sticker, stick_answer),
        ],
    },
    fallbacks=[CommandHandler("stop", done)],
    map_to_parent={ConversationHandler.END: States.WHY_LEAVE,},
)
