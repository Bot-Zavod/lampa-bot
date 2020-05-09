from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PreCheckoutQueryHandler, CallbackQueryHandler, ConversationHandler
from telegram import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
import logging
from requests import get

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

USERS = {}


def start(update, context):
	try:
		a = USERS[update.message.chat.id]
	except Exception as e:
		USERS[update.message.chat.id] = {'sub': False, 'trial': 3}

	text = 'Мы рады тебе. )\nПройди lampa-тест, чтобы мы могли почувствовать твой current mood (настроение и состояние) 🙂'
	reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text="Пройти тест!", callback_data="test")]])
	update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
	logger.info("User %s: send /start;", update.message.chat.id)

def getFruit(update, context):
	chat_id = update.callback_query.message.chat.id
	# to db methods
	user_subсribe = USERS[chat_id]['sub'] #checkUserApply()
	user_trial = USERS[chat_id]['trial'] #checkFreePass()

	if user_subсribe == True:
		text = 'Какой ты сейчас фрукт?'
	elif 0 < user_trial <= 3: #change on True or False
		text = 'Какой ты сейчас фрукт? ('+str(USERS[chat_id]['trial'])+' left)'

		# Просто добавить Pass
		USERS[chat_id]['trial'] -= 1
	else:
		text = "Кажется.. Сегодня все бесплатные lampa-тесты уже пройдены 😞 Ты можешь поболтать с кем-то еще, купив lampa-подписку /subscribe"
		day = InlineKeyboardButton(text="3 дня", callback_data="3days")
		week = InlineKeyboardButton(text="Неделя", callback_data="week")
		month = InlineKeyboardButton(text="Месяц", callback_data="month")
		no_sps = InlineKeyboardButton(text="Не сейчас", callback_data="no_sps")
		reply_markup = InlineKeyboardMarkup([[day],[week],[month],[no_sps]])

		context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
		return False

	context.bot.send_message(chat_id=chat_id, text=text)
	logger.info("User %s: chose FRUIT;", chat_id)

def no_sps(update, context):
	chat_id = update.callback_query.message.chat.id
	message_id = update.callback_query.message.message_id
	context.bot.delete_message(chat_id, message_id)
	
	text = 'Расскажите нам, почему вы не хотите использовать нашего Бота по платной подписке? 🙄'
	b1 = InlineKeyboardButton(text="Сервис мне не интересен", callback_data="reason1")
	b2 = InlineKeyboardButton(text="Меня не устраивает цена подписки", callback_data="reason2")
	b3 = InlineKeyboardButton(text="Другое...", callback_data="other")
	reply_markup = InlineKeyboardMarkup([[b1],[b2],[b3]])
	context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
	logger.info("User %s: refused to subscribe;", chat_id)
	return 1

def other(update, context):
	chat_id = update.callback_query.message.chat.id
	message_id = update.callback_query.message.message_id
	data = update.callback_query.data
	context.bot.delete_message(chat_id, message_id)
	if data == 'other':
		text = 'Расскажите пожалуйста почему?'
		context.bot.send_message(chat_id=chat_id, text=text)
		logger.info("User %s: take other;", chat_id)
		return 2
	else:
		logger.info("User %s: take 1-2 reason;", chat_id)
		return sps_buy(update.callback_query, context)
		

def sps_buy(update, context):
	text = 'Спасибо, друг!) Я всегда тебе рад, если вдруг будет грустно и захочется с кем-то поговорить 🙂'
	update.message.reply_text(text=text)
	logger.info("User %s: subscribed;", update.message.chat.id)
	return ConversationHandler.END

def cancel(update, context):
	text = 'Готово!'
	update.message.reply_text(text=text)
	logger.info("User %s: cancel;", update.message.chat.id)


def subscribe(update, context):
	text = "На сколько ты хочешь купить подписку? 🙈 ?\nНе забудь прочитать /terms"
	day = InlineKeyboardButton(text="3 дня", callback_data="3days")
	week = InlineKeyboardButton(text="Неделя", callback_data="week")
	month = InlineKeyboardButton(text="Месяц", callback_data="month")
	not_now = InlineKeyboardButton(text="Не сейчас", callback_data="not_now")
	reply_markup = InlineKeyboardMarkup([[day],[week],[month],[not_now]])
	update.message.reply_text(text=text, reply_markup=reply_markup)
	logger.info("User %s: try to subscribe;", update.message.chat.id)

def not_now(update, context):
	chat_id = update.callback_query.message.chat_id
	message_id = update.callback_query.message.message_id
	context.bot.delete_message(chat_id, message_id)
	logger.info("User %s: refused;", chat_id)
	return start(update.callback_query, context)

def terms(update, context):
	text = "1. Денюжки мы не вернем, уж прости.\n2. Время стартует сразу после списания средств"
	update.message.reply_text(text=text)
	logger.info("User %s: ask Terms;", update.message.chat.id)

def pay(update, context):
	update = update.callback_query
	currency = int(round(get('https://api.exchangeratesapi.io/latest?symbols=USD,RUB').json()['rates']['RUB']))
	description = {
		'3days':['Будет действовать в течение 3х дней 🦀', LabeledPrice("Subscribe on 3 days", 100*currency)], 
		'week':['Будет действовать в течение недели 🐟', LabeledPrice("Subscribe on week", 200*currency)],
		'month':['Будет действовать в течение месяца 🐬', LabeledPrice("Subscribe on month", 400*currency)]}
	context.bot.send_invoice(
		chat_id=update.message.chat.id, 
		title="Оформление платежа",
		description=description[update.data][0],
		payload=update.data,
		start_parameter=update.data,
		provider_token="381764678:TEST:15778",
		currency="RUB",
		prices=[description[update.data][1]])
	logger.info("User %s: get Invoice on %s;", update.message.chat.id, update.data)


def successful_payment_callback(update, context):
	#Тут записывает в базу newSubscribe()
	USERS[update.message.chat.id]['sub'] = True
	update.message.reply_text("Как хорошо, что ты здесь!) Узнаем твоё настроение?🦄")
	logger.info("User %s: subscribed", update.message.chat.id)


def precheckout_callback(update, context):
    query = update.pre_checkout_query
    if query.invoice_payload not in ['3days','week','month']:
        query.answer(ok=False, error_message="Smthn went wrong ...")
    else:    	
        query.answer(ok=True)



if __name__ == '__main__':
	updater = Updater(token='728358108:AAEd0cC2S2LW8HvBSuFbQP0EoA-jWJ5XyUQ', use_context=True)
	dispatcher = updater.dispatcher

	dispatcher.add_handler(CommandHandler('start', start))
	dispatcher.add_handler(CommandHandler('subscribe', subscribe))
	# dispatcher.add_handler(CallbackQueryHandler(subscribe, pattern='^(subscribe)$'))
	dispatcher.add_handler(CommandHandler('terms', terms))
	dispatcher.add_handler(CallbackQueryHandler(not_now, pattern='^(not_now)$'))
	dispatcher.add_handler(CallbackQueryHandler(getFruit, pattern='^(test)$'))
	dispatcher.add_handler(CallbackQueryHandler(pay, pattern='^(3days|week|month)$'))
	dispatcher.add_handler(PreCheckoutQueryHandler(precheckout_callback))
	dispatcher.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback))

	dispatcher.add_handler(ConversationHandler(
		per_message=False,
        entry_points=[CallbackQueryHandler(no_sps, pattern='^(no_sps)$')],
        states={
            1: [CallbackQueryHandler(other, pattern='^(other|reason1|reason2)$')],
            2: [MessageHandler(Filters.text, sps_buy)],
        },
        fallbacks=[CommandHandler('cancel', cancel),
        ]
    ))


	updater.start_polling()
	updater.idle()