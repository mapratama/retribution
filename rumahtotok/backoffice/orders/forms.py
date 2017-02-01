from django import forms
from django.core.urlresolvers import reverse_lazy

from model_utils import Choices

from rumahtotok.apps.orders.models import Order
from rumahtotok.apps.promotions.models import Promotion
from rumahtotok.apps.services.models import Service
from rumahtotok.apps.treatments.models import Treatment
from rumahtotok.apps.users.models import User

from rumahtotok.core.widgets import AjaxTypeaheadWidget


class OrderCreationForm(forms.Form):
    user = forms.CharField(label='Customer', required=True,
                                 widget=AjaxTypeaheadWidget(url=reverse_lazy('backoffice:customers:search'),
                                                            data_type='typeahead-identifier'))
    treatment = forms.ModelChoiceField(queryset=None)
    service = forms.ModelChoiceField(queryset=None)
    promotion_code = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(OrderCreationForm, self).__init__(*args, **kwargs)
        self.fields['treatment'].queryset = Treatment.objects.filter(
            is_active=True)
        self.fields['user'].queryset = User.objects.filter(
            is_active=True, type=User.TYPE.customer)
        self.fields['service'].queryset = Service.objects.filter(
            is_active=True)
        self.promotion = None

    def clean_user(self):
        identifier = self.cleaned_data.get('user').lower().partition('<')[-1].rpartition('>')[0]
        user = User.objects.get(mobile_number=identifier)
        if not user:
            raise forms.ValidationError("Customer not found")

        return user

    def clean(self):
        cleaned_data = super(OrderCreationForm, self).clean()

        if self.errors:
            return cleaned_data

        user = cleaned_data['user']
        service = cleaned_data['service']
        promotion_code = cleaned_data['promotion_code']

        if not promotion_code:
            return cleaned_data

        self.promotion = Promotion.objects.filter(code=promotion_code).first()
        if not self.promotion:
            self.add_error('promotion_code', "Promotion code is not valid")
            return cleaned_data

        is_valid, error_message = self.promotion.validate(user, service)
        if not is_valid:
            self.add_error('promotion_code', error_message)

        return cleaned_data

    def save(self, *args, **kwargs):
        user = self.cleaned_data['user']
        service = self.cleaned_data['service']
        promotion_code = self.cleaned_data['promotion_code']
        price = service.price
        discount = 0

        if self.promotion:
            discount = self.promotion.calculate_discount(price)

        order = user.orders.create(
            service=service, promotion_code=promotion_code,
            price=service.price, discount=discount)

        order.create_workflow()
        return order


class OrderFilterForm(forms.Form):
    STATUS = Choices(
        (str(Order.STATUS.canceled), 'canceled', 'Canceled'),
        (str(Order.STATUS.completed), 'completed', 'Completed'),
        ('99', 'active', 'Active')
    )
    status = forms.MultipleChoiceField(choices=STATUS, required=False,
                                       widget=forms.CheckboxSelectMultiple())
    PAYMENT_STATUS = Choices(
        ('1', 'paid', 'Paid'),
        ('2', 'credit', 'Credit'),
    )
    payment_status = forms.MultipleChoiceField(choices=PAYMENT_STATUS, required=False,
                                               widget=forms.CheckboxSelectMultiple())

    def get_orders(self):
        payment_statuses = self.cleaned_data['payment_status']
        statuses = self.cleaned_data['status']
        orders = Order.objects.select_related('user')\
            .select_related('service').order_by('-id')

        if statuses:
            list_filter = []
            if self.STATUS.active in statuses:
                list_filter += [Order.STATUS.created, Order.STATUS.confirmed, Order.STATUS.in_progress]

            if self.STATUS.canceled in statuses:
                list_filter.append(self.STATUS.canceled)

            if self.STATUS.completed in statuses:
                list_filter.append(self.STATUS.completed)

            orders = orders.filter(status__in=list_filter)

        if payment_statuses:
            if payment_statuses == [self.PAYMENT_STATUS.paid,
                                    self.PAYMENT_STATUS.credit]:
                return orders

            elif self.PAYMENT_STATUS.paid in payment_statuses:
                orders = orders.filter(completed_paid=True)

            elif self.PAYMENT_STATUS.credit in payment_statuses:
                orders = orders.filter(completed_paid=False)

        return orders
