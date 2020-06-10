import logging
from .states import States
from .chat import *

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    PreCheckoutQueryHandler,
    CallbackQueryHandler,
    PicklePersistence,
)

from .handlers import *
from .helpers import to_regex
from .constants import *
from .admin import *
from .payment import *

from os import remove, path, getcwd
from getpass import getuser

username = getuser()
if username != "ec2-user":
    storage = "storage"
    create_path = path.abspath(getcwd())
    create_path = path.join(create_path, storage)
    if path.exists(create_path):
        print("launched on dev machine")
        print("resetting storage")
        remove(create_path)
else:
    print("launched on production ec2-user")


def env():
    enviroment = ".env"
    create_path = path.abspath(getcwd())
    create_path = path.join(create_path, enviroment)

    if not path.exists(create_path):
        print("no .env found")
        print(f"create_path: {create_path}")
        f = open(create_path, "x")
        f.close()
        print(".env need to be completed")
    else:
        print(".env exist")


env()

from dotenv import load_dotenv

load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def main():

    print("Starting")

    my_persistence = PicklePersistence(filename="storage")
    updater = Updater(environ["API_KEY"], persistence=my_persistence, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("terms", terms))

    # Эти хэндлеры обрабатывают платежку не трогать нахой!
    dp.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    dp.add_handler(
        MessageHandler(Filters.successful_payment, successful_payment_callback)
    )

    conv_handler = ConversationHandler(
        allow_reentry=True,
        entry_points=[CommandHandler("start", start)],
        states={
            States.FRUIT: [MessageHandler(Filters.regex(to_regex(start_kb)), fruit,)],
            States.SOUND: [MessageHandler(Filters.regex(to_regex(fruit_kb)), sound,)],
            States.ANIMAL: [MessageHandler(Filters.regex(to_regex(sound_kb)), animal,)],
            States.CONSENT: [
                MessageHandler(Filters.regex(to_regex(animal_kb)), consent,)
            ],
            States.STICKERS: [
                MessageHandler(Filters.regex(to_regex(animal_kb)), stickers,)
            ],
            States.STICKERS_ANSW: [
                MessageHandler(Filters.regex("^Хочу$"), stickers_yes,),
                MessageHandler(Filters.regex("^Не хочу$"), stickers_no,),
            ],

            States.WHY_LEAVE: [
                MessageHandler(Filters.regex(to_regex(why_leave_kb)), current_mood,)
            ],
            States.CURRENT_MOOD: [
                MessageHandler(
                    Filters.regex(to_regex(current_mood_kb)), to_google_sheet,
                )
            ],

            # States.FUNNY: [MessageHandler(Filters.regex(to_regex(current_mood_kb)), funny)],
            States.FUNNY_ANSW: [
                MessageHandler(Filters.regex("^Мем$"), meme,),
                MessageHandler(Filters.regex("^Анекдот$"), anecdot,),
                MessageHandler(Filters.regex("^Выйти$"), start),
            ],

            States.IN_CONNECTION: [chat_handler],
            States.IN_PAYMENT: [
                CallbackQueryHandler(no_sps, pattern="^(no_sps)$"),
                CallbackQueryHandler(pay, pattern="^(3days|week|month)$"),
            ],
            States.SUB_REFUSAL: [
                CallbackQueryHandler(other, pattern="^(other|reason1|reason2)$")
            ],
            States.SUB_REFUSAL_EXPLAINED: [MessageHandler(Filters.text, sps_buy)],
        },
        fallbacks=[CommandHandler("stop", done)],
        persistent=True,
        name="conversations",
    )

    admin_handler = ConversationHandler(
        entry_points=[CommandHandler("admin", admin)],
        states={
            States.ADMIN: [
                MessageHandler(Filters.regex(to_regex(admin_kb)), admin_menu)
            ],
            States.PUSH_WHAT: [MessageHandler(Filters.text, push_text)],
            States.PUSH_SUBMIT: [
                MessageHandler(Filters.regex(to_regex(push_kb)), push)
            ],
        },
        fallbacks=[CommandHandler("stop", done)],
        persistent=True,
        name="admin",
    )

    dp.add_handler(conv_handler)
    dp.add_handler(admin_handler)

    updater.start_polling()
    print("Started succesfully")
    updater.idle()


if __name__ == "__main__":
    main()
