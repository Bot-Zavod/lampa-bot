import logging
import chat
from states import States
from chat import *

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)

from handlers import *
from helpers import to_regex
from settings import *

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def main():

    print("Starting")

    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            States.FRUIT: [MessageHandler(Filters.regex(to_regex(start_kb)), fruit,)],
            States.SOUND: [MessageHandler(Filters.regex(to_regex(fruit_kb)), sound,)],
            States.ANIMAL: [MessageHandler(Filters.regex(to_regex(sound_kb)), animal,)],
            States.CONSENT: [
                MessageHandler(Filters.regex(to_regex(animal_kb)), consent,)
            ],
            States.STICKERS: [
                MessageHandler(Filters.regex(to_regex(stickers_kb)), stickers,)
            ],
            States.CURRENT_MOOD: [
                MessageHandler(Filters.regex(to_regex(current_mood_kb)), current_mood,)
            ],
            States.WHY_LEAVE: [
                MessageHandler(Filters.regex(to_regex(start_kb)), why_leave,)
            ],
            States.IN_CONNECTION: [chat_handler],
        },
        fallbacks=[CommandHandler("stop", done)],
    )

    dp.add_handler(conv_handler)

    # dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    main()
