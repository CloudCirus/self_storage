from django.contrib import admin

from .models import *

admin.site.register(Customer)
admin.site.register(Storage)
admin.site.register(Storage_item)
admin.site.register(Order)
