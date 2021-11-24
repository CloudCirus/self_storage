from django.db import models

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
        default=''
    )
    first_name = models.CharField(
        'Имя',
        max_length=256, 
        blank=True, 
        default=''
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=256, 
        blank=True, 
        default=''
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
