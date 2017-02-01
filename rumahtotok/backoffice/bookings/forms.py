from datetime import timedelta

from django import forms
from django.utils import timezone
from model_utils import Choices

from rumahtotok.apps.bookings.models import Booking
from rumahtotok.apps.stores.models import Store
from rumahtotok.apps.therapists.models import Therapist


class BaseBookingForm(forms.ModelForm):
    date = forms.DateField(input_formats=["%Y-%m-%d"])
    therapist = forms.ModelChoiceField(queryset=Therapist.objects.select_related("user"))

    def __init__(self, order, created_by, *args, **kwargs):
        super(BaseBookingForm, self).__init__(*args, **kwargs)
        self.created_by = created_by
        self.order = order

    class Meta:
        model = Booking
        fields = ('date', 'store', 'therapist', 'notes')

    def clean_date(self):
        date = self.cleaned_data['date']

        if date < timezone.localtime(timezone.now()).date():
            raise forms.ValidationError("Please specify a future booking time")

        if date > timezone.localtime(timezone.now() + timedelta(days=30)).date():
            raise forms.ValidationError("Specify booking time within 30 days from today")

        return date

    def clean(self):
        cleaned_data = super(BaseBookingForm, self).clean()
        if self.errors:
            return cleaned_data

        therapist = cleaned_data['therapist']
        store = cleaned_data['store']

        if cleaned_data['therapist'] not in store.therapists.all():
            self.add_error('therapist', "%s not available in %s" % (
                therapist.user.name, store.name))

        return cleaned_data


class BookingCreationForm(BaseBookingForm):
    def __init__(self, *args, **kwargs):
        super(BookingCreationForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(BookingCreationForm, self).clean()
        if self.errors:
            return cleaned_data

        if not cleaned_data['store'].available_for_booking(self.order.user, cleaned_data['date']):
            raise forms.ValidationError("%s Store already full" % cleaned_data['store'].name)

        if self.order.bookings.filter(date=cleaned_data['date']).exists():
            raise forms.ValidationError("Duplicate booking detected in the same day.")

        if not self.order.completed_paid and self.order.total_booking > 0:
            raise forms.ValidationError("Please complete your payment for add another booking.")

        if self.order.calculate_total_booking() >= self.order.service.max_booking:
            raise forms.ValidationError("Booking has been reaches the maximum number of visit")

        return cleaned_data

    def save(self, *args, **kwargs):
        kwargs['commit'] = False
        booking = super(BookingCreationForm, self).save(*args, **kwargs)
        booking.order = self.order
        booking.duration = self.order.service.time_needed
        booking.created_by = self.created_by
        booking.therapist = self.cleaned_data['therapist']
        booking.platform = Booking.PLATFORM.backoffice
        booking.save()

        booking.create_workflow()
        return booking


class BookingEditForm(BaseBookingForm):

    def __init__(self, *args, **kwargs):
        super(BookingEditForm, self).__init__(*args, **kwargs)
        self.booking = kwargs['instance']
        self.fields['date'].initial = self.booking.date.strftime("%Y/%m/%d")

    def save(self, *args, **kwargs):
        self.booking.date = self.cleaned_data['date']
        self.booking.store = self.cleaned_data['store']
        self.booking.therapist = self.cleaned_data['therapist']
        self.booking.created_by = self.created_by
        self.booking.save()
        return self.booking


class BookingFilterForm(forms.Form):
    STATUS = Choices(
        (str(Booking.STATUS.canceled), 'canceled', 'Canceled'),
        (str(Booking.STATUS.completed), 'completed', 'Completed'),
        ('99', 'active', 'Active')
    )
    status = forms.MultipleChoiceField(choices=STATUS, required=False,
                                       widget=forms.CheckboxSelectMultiple())
    REVIEW_STATUS = Choices(
        ('1', 'reviewed', 'Reviewed'),
        ('2', 'not_reviewed', 'Not Reviewed'),
    )
    review_status = forms.MultipleChoiceField(choices=REVIEW_STATUS, required=False,
                                              widget=forms.CheckboxSelectMultiple())

    store = forms.ModelMultipleChoiceField(
        queryset=None, required=False, widget=forms.CheckboxSelectMultiple())

    def __init__(self, store_ids, *args, **kwargs):
        super(BookingFilterForm, self).__init__(*args, **kwargs)
        self.store_ids = store_ids
        self.fields['store'].queryset = Store.objects.filter(id__in=store_ids)

    def get_bookings(self):
        review_statuses = self.cleaned_data['review_status']
        statuses = self.cleaned_data['status']
        stores = self.cleaned_data['store']

        bookings = Booking.objects.select_related("therapist__user")\
            .select_related("order__user")

        if statuses:
            list_filter = []
            if self.STATUS.active in statuses:
                list_filter += [Booking.STATUS.new, Booking.STATUS.assigned]

            if self.STATUS.canceled in statuses:
                list_filter.append(self.STATUS.canceled)

            if self.STATUS.completed in statuses:
                list_filter.append(self.STATUS.completed)

            bookings = bookings.filter(status__in=list_filter)

        if not stores:
            bookings = bookings.filter(store__in=self.store_ids)
        else:
            bookings = bookings.filter(store__in=stores)

        if review_statuses:
            if review_statuses == [self.REVIEW_STATUS.reviewed,
                                   self.REVIEW_STATUS.not_reviewed]:
                return bookings

            elif self.REVIEW_STATUS.reviewed in review_statuses:
                bookings = bookings.exclude(rating=None)

            elif self.REVIEW_STATUS.not_reviewed in review_statuses:
                bookings = bookings.filter(rating=None)

        return bookings
