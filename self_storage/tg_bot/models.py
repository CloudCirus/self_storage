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
        max_length=4,
    )
    passport_number = models.PositiveIntegerField(
        verbose_name='Номер паспорта',
        max_length=6,
    )
    phone_number = PhoneNumberField(
        verbose_name='Номер телефона',
    )

    GDPR_status = models.BooleanField(
        verbose_name='Согласие?',
        null=True,
        default=False
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
        verbose_name='Складская площадь'
    )
    occupied_space = models.PositiveIntegerField(
        verbose_name='Занято м2'
    )

    def __str__(self):
        return f'{self.address} {self.occupied_space}/{self.space} м2'

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'


class Storage_item(models.Model):
    title = models.CharField(
        verbose_name='Складская единица',
        max_length=50,
    )
    price = models.IntegerField(
        verbose_name='Цена',
    )
    occupied_space = models.PositiveIntegerField(
        verbose_name='Занимает м2'
    )

    def __str__(self):
        return f'{self.title} {self.price} руб'

    class Meta:
        verbose_name = 'Складская единица'
        verbose_name_plural = 'Складские единицы'


class Ordered_space(models.Model):
    customer = models.ForeignKey(
        Customer,
        verbose_name='Клиент',
        on_delete=CASCADE,
    )
    item = models.ForeignKey(
        Storage_item,
        verbose_name='Складская единица',
        on_delete=CASCADE,
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        default=1,
    )
    price = models.PositiveIntegerField(
        verbose_name='Цена',
    )

    def __str__(self):
        return f'{self.customer}'

    class Meta:
        verbose_name = 'Арендованно м2'


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
    space_ordered = models.ForeignKey(
        Ordered_space,
        verbose_name='Арендованно м2',
        on_delete=CASCADE,
    )
    price = models.PositiveIntegerField(
        verbose_name='Цена заказа',
    )
    start_at = models.DateTimeField(
        verbose_name='Начало аренды',
    )
    finished_at = models.DateTimeField(
        verbose_name='Конец аренды',
    )
    qr_code = models.ImageField(
        verbose_name='QR код',
    )

    def __str__(self):
        return f'{self.order_id} / {self.storage.title} / {self.finished_at}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
