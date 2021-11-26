import time

from environs import Env

from django.core.management.base import BaseCommand

import logging
from datetime import datetime, timedelta

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, KeyboardButton
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

from tg_bot.models import Storage, Customer, Storage_item, Order

env = Env()
env.read_env()

telegram_token = env.str('TG_TOKEN')

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

(
    MAIN,  # склады
    CHOOSE_THINGS,  # что будем хранить “сезонные вещи” и “другое” def choose_things
    STORAGE_COND,  # выбираем, что будем хранить
    OTHER_ITEMS,  # стоимость хранения в неделю/месяц other
    STORAGE_PERIOD,  # период хранения storage_period
    SEASONAL_ITEMS,  # skis/snowboard/bicycle/wheels seasonal_items
    PD,  # добавляем ПД в БД, def add_pd
    ADD_PERSONAL_INFO,  # добавляем ПД в БД, def add_pd
    PAYMENT,  # добавляем ПД в БД, def add_pd get_payment

) = range(9)


def split(arr, size):
    arrs = []
    while len(arr) > size:
        pice = arr[:size]
        arrs.append(pice)
        arr = arr[size:]
    arrs.append(arr)
    return arrs


# БОТ - начало
def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    keyboard = []
    warehouses = Storage.objects.all()
    for warehouse in warehouses:
        keyboard.append([warehouse.address])

    update.message.reply_text(
        f'Привет, {user.first_name}!\n'
        'Я помогу вам арендовать личную ячейку для хранения вещей.\n'
        'Давайте посмотрим адреса складов, чтобы выбрать ближайший!',
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )

    return CHOOSE_THINGS


def get_warehouses(update, context):
    pass


def choose_things(update: Update, context: CallbackContext):
    user = update.effective_user

    customer, _ = Customer.objects.get_or_create(external_id=update.message.chat_id)
    customer.first_name = user.first_name
    customer.last_name = user.last_name or '-'
    customer.save()
    Order.objects.create(
        order_id=update.message.chat_id + int(time.time()),
        storage=Storage.objects.get(address=update.effective_message.text),
        customer=customer,
    )

    keyboard = [['Сезонное'], ['Другое']]
    update.message.reply_text(
        'Что хотите хранить?\n',
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return STORAGE_COND


def get_storage_conditions(update: Update, context: CallbackContext):
    user_input = update.effective_message.text
    if user_input == 'Сезонное':
        return SEASONAL_ITEMS
    if user_input == 'Другое':
        keyboard = []
        storage_cells = Storage_item.objects.filter(title__contains='sqm')
        for cell in storage_cells:
            keyboard.append(f'{cell.title} {cell.price_month} руб.')
        other_things_keyboard = split(keyboard, 5)
        update.message.reply_text(
            'Здесь будут условия хранения. Кстати где их взять?\n',
            reply_markup=ReplyKeyboardMarkup(other_things_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return STORAGE_PERIOD


def get_storage_period(update, context):
    user_input = update.effective_message.text
    active_order = Order.objects.get(is_active=True, customer__external_id=update.message.chat_id)
    active_order.price = int(user_input.split()[1])
    active_order.save()

    keyboard = [
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'
    ]
    storage_period_keyboard = split(keyboard, 4)

    update.message.reply_text(
        'Выберите, пожалуйста, период хранения (мес.)\n',
        reply_markup=ReplyKeyboardMarkup(storage_period_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return PD


def get_seasonal_items():
    return STORAGE_PERIOD


def add_pd():
    pass
    return PD


def add_personal_info():
    pass
    return PAYMENT


def get_payment():
    pass


# БОТ - нераспознанная команда
def unknown(update, context):
    reply_keyboard = [['ГЛАВНОЕ МЕНЮ']]
    update.message.reply_text(
        'Извините, не понял, что вы хотели этим сказать, начнем сначала',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
    )
    return MAIN


def error(bot, update, error):
    logger.error('Update "%s" caused error "%s"', update, error)
    return MAIN


class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **options):
        # Create the Updater and pass it your bot's token.
        updater = Updater(telegram_token)

        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher

        # Add conversation handler with the states CHOICE, TITLE, PHOTO, CONTACT, LOCATION
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                MAIN: [MessageHandler(Filters.text & ~Filters.command, get_warehouses)],
                PD: [MessageHandler(Filters.text & ~Filters.command, add_pd)],
                CHOOSE_THINGS: [MessageHandler(Filters.text & ~Filters.command, choose_things)],
                ADD_PERSONAL_INFO: [MessageHandler(Filters.text & ~Filters.command, add_personal_info)],
                STORAGE_COND: [MessageHandler(Filters.text & ~Filters.command, get_storage_conditions)],
                STORAGE_PERIOD: [MessageHandler(Filters.text & ~Filters.command, get_storage_period)],
                SEASONAL_ITEMS: [MessageHandler(Filters.text & ~Filters.command, get_seasonal_items)],
                PAYMENT: [MessageHandler(Filters.text & ~Filters.command, get_payment)],

            },
            fallbacks=[MessageHandler(Filters.text & ~Filters.command, unknown)],
            allow_reentry=True,
        )

        dispatcher.add_handler(conv_handler)
        dispatcher.add_error_handler(error)

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()

# def main() -> None:
#     """основная логика"""
#     env = Env()
#     env.read_env()
#
#     token = env.str('TG_TOKEN')
#     channel_id = env.str('BOT_ID')
#     print(token, channel_id)
#
#
# if __name__ == '__main__':
#     """для тестов из скрипта"""
#     main()
