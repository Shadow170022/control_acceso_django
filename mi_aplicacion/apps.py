from django.apps import AppConfig

class MiAplicacionConfig(AppConfig):
    """    
    This class defines the default application settings, including the type 
    of primary key field used for models within the app. By default, it uses
    'BigAutoField' for auto-incrementing primary keys.
    """
    
    default_auto_field = 'django.db.models.BigAutoField'  # Sets BigAutoField as the default primary key type
    name = 'mi_aplicacion'  # Specifies the name of this app
