from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from retribution.apps.users.models import Employee
from retribution.apps.users.decorators import user_employee_required
from retribution.core.utils import normalize_phone

from .forms import AddEmployeeForm, ChangeDestinationForm


@user_employee_required
def index(request):
    employees = Employee.objects.filter(user__is_active=True)
    query = request.GET.get('query', '').strip()
    if query:
        if query.isdigit():
            employees = employees.filter(
                user__mobile_number__startswith=normalize_phone(query))
        else:
            employees = employees.filter(
                Q(user__name__istartswith=query) |
                Q(user__email__istartswith=query)
            )

    context_data = {
        'employees': employees,
        'destinations': employees,
        'title': 'Employees',
    }
    return render(request, 'backoffice/employees/index.html', context_data)


@user_employee_required
def add(request):
    form = AddEmployeeForm(data=request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Employee has been successfully added')
        return redirect(reverse('backoffice:employees:index'))

    context_data = {
        'form': form,
        'title': 'Add Employee',
    }
    return render(request, 'backoffice/employees/add.html', context_data)


@user_employee_required
def edit_destination(request, id):
    employee = get_object_or_404(Employee, id=id)
    form = ChangeDestinationForm(
        data=request.POST or None,
        initial={
            'destinations': [destination.id for destination in employee.destinations.all()],
        }
    )
    if form.is_valid():
        form.save(employee)
        messages.success(request, 'Employee has been successfully updated')
        return redirect('backoffice:employees:index')

    context_data = {
        'form': form,
        'title': 'Edit Employee',
    }
    return render(request, 'backoffice/employees/add.html', context_data)


@user_employee_required
def detail(request, id):
    employee = Employee.objects.get(id=id)
    context_data = {
        'employee': employee,
        'destinations': employee.destinations.all(),
        'title': 'Customer details',
    }
    return render(request, 'backoffice/employees/details.html', context_data)
