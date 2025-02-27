from django.urls import path
from . import views

# urls.py
urlpatterns = [
    path('reportes/', views.reportes, name='reportes'),
    path('api/dominios/', views.api_dominios, name='api_dominios'),
    path('api/empresas/', views.api_empresas, name='api_empresas'),
    path('api/periodos/', views.api_periodos, name='api_periodos'),
    path('descargar_excel/', views.descargar_excel, name='descargar_excel'),
]