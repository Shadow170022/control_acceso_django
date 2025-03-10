from django.contrib import admin
from .models import MexcentrixAccess

class MexcentrixAccessAdmin(admin.ModelAdmin):
    pass

admin.site.register(MexcentrixAccess, MexcentrixAccessAdmin)