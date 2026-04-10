from rest_framework import serializers
from .models import User, Department, Demand, ServiceOrder

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'cpf', 'phone', 'role', 'department', 'department_name', 'is_active', 'created_at', 'updated_at']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            raise serializers.ValidationError({'password': 'Senha é obrigatória.'})
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class DemandSerializer(serializers.ModelSerializer):
    citizen_name = serializers.CharField(source='citizen.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Demand
        fields = '__all__'
        read_only_fields = ['protocol', 'created_at', 'updated_at']

class ServiceOrderSerializer(serializers.ModelSerializer):
    collaborator_name = serializers.CharField(source='collaborator.name', read_only=True)
    demand_protocol = serializers.CharField(source='demand.protocol', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = ServiceOrder
        fields = '__all__'
