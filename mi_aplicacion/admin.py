# mi_aplicacion/admin.py
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin  # <-- Importar el original
from .models import Company, UserCompany

class UserCompanyInline(admin.TabularInline):
    model = UserCompany
    extra = 1
    verbose_name = "Empresa asignada"
    verbose_name_plural = "Empresas asignadas"

# 1. Crear subclase personalizada de UserAdmin
class UserAdmin(BaseUserAdmin):  # <-- Heredar de BaseUserAdmin
    inlines = [UserCompanyInline]
    
    # Mantener funcionalidades originales
    list_display = BaseUserAdmin.list_display + ('get_companies',)
    
    def get_companies(self, obj):
        return ", ".join([uc.company.name for uc in obj.usercompany_set.all()])
    get_companies.short_description = 'Empresas asignadas'

# 2. Desregistrar el User original y registrar nuestra versión
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# 3. Registrar Company normalmente
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'domain')
    search_fields = ('code', 'name')
    list_filter = ('domain',)