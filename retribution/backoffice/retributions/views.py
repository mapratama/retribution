import os
import imgkit

from django.db.models import Q, Sum
from django.shortcuts import render
from django.utils import timezone

from retribution.apps.destinations.models import Destination
from retribution.apps.retributions.models import Retribution
from retribution.apps.users.decorators import user_employee_required
from retribution.core.utils import normalize_phone, Page

from .forms import BaseRetributionForm, RetributionFilterForm


@user_employee_required
def index(request):
    TRANSPORT_INITIAL = [Retribution.TRANSPORT.motor, Retribution.TRANSPORT.sedan,
                         Retribution.TRANSPORT.bus]
    initial = {
        'type': [Retribution.TYPE.local],
        'transport': TRANSPORT_INITIAL,
        'destinations': Destination.objects.all(),
    }

    query_parameters = request.GET.copy()
    if 'page' in query_parameters:
        del query_parameters['page']

    form = RetributionFilterForm(data=query_parameters or None, initial=initial)
    if form.is_valid():
        retributions = form.get_bookings()
    else:
        retributions = Retribution.objects\
            .filter(transport__in=TRANSPORT_INITIAL, type__in=[Retribution.TYPE.local])\
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
        'title': 'Retributions Data',
        'query': query,
        'form': form,
        'total_retributions': retributions.count(),
        'total_customer': retributions.aggregate(Sum('quantity'))['quantity__sum'] or 0,
        'total_transaction': retributions.aggregate(Sum('price'))['price__sum'] or 0,
        'query_parameters': query_parameters
    }
    return render(request, 'backoffice/retributions/index.html', context_data)


@user_employee_required
def add(request):
    form = BaseRetributionForm(data=request.POST or None)
    context_data = {
        'form': form,
        'title': 'Add Retribution',
    }

    if form.is_valid():
        retribution = form.save(user=request.user)
        data = '''<html><body><div><table><tr><td align="center">%s</td></tr>
        <tr><td align="center">KABUPATEN SUKABUMI</td></tr><tr><td align="center"
        >=======================</td></tr><tr><td align="center"><img height="100" 
        width="100" src="data:image/png;base64, %s"></td></tr><tr><td align="center">
        Rp.  %s</td></tr><tr><td align="center">%s</td></tr><tr><td align="center"
        >=======================</td></tr><tr><td align="center">SELAMAT DATANG</td>
        </tr><tr><td align="center">GUNAKAN KUNCI TAMBAHAN</td></tr><tr></tr><tr>
        </tr></table><div></body></html>''' % \
            (retribution.destination.name.upper(), retribution.generate_barcode, 
             "{:,}".format(int(retribution.price)),
             timezone.localtime(retribution.created).strftime("%d %B %Y, %H:%M"))

        temp_file = open("temp.html","w")
        temp_file.write(data)
        temp_file.close()

        os.system("xvfb-run -- /usr/bin/wkhtmltopdf 'temp.html' 'temp_struk.pdf'")

        new_form = BaseRetributionForm(data=None)
        context_data['form'] = new_form
        os.system('lp -o media=Custom.70x80mm temp_struk.pdf')

    return render(request, 'backoffice/retributions/add.html', context_data)


@user_employee_required
def detail(request, id):
    retribution = Retribution.objects.get(id=id)

    context_data = {
        'retribution': retribution,
        'title': 'Retribution details',
    }
    return render(request, 'backoffice/retributions/details.html', context_data)
