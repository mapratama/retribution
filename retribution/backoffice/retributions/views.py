from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from retribution.apps.retributions.models import Retribution
from retribution.apps.users.decorators import user_employee_required
from retribution.core.utils import normalize_phone, Page

from .forms import BaseRetributionForm, RetributionFilterForm


@user_employee_required
def index(request):
    initial = {
        'type': [Retribution.TYPE.local, Retribution.TYPE.mancanegara],
        'transport': [Retribution.TRANSPORT.motor]
    }

    query_parameters = request.GET.copy()
    if 'page' in query_parameters:
        del query_parameters['page']

    form = RetributionFilterForm(data=query_parameters or None, initial=initial)
    if form.is_valid():
        retributions = form.get_bookings()
    else:
        retributions = Retribution.objects\
            .filter(transport__in=[Retribution.TRANSPORT.motor])\
            .select_related('destination').order_by('-created')

    query = request.GET.get('query', '').strip()
    if query:
        if query.isdigit():
            retributions = retributions.filter(
                mobile_number__startswith=normalize_phone(query))
        else:
            retributions = retributions.filter(
                Q(transport_id__contains=query) |
                Q(qr_code__istartswith=query)
            )

    if len(query_parameters) > 0:
        query_parameters = "&%s" % query_parameters.urlencode()
    else:
        query_parameters = ''

    page = request.GET.get('page', 1)
    paginator = Page(retributions, page, step=10)
    context_data = {
        'retributions': paginator.objects,
        'paginator': paginator,
        'title': 'Retributions',
        'query': query,
        'form': form,
        'total_customer': retributions.count(),
        'query_parameters': query_parameters
    }
    return render(request, 'backoffice/retributions/index.html', context_data)


@user_employee_required
def add(request):
    form = BaseRetributionForm(data=request.POST or None)
    if form.is_valid():
        retribution = form.save(request.user)
        context_data = {'retribution': retribution}
        # return redirect(reverse('backoffice:retributions:add'))
        return render(request, 'backoffice/retributions/print.html', context_data)

    context_data = {
        'form': form,
        'title': 'Add Retribution',
    }
    return render(request, 'backoffice/retributions/add.html', context_data)


@user_employee_required
def detail(request, id):
    retribution = Retribution.objects.get(id=id)
    context_data = {
        'retribution': retribution,
        'title': 'Retribution details',
    }
    return render(request, 'backoffice/retributions/details.html', context_data)
