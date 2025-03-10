from django.shortcuts import render
from django.db.models import Q, Min, Max
from .models import Empleado
from datetime import date, datetime, timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect
from django.conf import settings

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/rh/empleados_por_fecha/')  # permite la captura el parámetro 'next'
            return redirect(next_url)
        else:
            messages.error(request, 'Credenciales inválidas')
    return render(request, 'rh_login.html')

def logout_view(request):
    logout(request)
    return redirect('rh_login')

@login_required(login_url='/rh/login/')
@permission_required('mi_aplicacion.is_rh', login_url='/rh/login/', raise_exception=True)
def empleados_por_fecha(request):
    """View to filter employees by name and/or date range and group their working hours."""
    nombre = request.GET.get('nombre', '').strip()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    agrupar_total = request.GET.get('agrupar_total') == 'on'

    # Convert date strings to date objects
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
    except ValueError:
        start_date, end_date = None, None

    empleados = []
    auth_data = []
    total_horas_trabajadas = None

    if (start_date and end_date) or nombre:
        empleados_queryset = Empleado.objects.all()

        if start_date and end_date:
            empleados_queryset = empleados_queryset.filter(auth_date__range=(start_date, end_date))

        if nombre:
            empleados_queryset = empleados_queryset.filter(Q(user_name__icontains=nombre))

        if agrupar_total:
            auth_data = list(empleados_queryset.values('user_name', 'id_empleado', 'auth_date', 'auth_time'))

            auth_totals = {}
            for empleado in auth_data:
                user_name = empleado['user_name']
                id_empleado = empleado['id_empleado']
                auth_date = empleado['auth_date']
                auth_time = empleado['auth_time']

                if (user_name, id_empleado) not in auth_totals:
                    auth_totals[(user_name, id_empleado)] = {}

                if auth_date not in auth_totals[(user_name, id_empleado)]:
                    auth_totals[(user_name, id_empleado)][auth_date] = []

                if auth_time:
                    auth_totals[(user_name, id_empleado)][auth_date].append(auth_time)

            empleados = [
                {
                    'user_name': key[0],
                    'id_empleado': key[1],
                    'auth_dates': value,
                    'total_horas_trabajadas': timedelta()
                }
                for key, value in auth_totals.items()
            ]

            for empleado in empleados:
                for auth_date, auth_times in empleado['auth_dates'].items():
                    auth_times.sort()
                    first_checkin = auth_times[0]
                    last_checkout = auth_times[-1]

                    first_checkin_dt = datetime.combine(datetime.min, first_checkin)
                    last_checkout_dt = datetime.combine(datetime.min, last_checkout)
                    horas_trabajadas = last_checkout_dt - first_checkin_dt
                    empleado['total_horas_trabajadas'] += horas_trabajadas

            for empleado in empleados:
                total_seconds = int(empleado['total_horas_trabajadas'].total_seconds())
                horas_totales = total_seconds // 3600
                minutos_totales = (total_seconds % 3600) // 60
                segundos_totales = total_seconds % 60
                empleado['total_horas_trabajadas'] = f"{horas_totales:02}:{minutos_totales:02}:{segundos_totales:02}"

        else:
            empleados = empleados_queryset.values('user_name', 'id_empleado', 'auth_date').annotate(
                first_checkin=Min('auth_time'),
                last_checkout=Max('auth_time')
            ).order_by('auth_date', 'id_empleado')

            for empleado in empleados:
                checkin = empleado['first_checkin']
                checkout = empleado['last_checkout']

                if checkin and checkout:
                    checkin_datetime = datetime.combine(empleado['auth_date'], checkin)
                    checkout_datetime = datetime.combine(empleado['auth_date'], checkout)
                    horas_trabajadas = (checkout_datetime - checkin_datetime).total_seconds() / 3600
                    empleado['horas_trabajadas'] = round(horas_trabajadas, 2)
                else:
                    empleado['horas_trabajadas'] = "N/A"

    formatted_start_date = start_date.strftime('%Y-%m-%d') if start_date else ''
    formatted_end_date = end_date.strftime('%Y-%m-%d') if end_date else ''

    return render(request, 'empleados_por_fecha.html', {
        'empleados': empleados,
        'start_date': formatted_start_date,
        'end_date': formatted_end_date,
        'nombre': nombre,
        'agrupar_total': agrupar_total,
        'auth_data': auth_data if agrupar_total else None,
        'total_horas_trabajadas': total_horas_trabajadas if agrupar_total else None
    })


def lista_empleados(request):
    """View to list employees and calculate their working hours for the current day."""
    today = date.today()

    # Group by employee and get the first and last authentication record of the day
    empleados = Empleado.objects.filter(auth_date=today).values('user_name', 'id_empleado').annotate(
        first_checkin=Min('auth_time'),
        last_checkout=Max('auth_time')
    )

    # Calculate working hours if both check-in and check-out times exist
    for empleado in empleados:
        checkin = empleado['first_checkin']
        checkout = empleado['last_checkout']

        if checkin and checkout:
            checkin_datetime = datetime.combine(today, checkin)
            checkout_datetime = datetime.combine(today, checkout)
            horas_trabajadas = (checkout_datetime - checkin_datetime).total_seconds() / 3600  # Convert to hours
            empleado['horas_trabajadas'] = round(horas_trabajadas, 2)
        else:
            empleado['horas_trabajadas'] = "N/A"

    return render(request, 'empleados.html', {'empleados': empleados, 'today': today})
