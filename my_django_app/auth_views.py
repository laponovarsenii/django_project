from rest_framework import status, permissions
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings




from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from my_django_app.serealizers.auth_serializer import RegistrationSerializer


class RegisterView(CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]



class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

    def finalize_response(self, request, response, *args, **kwargs):

        response = super().finalize_response(request, response, *args, **kwargs)
        return response

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)

        access = resp.data.get('access')
        refresh = resp.data.get('refresh')


        if refresh:
            # cookie settings
            cookie_name = 'refresh_token'

            resp.set_cookie(
                cookie_name,
                refresh,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=7 * 24 * 60 * 60,
            )

        return resp



class RefreshTokenViewCustom(TokenRefreshView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):

        if 'refresh' not in request.data and 'refresh_token' in request.COOKIES:
            request._full_data = request.data.copy()
            request._full_data['refresh'] = request.COOKIES.get('refresh_token')

            request.data = request._full_data
        resp = super().post(request, *args, **kwargs)

        new_refresh = resp.data.get('refresh')
        if new_refresh:
            resp.set_cookie(
                'refresh_token',
                new_refresh,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=7 * 24 * 60 * 60,
            )
        return resp



class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        refresh_token = request.data.get('refresh') or request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'detail': 'Refresh token not provided.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)

            token.blacklist()
        except TokenError as e:
            return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)


        response = Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        response.delete_cookie('refresh_token')
        return response