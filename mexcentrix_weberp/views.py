import pymysql
import openpyxl
import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from mexcentrix_weberp.utils.db_utils import get_company_connection, get_domain_companies

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
    print(dominios)
    print("El dominio es:", dominio)
    empresas = dominios.get(dominio, {}).get('companies', {})
    print("Las empresas son:", empresas)
    return JsonResponse(empresas)

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
            query += f" AND g.periodno = {periodo_seleccionado}"

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
