from django.db import models
from django.db.models.deletion import CASCADE

from phonenumber_field.modelfields import PhoneNumberField


class Customer(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='Внешний ID покупателя',
        unique=True,
    )
    tg_username = models.CharField(
        'Имя покупателя в Телеграме',
        max_length=256,
        blank=True,
        default='',
    )
    first_name = models.CharField(
        'Имя',
        max_length=50,
        # blank=True,
        # default='',
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=50,
    )
    midle_name = models.CharField(
        'Отчество',
        max_length=50,
    )
    passport_series = models.PositiveIntegerField(
        'Серия паспорта',
        max_length=4,
    )
    passport_number = models.PositiveIntegerField(
        'Серия паспорта',
        max_length=6,
    )
    phone_number = PhoneNumberField()

    GDPR_status = models.BooleanField(null=True, default=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.external_id})'

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'


class Storages(models.Model):
    title = models.CharField(
        'Короткое название',
        max_length=50,
    )
    city = models.CharField(
        'Город',
        max_length=50,
    )
    address = models.CharField(
        'Адрес',
        max_length=256,
    )
    space = models.PositiveIntegerField('Складская площадь')
    free_space = models.PositiveIntegerField('Свободно м2')
    occupied_space = models.PositiveIntegerField('Занято м2')

    def __str__(self):
        return f'{self.address} {self.free_space}/{self.occupied_space} м2'

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'


class Order(models.Model):
    order_id = models.PositiveIntegerField(
        'Номер заказа',
        null=True,
        unique=True,
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=CASCADE,
    )
    storage = models.ForeignKey(
        Storages,
        on_delete=CASCADE,
    )
    space_ordered = models.PositiveIntegerField('Арендованно м2')
    order_price = models.PositiveIntegerField(
        verbose_name='Цена заказа',
    )
    start_at = models.DateTimeField('Начало аренды')
    finished_at = models.DateTimeField('Конец аренды')
    qr_code = models.ImageField('QR код')

    def __str__(self):
        return f'{self.order_id} / {self.storage.title} / {self.finished_at}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
