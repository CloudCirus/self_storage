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
    STORAGE_PERIOD_OTHER,  # период хранения storage_period
    CHOOSE_SEASON_ITEMS,  # выбираем кол-во сезонных вещей
    STORAGE_PERIOD_SEASON,  # период хранения storage_period
    COUNTING_BOOKING_SEASON,  # период хранения storage_period
    COUNTING_BOOKING_OTHER,  # период хранения storage_period
    BOOKING,  # записываем цену, кнопка "Бронировать"
    PD,  # добавляем ПД в БД, def add_pd
    IS_PD,  # добавляем ПД в БД, def add_pd
    CONTACT_PHONE,  # добавляем телефон
    CONTACT_NAME,  # добавляем ФИ
    CONTACT_PASS,  # добавляем номер паспорта
    PAYMENT,  # добавляем ПД в БД, def add_pd get_payment

) = range(16)


def split(arr, size):
    arrs = []
    while len(arr) > size:
        pice = arr[:size]
        arrs.append(pice)
        arr = arr[size:]
    arrs.append(arr)
    return arrs


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
        keyboard = [['лыжи'], ['сноуборд'], ['велосипед'], ['колеса']]
        update.message.reply_text(
            'Здесь будут условия хранения сезонных вещей.\n',
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        )

        return CHOOSE_SEASON_ITEMS

    if user_input == 'Другое':
        keyboard = []
        storage_cells = Storage_item.objects.filter(title__contains='sqm')
        for cell in storage_cells:
            keyboard.append(f'{cell.title} {cell.price_month} руб.')
        other_things_keyboard = split(keyboard, 5)
        update.message.reply_text(
            'Здесь будут условия хранения других вещей.\n',
            reply_markup=ReplyKeyboardMarkup(other_things_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )

        return STORAGE_PERIOD_OTHER


def get_storage_period_other(update, context):
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
    return BOOKING


def choose_season_items(update, context):
    user_input = update.effective_message.text
    active_order = Order.objects.get(is_active=True, customer__external_id=update.message.chat_id)
    active_order.item = Storage_item.objects.get(title=user_input)
    active_order.save()
    update.message.reply_text(
        'Введите, пожалуйста, количество вещей'
    )

    return STORAGE_PERIOD_SEASON


def get_storage_period_season(update, context):
    user_input = update.effective_message.text
    active_order = Order.objects.get(is_active=True, customer__external_id=update.message.chat_id)
    active_order.quantity = int(user_input)
    active_order.save()

    keyboard = [[f'неделя {active_order.item.price_week} р.'], [f'месяц {active_order.item.price_month} р.']]

    if active_order.item.title == 'колеса':
        keyboard = [[f'месяц {active_order.item.price_month} р.']]

    update.message.reply_text(
        'Пожалуйста, выберите удобный вариант хранения\n',
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )

    return COUNTING_BOOKING_SEASON


def counting_booking_other(update, context):
    pass


def counting_season(update, context):
    user_input = update.effective_message.text
    active_order = Order.objects.get(is_active=True, customer__external_id=update.message.chat_id)
    period, price, _ = user_input.split()
    active_order.price = int(price) * active_order.quantity
    active_order.save()

    keyboard = [
        '1', '2', '3', '4', '5', '6'
    ]
    if period == 'неделя':
        keyboard = [
            '1', '2', '3', '4', '5', '6',
            '7', '8', '9', '10', '11', '12',
            '13', '14', '15', '16', '17', '18',
            '19', '20', '21', '22', '23', '24'
        ]

    counting_season_keyboard = split(keyboard, 6)

    update.message.reply_text(
        f'Укажите, пожалуйста, кол-во ({period})\n',
        reply_markup=ReplyKeyboardMarkup(counting_season_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )

    return BOOKING


def booking(update, context):
    user_input = update.effective_message.text
    active_order = Order.objects.get(is_active=True, customer__external_id=update.message.chat_id)
    active_order.price = active_order.price * int(user_input)
    active_order.save()

    update.message.reply_text(
        f'Пожалуйста, подтвердите заказ',
        reply_markup=ReplyKeyboardMarkup([['Брорнировать']], resize_keyboard=True, one_time_keyboard=True)
    )

    return IS_PD


def is_pd(update, context):
    customer = Customer.objects.get(external_id=update.message.chat_id)

    if not customer.GDPR_status:
        with open("pd.pdf", 'rb') as file:
            context.bot.send_document(chat_id=update.message.chat_id, document=file)
        reply_keyboard = [['Принять', 'Отказаться']]
        update.message.reply_text(
            text='Прошу ознакомиться с положением об обработке персональных данных.',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, resize_keyboard=True
            ),
        )
        return PD

    update.message.reply_text(
        text='Переходим к заполнению персональных данных. Укажите, пожалуйста, свой номер телефона',
        reply_markup=ReplyKeyboardMarkup(
            [['Отправить мой номер'], ['Ввести номер вручную']],
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )

    return CONTACT_PHONE


def add_pd(update, context):
    customer = Customer.objects.get(external_id=update.message.chat_id)
    answer = update.message.text

    if answer == 'Принять':
        customer.GDPR_status = True

        update.message.reply_text(
            f'Добавлено согласие на обработку данных.',
        )
        logger.info(f'Пользователю {customer.external_id}'
                    f'Добавлено согласие на обработку данных: {customer.GDPR_status}')
        customer.save()

        update.message.reply_text(
            text='Переходим к заполнению персональных данных. Укажите, пожалуйста, свой номер телефона',
            reply_markup=ReplyKeyboardMarkup(
                [['Отправить мой номер'], ['Ввести номер вручную']],
                one_time_keyboard=True,
                resize_keyboard=True,
            ),
        )

        return CONTACT_PHONE

    elif answer == 'Отказаться':
        with open("pd.pdf", 'rb') as file:
            context.bot.send_document(chat_id=update.message.chat_id, document=file)
        reply_keyboard = [['Принять', 'Отказаться']]
        update.message.reply_text(
            text='Извините, без согласия на обработку данных заказы невозможны.',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, resize_keyboard=True
            ),
        )

        return PD


def add_personal_info_phone(update, context):
    customer = Customer.objects.get(external_id=update.message.chat_id)
    answer = update.message.text
    if answer == 'Ввести номер вручную':
        update.message.reply_text(
            f'Введите номер телефона в формате +7 (код) номер',
        )

    return CONTACT_NAME


def add_personal_info_name(update, context):
    customer = Customer.objects.get(external_id=update.message.chat_id)
    customer.phone_number = update.message.text
    customer.save()
    update.message.reply_text(
        f'В Телеграм вас зовут {customer.first_name} {customer.last_name}.\n'
        f'Если желаете переименоваться, введите пожалуйста Фамилию Имя.',
    )

    return CONTACT_PASS


def add_personal_info_pass(update, context):
    customer = Customer.objects.get(external_id=update.message.chat_id)
    customer.first_name, customer.last_name = update.message.text.split()
    customer.save()
    update.message.reply_text(
        f'Введите, пожалуйста, номер паспорта в формате серия номер.\n'
    )

    return PAYMENT


def get_payment(update, context):
    customer = Customer.objects.get(external_id=update.message.chat_id)
    customer.passport_series, customer.passport_number = update.message.text.split()
    customer.save()
    active_order = Order.objects.get(is_active=True, customer__external_id=update.message.chat_id)
    active_order.is_active = False
    active_order.save()


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
        updater = Updater(telegram_token)

        dispatcher = updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={

                PD: [MessageHandler(Filters.text & ~Filters.command, add_pd)],
                IS_PD: [MessageHandler(Filters.text & ~Filters.command, is_pd)],
                CHOOSE_THINGS: [MessageHandler(Filters.text & ~Filters.command, choose_things)],
                CONTACT_PHONE: [MessageHandler(Filters.text & ~Filters.command, add_personal_info_phone)],
                CONTACT_NAME: [MessageHandler(Filters.text & ~Filters.command, add_personal_info_name)],
                CONTACT_PASS: [MessageHandler(Filters.text & ~Filters.command, add_personal_info_pass)],
                STORAGE_COND: [MessageHandler(Filters.text & ~Filters.command, get_storage_conditions)],
                STORAGE_PERIOD_OTHER: [MessageHandler(Filters.text & ~Filters.command, get_storage_period_other)],
                CHOOSE_SEASON_ITEMS: [MessageHandler(Filters.text & ~Filters.command, choose_season_items)],
                STORAGE_PERIOD_SEASON: [MessageHandler(Filters.text & ~Filters.command, get_storage_period_season)],
                COUNTING_BOOKING_SEASON: [MessageHandler(Filters.text & ~Filters.command, counting_season)],
                COUNTING_BOOKING_OTHER: [MessageHandler(Filters.text & ~Filters.command, counting_booking_other)],
                BOOKING: [MessageHandler(Filters.text & ~Filters.command, booking)],
                PAYMENT: [MessageHandler(Filters.text & ~Filters.command, get_payment)],

            },
            fallbacks=[MessageHandler(Filters.text & ~Filters.command, unknown)],
            allow_reentry=True,
        )

        dispatcher.add_handler(conv_handler)
        dispatcher.add_error_handler(error)

        updater.start_polling()

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
