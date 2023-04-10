from django.db import models
from django.utils import timezone

class Plan(models.Model):
    plan = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'planes'

class Empresa(models.Model):
    nombre = models.CharField(max_length=255)
    token = models.CharField(max_length=255)
    endpoint_token = models.CharField(max_length=255)
    contador = models.IntegerField(default=0)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'empresas'

class Transacciones_Prueba(models.Model):
    ip_address = models.CharField(max_length=255)
    email_address = models.EmailField()
    billing_state = models.CharField(max_length=255)
    user_agent = models.CharField(max_length=255)
    billing_postal = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    EVENT_TIMESTAMP =  models.CharField(max_length=255)
    billing_address = models.CharField(max_length=255)
    EVENT_LABEL = models.CharField(max_length=255)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    archivo = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'transacciones_prueba'

    