from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime
from os import getcwd, remove, environ


from .states import States
from db import *
from .constants import *
from .handlers import start

# for send_statisctics
from os import getcwd
import matplotlib.pyplot as plt
from collections import Counter


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


# generate statisctics files payments1(2).png return path to file
def total_count():
    days = DB.getCountByTerm("3days")
    week = DB.getCountByTerm("week")
    month = DB.getCountByTerm("month")

    # test
    # days, week, month = 12,34, 55

    # First for payments
    names = ["3day", "week", "month"]
    values = [days, week, month]
    yint = range(0, max(values) + 1)

    plt.figure(figsize=(15, 5))
    plt.subplot(131)
    plt.bar(names, values, color=["red", "blue", "green"])
    plt.yticks(yint)
    plt.title("Платежи")
    plt.ylabel("Покупки")
    plt.ylabel("Тип")
    plt.savefig("payments1.png", bbox_inches="tight")
    return getcwd() + "/payments1.png"


def all_payments_graph():
    arr = DB.getDates()
    print(arr)
    date = list(Counter(arr).keys())
    values = list(Counter(arr).values())
    yint = range(0, max(values) + 1)
    # test
    # date = ['2020-12-02', '2020-12-03', '2020-12-04', '2020-12-05', '2020-12-06']
    # values = [13, 10, 22, 12, 22]

    # Задать размер, по умолчанию сам выбирает
    plt.figure(figsize=(10, 5))
    plt.plot(date, values, color="red", linestyle="dashed", marker=".", markersize=5)
    plt.ylabel("Покупки")
    plt.yticks(yint)
    plt.title("Все платежи")
    plt.savefig("payments2.png", bbox_inches="tight")
    return getcwd() + "/payments2.png"


# handle answer from admin menu
def admin_menu(update, context):
    answer = update.message.text
    if answer == admin_text["push"]:
        update.message.reply_text(admin_text["push_text"])
        return States.PUSH_WHAT
    elif answer == admin_text["stats"]:
        stats_result = admin_text["data"].format(
            sub_1=DB.getCountByTerm("3days"),
            sub_2=DB.getCountByTerm("week"),
            sub_3=DB.getCountByTerm("month"),
            dialogs=DB.getConversationsCount(),
            users=DB.getTotalUsersCount(),
        )
        update.message.reply_text(text=stats_result)

        # sending payments1(2).png
        path_file1 = total_count()
        path_file2 = all_payments_graph()

        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(path_file1, "rb"),
            caption="Кол-во всех платежей по популярности",
        )
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(path_file2, "rb"),
            caption="Кол-во всех платежей за все время",
        )
        remove(path_file1)
        remove(path_file2)

        return admin(update, context)
    elif answer == admin_text["back"]:
        return start(update, context)


# show up basic admin menu
def admin(update, context):
    # checks if you are a true admin
    if str(update.message.chat.username) in environ["ADMIN"]:
        update.message.reply_text(admin_text["hi_boss"], reply_markup=admin_kb_markup)
        return States.ADMIN
    else:
        update.message.reply_text(admin_text["not_boss"])
        return start(update, context)
