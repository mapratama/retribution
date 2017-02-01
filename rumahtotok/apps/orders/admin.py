from django.contrib import admin

from .models import Order
from .models import PaymentConfirmation


class PaymentConfirmationInline(admin.StackedInline):
    model = PaymentConfirmation
    fk_name = "order"


class OrderAdmin(admin.ModelAdmin):
    inlines = [PaymentConfirmationInline]

admin.site.register(Order, OrderAdmin)
admin.site.register(PaymentConfirmation)
