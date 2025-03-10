from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('reportes/', login_required(views.reportes), name='reportes'),
    path('api/dominios/', login_required(views.api_dominios), name='api_dominios'),
    path('api/empresas/', login_required(views.api_empresas), name='api_empresas'),
    path('api/periodos/', login_required(views.api_periodos), name='api_periodos'),
    path('descargar_excel/', login_required(views.descargar_excel), name='descargar_excel'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]