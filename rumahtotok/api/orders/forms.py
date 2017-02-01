from django import forms

from rumahtotok.apps.promotions.models import Promotion
from rumahtotok.apps.payments.models import Payment
from rumahtotok.apps.services.models import Service
from rumahtotok.apps.orders.models import Order


class BaseOrderForm(forms.Form):
    service = forms.ModelChoiceField(queryset=Service.objects.filter(is_active=True))
    promotion_code = forms.CharField(required=False)

    def __init__(self, user, *args, **kwargs):
        super(BaseOrderForm, self).__init__(*args, **kwargs)
        self.user = user
        self.promotion = None

    def clean_promotion_code(self):
        promotion_code = self.cleaned_data['promotion_code']

        if not promotion_code:
            return

        self.promotion = Promotion.objects.filter(code=promotion_code).first()
        if not self.promotion:
            raise forms.ValidationError("Promotion code is not valid")

        return promotion_code


class ValidatePromotionCodeForm(BaseOrderForm):
    promotion_code = forms.CharField()

    def clean(self):
        cleaned_data = super(ValidatePromotionCodeForm, self).clean()

        if self.errors:
            return cleaned_data

        is_valid, error_message = self.promotion.validate(self.user, cleaned_data['service'])
        if not is_valid:
            self.add_error('promotion_code', error_message)

        return cleaned_data


class OrderCreationForm(BaseOrderForm):

    def clean(self):
        cleaned_data = super(OrderCreationForm, self).clean()

        if self.errors:
            return cleaned_data

        if self.user.orders.filter(completed_paid=False) \
                .exclude(status=Order.STATUS.canceled).exists():
            raise forms.ValidationError("Please complete your previous order payment")

        if self.promotion:
            is_valid, error_message = self.promotion.validate(self.user, cleaned_data['service'])
            if not is_valid:
                self.add_error('promotion_code', error_message)

        return cleaned_data

    def save(self, *args, **kwargs):
        service = self.cleaned_data['service']
        promotion_code = self.cleaned_data['promotion_code']
        price = service.price
        discount = 0

        if self.promotion:
            discount = self.promotion.calculate_discount(price)

        order = self.user.orders.create(
            service=service, promotion_code=promotion_code,
            price=service.price, discount=discount)

        order.create_workflow()

        if order.user.balance > order.discounted_price:
            payment = order.payments.create(
                balance_used=order.discounted_price,
                value=0, notes="Auto create order from API",
                created_by=order.user, method=Payment.METHOD.balance
            )
            payment.save()
            payment.update_balance()

        order.calculate_total_payment()

        return order


class OrderCancelationForm(forms.Form):

    order = forms.ModelChoiceField(queryset=None)

    def __init__(self, user, *args, **kwargs):
        super(OrderCancelationForm, self).__init__(*args, **kwargs)
        self.fields['order'].queryset = Order.objects.filter(user=user)

    def clean_order(self):
        order = self.cleaned_data.get('order')
        if not order.can_canceled():
            raise forms.ValidationError('Order can not be canceled')
        return order
