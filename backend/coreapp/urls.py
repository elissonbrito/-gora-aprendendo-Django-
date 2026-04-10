from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, DepartmentViewSet, DemandViewSet, ServiceOrderViewSet, RegisterPublicView, DashboardAdminView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'departments', DepartmentViewSet, basename='departments')
router.register(r'demands', DemandViewSet, basename='demands')
router.register(r'service-orders', ServiceOrderViewSet, basename='service-orders')

urlpatterns = [
    path('auth/register/', RegisterPublicView.as_view()),
    path('dashboard/admin/', DashboardAdminView.as_view()),
    path('', include(router.urls)),
]
