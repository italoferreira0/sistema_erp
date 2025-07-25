from django.urls import path

from companies.views.employees import Employees, EmployeeDatail

urlpatterns = [
    # Employees Endpoints
    path('employees', Employees.as_view()), 
    path('employees/<int:employee_id>', EmployeeDatail.as_view())  # corrigido: as_view()
]
