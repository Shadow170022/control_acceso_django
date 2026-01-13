import pymysql
import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables del archivo .env

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = int(os.getenv("DB_PORT", 3306))

# db_utils.py
def get_connection(host, user, password, database):
    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=int(os.getenv('DB_PORT', 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )

def get_company_connection(company_name):
    valid_companies = [
        "mxcxit_htcerp",
        "mxcxit_mexxonerp",
        "mxcxit_rsserp",
        "mxcxit_ripmerp",
        "mxcxit_spqerp"
    ]
    
    if company_name not in valid_companies:
        raise ValueError(f"Empresa no válida para dominio mxcxit: {company_name}")

    return get_connection(
        host=os.getenv('DB_HOST'),
        user=os.getenv('MXCXIT_DB_USER'),
        password=os.getenv('MXCXIT_DB_PASSWORD'),
        database=company_name
    )

def get_company2_connection(company_name):
    valid_companies = [
        "mexcx_asiaop",
        "mexcx_daimayerp",
        "mexcx_hmserp",
        "mexcx_mlogerp",
        "mexcx_riaperp",
        "mexcx_tongtaierp"
    ]
    
    if company_name not in valid_companies:
        raise ValueError(f"Empresa no válida para dominio mexcx: {company_name}")

    return get_connection(
        host=os.getenv('DB_HOST'),
        user=os.getenv('MEXCX_DB_USER'),
        password=os.getenv('MEXCX_DB_PASSWORD'),
        database=company_name
    )

def get_company3_connection(company_name):
    """
    Establece una conexión dinámica con la base de datos de la empresa seleccionada.
    """
    # Lista de bases de datos permitidas
    valid_companies = [
        "mxcenit_sicerp",
        "mxcenit_tbgerp",
        "mxcenit_tbgerp2",
        "mxcenit_jinerp",
        "mxcenit_lererp",
        "mxcenit_suzhouerp",
        "mxcenit_tsperp"
    ]
    
    if company_name not in valid_companies:
        company_name = "mxcenit_sicerp"  # Valor por defecto

    conn = pymysql.connect(
        host="mexcentrix.com",         # Servidor de base de datos
        user="mxcenit_sistemas",        # Usuario
        password="DDGd6YI9it9AQf",      # Contraseña
        database=company_name,         # valor seleccionado
        port=3306,
        cursorclass=pymysql.cursors.DictCursor  # Retorna resultados como diccionario
    )
    return conn

def get_domain_companies():
    """Estructura de dominios y empresas"""
    return {
        "mxcxit": {
            "connection_func": get_company_connection,
            "companies": {
                "mxcxit_htcerp": "HTC",
                "mxcxit_mexxonerp": "MEXXON",
                "mxcxit_rsserp": "RSS",
                "mxcxit_ripmerp": "RIPM",
                "mxcxit_spqerp": "SPQ"
            }
        },
        "mexcx": {
            "connection_func": get_company2_connection,
            "companies": {
                "mexcx_asiaop": "ASIA OP",
                "mexcx_daimayerp": "DAIMAY",
                "mexcx_hmserp": "HMS",
                "mexcx_mlogerp": "MLOG",
                "mexcx_riaperp": "RIAP",
                "mexcx_tongtaierp": "TONGTAI"
            }
        },
        "mxcenit": {
            "connection_func": get_company3_connection,
            "companies": {
                "mxcenit_sicerp": "SIC",
                "mxcenit_tbgerp": "TBG QRO",
                "mxcenit_tbgerp2": "TBG MEX",
                "mxcenit_jinerp": "JIN",
                "mxcenit_lererp": "LER",
                "mxcenit_suzhouerp": "SUZHOU",
                "mxcenit_tsperp": "TSP"
            }
        }
    }
    


