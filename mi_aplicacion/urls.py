from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # Route for displaying the list of employees with their first check-in and last check-out times for the current day
    path('empleados/', views.lista_empleados, name='lista_empleados'),

    # Route for filtering employees based on a date range and optionally by name,
    # and grouping the total worked hours per employee
    path('empleados_por_fecha/', views.empleados_por_fecha, name='empleados_por_fecha'),
    path('login/', views.login_view, name='rh_login'),
    path('logout/', views.logout_view, name='rh_logout'),
]
