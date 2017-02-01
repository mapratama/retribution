from datetime import timedelta

from django import forms
from django.utils import timezone

from rumahtotok.apps.bookings.models import Booking
from rumahtotok.apps.orders.models import Order
from rumahtotok.apps.stores.models import Store
from rumahtotok.apps.services.models import Service


class PreviewBookingForm(forms.Form):
    date = forms.DateField(input_formats=["%Y-%m-%d"])
    store = forms.ModelChoiceField(queryset=Store.objects.filter(is_active=True))
    service = forms.ModelChoiceField(queryset=None, required=False)

    def __init__(self, user, *args, **kwargs):
        super(PreviewBookingForm, self).__init__(*args, **kwargs)
        self.user = user
        self.fields['service'].queryset = Service.objects.filter(is_active=True)

    def clean_date(self):
        date = self.cleaned_data['date']

        if date < timezone.localtime(timezone.now()).date():
            raise forms.ValidationError("Please specify a future booking time")

        if date > timezone.localtime(timezone.now() + timedelta(days=30)).date():
            raise forms.ValidationError("Specify booking time within 30 days from today")

        return date

    def clean(self):
        cleaned_data = super(PreviewBookingForm, self).clean()

        if self.errors:
            return

        date = cleaned_data['date']
        store = cleaned_data['store']

        if not store.available_for_booking(self.user, date):
            raise forms.ValidationError("%s Store already full" % store.name)

        return cleaned_data


class EditBookingForm(forms.Form):
    date = forms.DateField(input_formats=["%Y-%m-%d"])
    booking = forms.ModelChoiceField(queryset=None)
    store = forms.ModelChoiceField(queryset=Store.objects.filter(is_active=True))

    def __init__(self, user, *args, **kwargs):
        super(EditBookingForm, self).__init__(*args, **kwargs)
        self.user = user
        self.fields['booking'].queryset = Booking.objects.filter(order__user=user) \
            .exclude(status=Booking.STATUS.canceled)

    def clean_date(self):
        date = self.cleaned_data["date"]

        if self.cleaned_data["date"] < timezone.localtime(timezone.now()).date():
            raise forms.ValidationError("Please specify future booking time")

        return date

    def clean(self):
        cleaned_data = super(EditBookingForm, self).clean()

        if self.errors:
            return cleaned_data

        booking = cleaned_data["booking"]
        store = cleaned_data["store"]
        date = cleaned_data["date"]

        if date == booking.date and store == booking.store:
            raise forms.ValidationError("No changes detected for this booking")

        return cleaned_data

    def save(self):
        booking = self.cleaned_data['booking']

        booking.date = self.cleaned_data['date']
        booking.store = self.cleaned_data['store']
        booking.platform = Booking.PLATFORM.api
        booking.created_by = self.user
        booking.save()

        return booking


class BookingCreationForm(PreviewBookingForm):
    order = forms.ModelChoiceField(queryset=None)

    def __init__(self, user, *args, **kwargs):
        super(BookingCreationForm, self).__init__(user, *args, **kwargs)
        self.fields['order'].queryset = self.user.orders.exclude(status=Order.STATUS.completed)

    def clean(self):
        cleaned_data = super(PreviewBookingForm, self).clean()

        if self.errors:
            return

        order = cleaned_data["order"]
        date = cleaned_data["date"]

        if order.total_booking > 0 and not order.completed_paid:
            raise forms.ValidationError("Please complete your payment for add another booking.")

        if order.total_booking >= order.service.max_booking:
            raise forms.ValidationError("Booking has been reaches the maximum number.")

        if order.bookings.filter(date=date).exists():
            raise forms.ValidationError("Duplicate booking detected in the same day.")

        return cleaned_data

    def save(self):
        self.order = self.cleaned_data['order']

        booking = self.order.bookings.create(
            duration=self.order.service.time_needed,
            date=self.cleaned_data['date'],
            store=self.cleaned_data['store'],
            platform=Booking.PLATFORM.backoffice,
            created_by=self.user
        )

        booking.create_workflow()

        return booking


class BookingCancelationForm(forms.Form):
    booking = forms.ModelChoiceField(queryset=None)

    def __init__(self, user, *args, **kwargs):
        super(BookingCancelationForm, self).__init__(*args, **kwargs)
        self.fields['booking'].queryset = Booking.objects.filter(order__user=user) \
            .exclude(status=Booking.STATUS.canceled)

    def clean_booking(self):
        booking = self.cleaned_data.get('booking')
        if not booking.can_reprocessed():
            raise forms.ValidationError("Booking can't be canceled")
        return booking


class BookingReviewForm(forms.Form):
    booking = forms.ModelChoiceField(queryset=None)
    rating = forms.IntegerField(min_value=1, max_value=5)
    review = forms.CharField(required=False)

    def __init__(self, user, *args, **kwargs):
        super(BookingReviewForm, self).__init__(*args, **kwargs)
        self.user = user
        self.fields['booking'].queryset = Booking.objects.filter(order__user=user)\
            .filter(status=Booking.STATUS.completed)

    def clean_booking(self):
        booking = self.cleaned_data.get('booking')
        if booking.rating or booking.review:
            raise forms.ValidationError('This booking has been reviewed')
        return booking

    def save(self):
        booking = self.cleaned_data['booking']
        booking.rating = self.cleaned_data['rating']
        booking.review = self.cleaned_data['review']
        booking.save(update_fields=['rating', 'review'])
        return booking
