from telegram import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, ReplyKeyboardRemove
from telegram.ext import ConversationHandler
import logging
from requests import get

from .states import States
from spreadsheet import *
from db import *
from .constants import *

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# terms or why we are not going to return money
def terms(update, context):
	text = "1. Денюжки мы не вернем, уж прости.\n2. Время стартует сразу после списания средств"
	update.message.reply_text(text=text)
	logger.info("User %s: ask Terms;", update.message.chat.id)

# ask dickhead to pay or die
def noSubscription(update, context):
	chat_id = update.message.chat.id

	text = "Кажется.. Сегодня все lampa-тесты уже пройдены 😞"
	context.bot.send_message(chat_id=chat_id, text=text, reply_markup=ReplyKeyboardRemove())

	text = "Ты можешь поболтать с кем-то еще, купив lampa-подписку"
	day = InlineKeyboardButton(text="3 дня", callback_data="3days")
	week = InlineKeyboardButton(text="Неделя", callback_data="week")
	month = InlineKeyboardButton(text="Месяц", callback_data="month")
	no_sps = InlineKeyboardButton(text="Не сейчас", callback_data="no_sps")
	reply_markup = InlineKeyboardMarkup([[day],[week],[month],[no_sps]])

	context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

	logger.info("User %s: try to subscribe;", chat_id)
	return States.SUB


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
	return States.SUB_REFUSAL

# why user do not want to pay
def other(update, context):
	chat_id = update.callback_query.message.chat.id
	message_id = update.callback_query.message.message_id
	context.bot.delete_message(chat_id, message_id)

	# Что нажал пользователь в no_sps
	data = update.callback_query.data
	
	# Просим пояснить за базар
	if data == 'other':
		text = 'Расскажите пожалуйста почему?'
		context.bot.send_message(chat_id=chat_id, text=text)
		logger.info("User %s: take other;", chat_id)
		return States.SUB_REFUSAL_EXPLAINED

	# Понятная причина reason1 or reason2
	else:
		logger.info("User %s: take 1-2 reason;", chat_id)
		payment_refused(data)

		# Тут надо так, ибо update спецефический
		return sps_buy(update.callback_query, context)

# Конец опросника "Пояснение за базар!)"
def sps_buy(update, context):
	reason = update.message.text
	payment_refused(reason)
	
	reply_markup=ReplyKeyboardMarkup(keyboard=start_kb, resize_keyboard=True)
	text = 'Спасибо, друг!) Я всегда тебе рад, если вдруг будет грустно и захочется с кем-то поговорить 🙂'
	update.message.reply_text(text=text, reply_markup=reply_markup)
	logger.info("User %s: subscribed;", update.message.chat.id)
	return ConversationHandler.END

# sendInvoice
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
		provider_token="381764678:TEST:16213",
		currency="RUB",
		need_email=True,
		prices=[description[update.data][1]])
	logger.info("User %s: get Invoice on %s;", update.message.chat.id, update.data)

# И это обработчик платежки
def precheckout_callback(update, context):
    query = update.pre_checkout_query
    chat_id = update.effective_user.id
    payment_id = query.id
    email =  query.order_info.email
    term = query.invoice_payload

    if query.invoice_payload not in ['3days','week','month']:
        query.answer(ok=False, error_message="Smthn went wrong ...")
    else:    	
    	DB.newSubscriber(chat_id, term)
    	DB.createNewPayment(payment_id, chat_id, email, term)
    	query.answer(ok=True)

# Это обработчик платежки
def successful_payment_callback(update, context):
	reply_markup=ReplyKeyboardMarkup(keyboard=start_kb, resize_keyboard=True)
	update.message.reply_text("Как хорошо, что ты здесь!) Узнаем твоё настроение?🦄", reply_markup=reply_markup)
	logger.info("User %s: subscribed", update.message.chat.id)

# Остановка хэндлера, аля отмены
def cancel(update, context):
	text = 'Готово!'
	update.message.reply_text(text=text)
	logger.info("User %s: cancel;", update.message.chat.id)