from functools import wraps

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect


def user_employee_required(view_func):
    def _check_user_account(request, *args, **kwargs):
        if request.user.is_authenticated() and request.user.employees.exists():
            return view_func(request, *args, **kwargs)

        messages.info(request, 'Please login as a employee')
        return redirect(reverse('backoffice:login'))
    return wraps(view_func)(_check_user_account)


def super_user_required(view_func):
    def _check_user_account(request, *args, **kwargs):
        if request.user.is_authenticated() and request.user.employees.exists() and\
                request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        messages.info(request, "You don't have access to this page")
        return redirect(reverse('backoffice:login'))
    return wraps(view_func)(_check_user_account)
