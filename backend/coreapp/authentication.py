from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions
from .models import User

class AgoraJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None
        token_user, validated_token = result
        user_id = validated_token.get('user_id')
        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Usuário inválido.')
        request.user_obj = user
        return (user, validated_token)
