from django.contrib.auth.hashers import make_password, check_password
from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Department(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class User(TimeStampedModel):
    ROLE_CHOICES = [
        ('USER', 'Usuário'),
        ('COLLABORATOR', 'Colaborador'),
        ('ADMIN', 'Administrador'),
    ]
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    cpf = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='USER')
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, related_name='users')
    is_active = models.BooleanField(default=True)

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)

    def __str__(self):
        return self.email

class Demand(TimeStampedModel):
    STATUS_CHOICES = [
        ('ABERTA', 'Aberta'),
        ('EM_ANALISE', 'Em análise'),
        ('ENCAMINHADA', 'Encaminhada'),
        ('EM_EXECUCAO', 'Em execução'),
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),
    ]
    PRIORITY_CHOICES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente'),
    ]
    protocol = models.CharField(max_length=30, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    citizen = models.ForeignKey(User, on_delete=models.CASCADE, related_name='demands')
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, related_name='demands')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='ABERTA')
    priority = models.CharField(max_length=30, choices=PRIORITY_CHOICES, default='MEDIA')
    address = models.CharField(max_length=255, blank=True, null=True)
    district = models.CharField(max_length=120, blank=True, null=True)
    latitude = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.protocol

class ServiceOrder(TimeStampedModel):
    STATUS_CHOICES = [
        ('ABERTA', 'Aberta'),
        ('EM_ANDAMENTO', 'Em andamento'),
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),
    ]
    demand = models.ForeignKey(Demand, on_delete=models.CASCADE, related_name='service_orders')
    collaborator = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='service_orders')
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, related_name='service_orders')
    description = models.TextField()
    execution_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='ABERTA')
    opened_at = models.DateTimeField(blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'OS #{self.id}'
