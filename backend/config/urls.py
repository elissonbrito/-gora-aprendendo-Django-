from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from coreapp.views import HealthView, LoginView, MeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', HealthView.as_view()),
    path('api/auth/login/', LoginView.as_view()),
    path('api/auth/refresh/', TokenRefreshView.as_view()),
    path('api/auth/me/', MeView.as_view()),
    path('api/', include('coreapp.urls')),
]
