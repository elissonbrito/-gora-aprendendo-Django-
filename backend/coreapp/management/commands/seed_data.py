from django.core.management.base import BaseCommand
from coreapp.models import Department, User

class Command(BaseCommand):
    help = 'Cria dados iniciais do projeto.'

    def handle(self, *args, **kwargs):
        dep, _ = Department.objects.get_or_create(name='Tecnologia', defaults={'description': 'Departamento de Tecnologia'})
        admin, created = User.objects.get_or_create(email='admin@agora.local', defaults={
            'name': 'Administrador',
            'role': 'ADMIN',
            'department': dep,
            'is_active': True,
        })
        if created or not admin.password_hash:
            admin.set_password('123456')
            admin.role = 'ADMIN'
            admin.department = dep
            admin.is_active = True
            admin.save()
        self.stdout.write(self.style.SUCCESS('Seed concluído.'))
