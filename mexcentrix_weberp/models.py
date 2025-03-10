# mexcentrix_weberp/models.py
from django.db import models

class MexcentrixAccess(models.Model):
    # Campo temporal para crear la estructura de tabla
    dummy_field = models.BooleanField(default=True)

    class Meta:
        permissions = [
            ("access_mexcentrix", "Puede acceder a la app Mexcentrix"),
        ]