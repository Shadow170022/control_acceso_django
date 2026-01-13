import pymysql
import openpyxl
import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from mexcentrix_weberp.utils.db_utils import get_company_connection, get_domain_companies
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import permission_required
from mi_aplicacion.models import Company

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('reportes')
        else:
            messages.error(request, 'Credenciales inválidas')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@permission_required('mi_aplicacion.is_finance', login_url='/login/', raise_exception=True)
def reportes(request):
    """ Obtiene los períodos disponibles y selecciona el actual """
    company_name = request.GET.get('company', 'mxcxit_rsserp')
    conn = get_company_connection(company_name)
    dominios = get_domain_companies_serializable()

    with conn.cursor() as cursor:
        cursor.execute("SELECT periodno, lastdate_in_period FROM periods ORDER BY lastdate_in_period DESC;")
        periodos = cursor.fetchall()

    conn.close()

    # Obtener el periodo actual basado en la fecha
    hoy = datetime.date.today()
    periodo_actual = None

    for periodo in periodos:
        if periodo["lastdate_in_period"].month == hoy.month and periodo["lastdate_in_period"].year == hoy.year:
            periodo_actual = periodo["periodno"]
            break

    return render(request, 'reportes.html', {'periodos': periodos, 'periodo_actual': periodo_actual, 'dominios': dominios.keys()})

def api_periodos(request):
    """Endpoint para obtener períodos de una empresa específica"""
    company_name = request.GET.get('company', 'mxcxit_rsserp')
    dominio = request.GET.get('dominio', 'mxcxit')
    print("La empresa es:", company_name)
    print("El dominio es:", dominio)
    
    # Obtener función de conexión por dominio
    dominio_data = get_domain_companies().get(dominio, {})
    connection_func = dominio_data.get('connection_func', get_company_connection)
    
    conn = connection_func(company_name)
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT periodno, lastdate_in_period FROM periods ORDER BY lastdate_in_period DESC;")
        periodos = cursor.fetchall()
    
    conn.close()
    
    # Formatear fechas
    periodos_formateados = {
        periodo['lastdate_in_period'].strftime('%Y-%m'): periodo['periodno']
        for periodo in periodos
    }
    
    return JsonResponse({
        'periodos': periodos_formateados,
        'empresa': company_name
    })

@login_required
@permission_required('mi_aplicacion.is_finance', login_url='/login/', raise_exception=True)
def descargar_excel(request):
    """ Genera el reporte de facturas en Excel filtrado por el período seleccionado """
    company_name = request.GET.get('company', 'mxcxit_rsserp')
    dominio = request.GET.get('dominio', 'mxcxit')
    print("La empresa es:", company_name)
    print("El dominio es:", dominio)
    
    dominio_data = get_domain_companies().get(dominio, {})
    connection_func = dominio_data.get('connection_func', get_company_connection)
    
    conn = connection_func(company_name)

    periodo_seleccionado = request.GET.get('periodo', None)
    periodo_tipo = request.GET.get('periodo_tipo', 'exact')

    with conn.cursor() as cursor:
        query = """
        SELECT g.counterindex, g.type, g.typeno, g.chequeno, g.trandate, g.periodno, g.account, g.narrative, g.amount,
               s.supplierno, s2.suppname as razon_social, s2.taxref as rfc,
               c.accountname, s2.address6 
        FROM gltrans g 
        LEFT JOIN supptrans s ON s.transno = g.typeno AND s.`type` = g.`type`
        LEFT JOIN suppliers s2 ON s2.supplierid = s.supplierno 
        LEFT JOIN chartmaster c ON c.accountcode = g.account
        WHERE g.`type` IN (20, 21)
        """

        # Filtrar por período si se seleccionó uno
        if periodo_seleccionado:
            if periodo_tipo == 'exact':
                query += f" AND g.periodno = {periodo_seleccionado}"
            else:
                query += f" AND g.periodno >= {periodo_seleccionado}"

        query += " ORDER BY s.supplierno, g.counterindex;"
        
        print(query)

        cursor.execute(query)
        facturas = cursor.fetchall()

    conn.close()

    # Crea un Excel con openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = dominio + "_" + company_name  # Nombre de la hoja

    # encabezados
    headers = ["CounterIndex", "Type", "TypeNo", "ChequeNo", "TranDate", "PeriodNo", "Account",
               "Narrative", "Amount", "SupplierNo", "Razon Social", "RFC", "AccountName", "Address6"]
    ws.append(headers)

    # datos
    for factura in facturas:
        ws.append([
            factura["counterindex"], factura["type"], factura["typeno"], factura["chequeno"],
            factura["trandate"], factura["periodno"], factura["account"], factura["narrative"],
            factura["amount"], factura["supplierno"], factura["razon_social"], factura["rfc"],
            factura["accountname"], factura["address6"]
        ])

    # Respuesta HTTP con el Excel
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="reporte_proveedores_periodo_{periodo_seleccionado}.xlsx"'
    wb.save(response)

    return response


@login_required
@permission_required('mi_aplicacion.is_finance', login_url='/login/', raise_exception=True)
def gltrans_report(request):
    """ Vista para mostrar formulario y resultados de GLTrans """
    dominios = get_domain_companies_serializable()
    return render(request, 'gltrans_report.html', {'dominios': dominios.keys()})

def api_gltrans_count(request):
    """ Endpoint para obtener el conteo de GLTrans """
    company_name = request.GET.get('company')
    dominio = request.GET.get('dominio')
    periodno = request.GET.get('period')
    tag = request.GET.get('tag', None)
    print("tag:", tag)

    if not all([company_name, dominio, periodno]):
        return JsonResponse({'error': 'Parámetros faltantes'}, status=400)

    try:
        dominio_data = get_domain_companies().get(dominio, {})
        connection_func = dominio_data.get('connection_func', get_company_connection)
        conn = connection_func(company_name)

        query = "SELECT COUNT(*) as total FROM gltrans WHERE periodno = " + periodno

        if tag:
            query += " AND tag = " + tag

        with conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
            total = result['total'] if result else 0

        print("La query es:", query)

        return JsonResponse({
            'total': total,
            'gl_value': total/3
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        if 'conn' in locals():
            conn.close()

def api_tags(request):
    print(request)
    company = request.GET.get('company')
    print("La empresa es:", company)
    tags = {}
    
    if company == 'mxcxit_rsserp':
        tags = {
            '0': 'None',
            '1': 'BD Medical',
            '8': 'Capital',
            '9': 'Linea 7',
            '10': 'Cracker #3',
            '11': 'SIC',
            '12': 'RSS',
            '13': 'SANOK'
        }
    elif company == 'mxcxit_ripmerp':
        tags = {
            '0': 'None',
            '1': 'SPQ',
            '2': 'BAE',
            '3': 'RIM',
            '4': 'SENKO',
            '5': 'MEXXON',
            '6': 'DAIMAY',
            '7': 'DELAB',
            '8': 'ANJI',
            '9': 'ASIAWAY',
            '10': 'CAMEL',
            '11': 'POLESTAR',
            '12': 'HTC',
            '13': 'LER',
            '16': 'SAIC',
            '17': 'QUALUS',
            '18': 'UNISON'
        }
    
    return JsonResponse({'tags': tags})

def get_domain_companies_serializable():
    dominios = get_domain_companies()  # diccionario completo
    serializable = {}
    for dominio, data in dominios.items():
        serializable[dominio] = {"companies": data.get("companies", {})}
    return serializable

def api_dominios(request):
    """Endpoint para obtener la estructura de dominios y empresas sin las funciones."""
    dominios = get_domain_companies_serializable()
    return JsonResponse(dominios)

def api_empresas(request):
    """Endpoint para obtener empresas de un dominio específico"""
    dominio = request.GET.get('dominio')
    dominios = get_domain_companies_serializable()
    usuario = request.user.username
    print(dominios)
    print("El usuario es:", usuario)
    print("El dominio es:", dominio)
    empresas = dominios.get(dominio, {}).get('companies', {})
    # Lógica de exclusión: Si no es finanzas, remover empresas
    if usuario != 'finanzas':
        empresas_a_ocultar = [
            'mxcenit_jinerp',
            'mxcenit_lererp',
            'mxcenit_suzhouerp',
            'mxcenit_tsperp',
            'mexcx_mlogerp',
            'mexcx_riaperp',
            'mexcx_tongtaierp'
            ]
        for codigo in empresas_a_ocultar:
            empresas.pop(codigo, None)  # Eliminar empresa si existe
    print("Las empresas son:", empresas)
    return JsonResponse(empresas)

def api_empresas_2(request):
    dominio = request.GET.get('dominio')
    empresas = Company.objects.filter(
        domain=dominio,
        usercompany__user=request.user
    ).values('code', 'name')
    
    return JsonResponse({e['code']: e['name'] for e in empresas})