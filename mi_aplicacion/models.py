from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    domain = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.code})"

class UserCompany(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'company')

class Empleado(models.Model):
    """
    Represents an employee's authentication and personal information.
    
    This model is primarily designed to retrieve and manage employee time records 
    from the Hikvision DS-K1A8503EF-B time clock system, through a SQL Server 
    database linked to the iVMS-4200 software.
    """
    
    id_empleado = models.CharField(max_length=255)  # Employee ID
    auth_datetime = models.DateTimeField()  # Full authentication timestamp
    auth_date = models.DateField()  # Date of authentication
    auth_time = models.TimeField()  # Time of authentication
    address = models.CharField(max_length=255)  # Location or address associated with the employee
    device_name = models.CharField(max_length=255)  # Name of the device used for authentication
    device_serial = models.CharField(max_length=255)  # Serial number of the device used
    user_name = models.CharField(max_length=255)  # Employee's username or full name
    card_no = models.CharField(max_length=255)  # Card number used for authentication (e.g., access card)

    def __str__(self):
        """
        Returns a string representation of the employee object.
        Used to display the employee's name and ID in a readable format.
        """
        return f"{self.user_name} - {self.id_empleado}"

class PermissionsTest(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        permissions = [
            ("is_finance", "Puede acceder al área de Finanzas"),
            ("is_developer", "Puede acceder al área de Desarrollo"),
            ("is_rh", "Puede acceder al área de Recursos Humanos"),
            
        ]