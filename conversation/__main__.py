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
fucking_path="/home/vargan/Dropbox/Programming_projects/Chatbots/lampa-bot/storage"
if path.exists(fucking_path):
        print("fucking_path exists")
        remove(fucking_path)

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

    pp = PicklePersistence(filename="storage")
    updater = Updater(environ["API_KEY"], persistence=pp, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('terms', terms))

    # Эти хэндлеры обрабатывают платежку не трогать нахой!
    dp.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    dp.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback))

    payment_handler = ConversationHandler(
        # per_message=True,
        entry_points=[CallbackQueryHandler(no_sps, pattern='^(no_sps)$'),
                      CallbackQueryHandler(pay, pattern='^(3days|week|month)$')],
        states={
            States.SUB_REFUSAL: [CallbackQueryHandler(other, pattern='^(other|reason1|reason2)$')],
            States.SUB_REFUSAL_EXPLAINED: [MessageHandler(Filters.text, sps_buy)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        map_to_parent={ConversationHandler.END: States.FRUIT,},
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            States.IN_PAYMENT: [payment_handler],
            States.FRUIT: [MessageHandler(Filters.regex(to_regex(start_kb)), fruit,)],
            States.SOUND: [MessageHandler(Filters.regex(to_regex(fruit_kb)), sound,)],
            States.ANIMAL: [MessageHandler(Filters.regex(to_regex(sound_kb)), animal,)],
            States.CURRENT_MOOD: [
                MessageHandler(Filters.regex(to_regex(current_mood_kb)), current_mood,)
            ],
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
                MessageHandler(Filters.regex(to_regex(start_kb)), why_leave,)
            ],
            States.FUNNY: [MessageHandler(Filters.regex(to_regex(start_kb)), funny,)],
            States.FUNNY_ANSW: [
                MessageHandler(Filters.regex("^Мем$"), meme,),
                MessageHandler(Filters.regex("^Анекдот$"), anecdot,),
                MessageHandler(Filters.regex("^Выйти$"), why_leave,),
            ],
            States.IN_CONNECTION: [chat_handler],
        },
        fallbacks=[CommandHandler("stop", done)],
        persistent=True,
        name="conversations",
    )

    admin_handler = ConversationHandler(
        entry_points=[CommandHandler("admin", admin)],
        states={
            States.ADMIN: [MessageHandler(Filters.regex(to_regex(admin_kb)), admin_menu)],
            States.PUSH_WHAT: [MessageHandler(Filters.text, push_text)],
            States.PUSH_SUBMIT: [MessageHandler(Filters.regex(to_regex(push_kb)), push)],
        },
        fallbacks=[CommandHandler("stop", done)],
    )

    dp.add_handler(payment_handler)
    dp.add_handler(conv_handler)
    dp.add_handler(admin_handler)

    updater.start_polling()
    print("Started succesfully")
    updater.idle()


if __name__ == "__main__":
    main()
