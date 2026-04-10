from django.contrib import admin
from .models import User, Department, Demand, ServiceOrder

admin.site.register(User)
admin.site.register(Department)
admin.site.register(Demand)
admin.site.register(ServiceOrder)
