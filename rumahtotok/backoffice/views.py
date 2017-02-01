from django.core.cache import cache
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from rumahtotok.apps.stores.models import Store


def login_view(request):
    auth_form = AuthenticationForm(data=request.POST or None)
    if auth_form.is_valid():
        login(request, auth_form.get_user())
        user = auth_form.get_user()

        employee = user.employees.first()
        if employee:
            stores = employee.stores.all()

        if user.is_superuser:
            strore_id = Store.objects.filter(is_active=True).values_list('id', flat=True)
        else:
            strore_id = stores.values_list("id", flat=True)

        cache.set(user.code, strore_id)
        return redirect('backoffice:bookings:index')
    else:
        invalid_data = request.method == 'POST'

    list(messages.get_messages(request))
    context_data = {
        'form': auth_form,
        'invalid_data': invalid_data,
        'title': 'Login'
    }
    return render(request, 'backoffice/login.html', context_data)


def log_out(request):
    logout(request)
    return redirect('backoffice:login')


def index(request):
    return redirect('backoffice:bookings:index')
