from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime
from os import getcwd, remove, environ


from .states import States
from db import *
from .constants import *
from .handlers import start

# for text that admin wants to send
push_text_notification = None


def push(update, context):
    msg = update.message.text
    if msg != admin_text["send"]:
        return admin(update, context)

    global push_text_notification
    # sending the notification message
    users_ids = DB.getAllUsersID()
    for user_id in users_ids:
        context.bot.send_message(chat_id=user_id, text=push_text_notification)
    user_number = len(users_ids)
    update.message.reply_text(
        text=admin_text["push_success"].format(user_number=user_number)
    )
    return admin(update, context)


# catches admin massage
def push_text(update, context):
    global push_text_notification
    answer = update.message.text
    push_text_notification = answer

    msg = admin_text["push_submit"].format(answer=answer)
    update.message.reply_text(text=msg, reply_markup=push_kb_markup)
    return States.PUSH_SUBMIT


# handle answer from admin menu
def admin_menu(update, context):
    answer = update.message.text
    if answer == admin_text["push"]:
        update.message.reply_text(admin_text["push_text"])
        return States.PUSH_WHAT
    elif answer == admin_text["stats"]:
        stats_result = admin_text["data"]\
            .format(sub_1=DB.getCountByTerm("3days"),
                    sub_2=DB.getCountByTerm("week"),
                    sub_3=DB.getCountByTerm("month"),
                    dialogs=DB.getConversationsCount())
        update.message.reply_text(text=stats_result)
        return admin(update, context)
    elif answer == admin_text["back"]:
        return start(update, context)


# show up basic admin menu
def admin(update, context):
    # checks if you are a true admin
    if update.message.chat.username == "V_vargan":#in environ["ADMIN"]:
        update.message.reply_text(admin_text["hi_boss"], reply_markup=admin_kb_markup)
        return States.ADMIN
    else:
        update.message.reply_text(admin_text["not_boss"])
        return start(update, context)
