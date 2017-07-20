from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.shortcuts import redirect, render
from django.http import JsonResponse

from retribution.backoffice.retributions.forms import BaseRetributionForm

from .forms import LoginForm


def login_view(request):
    form = LoginForm(data=request.POST or None)
    if form.is_valid():
        a = form.save()
        print a
        return
        # login(request, auth_form.get_user())
        # if request.user.is_superuser:
        #     return redirect('backoffice:retributions:index')
        # else:
        #     return redirect('backoffice:retributions:add')

    context_data = {
        'form': form,
        'title': 'Login'
    }
    return render(request, 'backoffice/login.html', context_data)


def create(request):
    form = BaseRetributionForm(data=request.POST or None, user=request.user)
    if form.is_valid():
        retribution = form.save()

        transport_id = ""
        if retribution.transport_id:
            transport_id = "(%s)" % retribution.transport_id

        response = {
            "name": retribution.destination.name,
            "address": retribution.destination.address,
            "time": retribution.created.strftime("%d %B %Y, %H:%M"),
            "barcode": retribution.generate_barcode,
            "qr_code": retribution.qr_code,
            "type": retribution.get_type_display(),
            "quantity": retribution.quantity,
            "transport": retribution.get_transport_display() or "-",
            "transport_id": transport_id,
            "price": '{0:,}'.format(retribution.price)
        }
        return JsonResponse(response, status=200)

    return JsonResponse({"error": form.errors.values()[0][0]}, status=400)


def log_out(request):
    logout(request)
    return redirect('backoffice:login')


def index(request):
    if request.user.is_superuser:
        return redirect('backoffice:retributions:index')
    else:
        return redirect('backoffice:retributions:add')


def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('backoffice:login')

    context_data = {
        'title': 'Change Password',
        'current_page': 'change_password',
        'form': form
    }
    return render(request, 'backoffice/users/add.html', context_data)
