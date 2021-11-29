import telegram
from environs import Env
from telegram import Update, LabeledPrice
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    PreCheckoutQueryHandler,
    CallbackContext,
    CallbackQueryHandler,
)

env = Env()
env.read_env()
provider_token = env.str('PROVIDER_TOKEN')
token = env.str('TG_TOKEN')
chat_id = env.str('BOT_ID')

bot = telegram.Bot(token=token)


def send_invoice(update: Update, context: CallbackContext):
    prices = [LabeledPrice(label="руб", amount=10000)]
    title = "SELF STORAGE"
    description = "Услуги аренды"
    payload = "YourPayload"
    currency = "RUB"
    start_parameter = "test"
    context.bot.sendInvoice(
        chat_id,
        title,
        description,
        payload,
        provider_token,
        start_parameter,
        currency,
        prices
    )


def precheckout_callback(update: Update, context: CallbackContext):
    query = update.pre_checkout_query

    if query.invoice_payload != "YourPayload":
        bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=False,
                                      error_message="Что то пошло не так")
    else:
        bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)


def successful_payment_callback(update: Update, context: CallbackContext):
    update.message.reply_text("Все готово.")


updater = Updater(token)
dispatcher = updater.dispatcher
dispatcher.add_handler(CallbackQueryHandler(send_invoice))
dispatcher.add_handler(PreCheckoutQueryHandler(precheckout_callback))
dispatcher.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback))
updater.start_polling()
