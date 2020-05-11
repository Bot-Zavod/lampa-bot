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
    PicklePersistence,
)

from .handlers import *
from .helpers import to_regex
from .settings import TOKEN
from .constants import *

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def main():

    print("Starting")

    pp = PicklePersistence(filename="storage")
    updater = Updater(TOKEN, persistence=pp, use_context=True)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
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
                MessageHandler(Filters.regex(to_regex(why_leave_kb)), why_leave)
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

    dp.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    main()
