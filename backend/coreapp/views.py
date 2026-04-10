import json
from django.db.models import Count
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Department, Demand, ServiceOrder
from .serializers import UserSerializer, DepartmentSerializer, DemandSerializer, ServiceOrderSerializer
from .permissions import IsAdminRole, IsAdminOrCollaboratorRole
from .services import mongo_audit, cache_service
from .authentication import AgoraJWTAuthentication

class HealthView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def get(self, request):
        return Response({'status': 'ok'})

class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'detail': 'Email e senha são obrigatórios.'}, status=400)
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return Response({'detail': 'Credenciais inválidas.'}, status=401)
        if not user.check_password(password):
            return Response({'detail': 'Credenciais inválidas.'}, status=401)
        refresh = RefreshToken()
        refresh['user_id'] = user.id
        refresh['role'] = user.role
        refresh['email'] = user.email
        access = refresh.access_token
        access['user_id'] = user.id
        access['role'] = user.role
        access['email'] = user.email
        return Response({
            'access': str(access),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        })

class MeView(APIView):
    authentication_classes = [AgoraJWTAuthentication]
    def get(self, request):
        return Response(UserSerializer(request.user_obj).data)

class BaseViewSet(viewsets.ModelViewSet):
    authentication_classes = [AgoraJWTAuthentication]

class UserViewSet(BaseViewSet):
    queryset = User.objects.select_related('department').all().order_by('-id')
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create_public':
            return [AllowAny()]
        return [IsAdminRole()]

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class DepartmentViewSet(BaseViewSet):
    queryset = Department.objects.all().order_by('name')
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAdminOrCollaboratorRole()]
        return [IsAdminRole()]

class DemandViewSet(BaseViewSet):
    queryset = Demand.objects.select_related('citizen', 'department').all().order_by('-id')
    serializer_class = DemandSerializer

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve', 'update', 'partial_update']:
            return [IsAdminOrCollaboratorRole() if self.action != 'create' else AllowAny()]
        return [IsAdminRole()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = getattr(self.request, 'user_obj', None)
        if not user:
            return qs.none()
        if user.role == 'USER':
            return qs.filter(citizen=user)
        if user.role == 'COLLABORATOR':
            return qs.filter(department=user.department)
        return qs

    def perform_create(self, serializer):
        user = getattr(self.request, 'user_obj', None)
        citizen = user
        if not citizen:
            citizen_id = self.request.data.get('citizen')
            citizen = User.objects.get(id=citizen_id)
        last_id = Demand.objects.count() + 1
        protocol = f"AG-{last_id:06d}"
        demand = serializer.save(protocol=protocol, citizen=citizen)
        mongo_audit.log('audit_logs', {'entityType': 'demand', 'entityId': demand.id, 'action': 'CREATED', 'performedBy': citizen.email})
        cache_service.delete('dashboard_admin')

    def perform_update(self, serializer):
        demand = serializer.save()
        mongo_audit.log('audit_logs', {'entityType': 'demand', 'entityId': demand.id, 'action': 'UPDATED', 'performedBy': self.request.user_obj.email})
        cache_service.delete('dashboard_admin')

class ServiceOrderViewSet(BaseViewSet):
    queryset = ServiceOrder.objects.select_related('demand', 'collaborator', 'department').all().order_by('-id')
    serializer_class = ServiceOrderSerializer

    def get_permissions(self):
        return [IsAdminOrCollaboratorRole()]

    def perform_create(self, serializer):
        service_order = serializer.save()
        mongo_audit.log('audit_logs', {'entityType': 'service_order', 'entityId': service_order.id, 'action': 'CREATED', 'performedBy': self.request.user_obj.email})
        cache_service.delete('dashboard_admin')

    def perform_update(self, serializer):
        service_order = serializer.save()
        mongo_audit.log('audit_logs', {'entityType': 'service_order', 'entityId': service_order.id, 'action': 'UPDATED', 'performedBy': self.request.user_obj.email})
        cache_service.delete('dashboard_admin')

class RegisterPublicView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        serializer = UserSerializer(data={**request.data, 'role': 'USER'})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class DashboardAdminView(APIView):
    authentication_classes = [AgoraJWTAuthentication]
    permission_classes = [IsAdminRole]

    def get(self, request):
        cache_key = 'dashboard_admin'
        cached = cache_service.get(cache_key)
        if cached:
            return Response(json.loads(cached))
        data = {
            'total_users': User.objects.count(),
            'total_departments': Department.objects.count(),
            'total_demands': Demand.objects.count(),
            'open_demands': Demand.objects.exclude(status='CONCLUIDA').count(),
            'closed_demands': Demand.objects.filter(status='CONCLUIDA').count(),
            'total_service_orders': ServiceOrder.objects.count(),
            'demands_by_status': list(Demand.objects.values('status').annotate(total=Count('id')).order_by('status')),
        }
        cache_service.set(cache_key, json.dumps(data), ex=120)
        return Response(data)
