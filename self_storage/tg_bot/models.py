from django.db import models
from django.db.models.deletion import CASCADE

from phonenumber_field.modelfields import PhoneNumberField


class Customer(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='Внешний ID покупателя',
        unique=True,
    )
    tg_username = models.CharField(
        verbose_name='Имя покупателя в телеграм',
        max_length=256,
        blank=True,
        default='',
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=50,
        # blank=True,
        # default='',
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=50,
    )
    midle_name = models.CharField(
        verbose_name='Отчество',
        max_length=50,
    )
    passport_series = models.PositiveIntegerField(
        verbose_name='Серия паспорта',
        default=1,
    )
    passport_number = models.PositiveIntegerField(
        verbose_name='Номер паспорта',
        default=1,
    )
    phone_number = PhoneNumberField(
        verbose_name='Номер телефона',
        default='',
    )

    GDPR_status = models.BooleanField(
        verbose_name='Согласие?',
        null=True,
        default=False
    )

    birthday = models.DateTimeField(
        verbose_name='Дата рождения',
        null=True,
    )

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.external_id})'

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'


class Storage(models.Model):
    title = models.CharField(
        verbose_name='Короткое название',
        max_length=50,
    )
    city = models.CharField(
        verbose_name='Город',
        max_length=50,
    )
    address = models.CharField(
        verbose_name='Адрес',
        max_length=256,
    )
    space = models.PositiveIntegerField(
        verbose_name='Складская площадь',
    )
    occupied_space = models.PositiveIntegerField(
        verbose_name='Занято м2',
        null=True,
    )

    def __str__(self):
        return f'{self.address}'

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'


class Storage_item(models.Model):
    title = models.CharField(
        verbose_name='Складская единица',
        max_length=50,
    )
    price_week = models.IntegerField(
        verbose_name='Цена нед.',
        default=False
    )
    price_month = models.IntegerField(
        verbose_name='Цена мес.',
        default=False
    )
    occupied_space = models.PositiveIntegerField(
        verbose_name='Занимает м2',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Колличество',
    )
    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Складская единица'
        verbose_name_plural = 'Складские единицы'


# class Ordered_space(models.Model):
#     customer = models.ForeignKey(
#         Customer,
#         verbose_name='Клиент',
#         on_delete=CASCADE,
#     )
#     item = models.ForeignKey(
#         Storage_item,
#         verbose_name='Складская единица',
#         on_delete=CASCADE,
#     )
#     amount = models.PositiveIntegerField(
#         verbose_name='Количество',
#         default=1,
#     )
#     price = models.PositiveIntegerField(
#         verbose_name='Цена',
#     )

#     def __str__(self):
#         return f'{self.customer}'

#     class Meta:
#         verbose_name = 'Арендованно м2'


class Order(models.Model):
    order_id = models.PositiveIntegerField(
        verbose_name='Номер заказа',
        null=True,
        unique=True,
    )
    customer = models.ForeignKey(
        Customer,
        verbose_name='Клиент',
        on_delete=CASCADE,
        null=True,
    )
    storage = models.ForeignKey(
        Storage,
        verbose_name='Склад',
        on_delete=CASCADE,
        null=True,
    )
    item = models.ForeignKey(
        Storage_item,
        verbose_name='Вещи в заказе',
        on_delete=CASCADE,
        null=True,
    )
    space_ordered = models.PositiveIntegerField(
        verbose_name='Арендованно м2',
        null=True,
    )
    price = models.PositiveIntegerField(
        verbose_name='Цена заказа',
        null=True,
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество сезонных вещей',
        null=True,
    )
    start_at = models.DateTimeField(
        verbose_name='Начало аренды',
        null=True,
    )
    finished_at = models.DateTimeField(
        verbose_name='Конец аренды',
        null=True,
    )
    qr_code = models.ImageField(
        verbose_name='QR код',
        null=True,
    )

    is_active = models.BooleanField(
        verbose_name='Заказ в процессе создания',
        default=True
    )

    def __str__(self):
        return f'{self.order_id} / {self.storage.title} / {self.finished_at}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
