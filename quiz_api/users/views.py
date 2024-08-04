from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import status
from rest_framework.views import APIView

from .authentication import CustomJWTAuthentication
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings

import logging

logger = logging.getLogger(__name__)


class CookieTokenObtainPairView(TokenObtainPairView):
    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get('access'):
            access_max_age = 15 * 60  # 15 minutes
            refresh_max_age = 24 * 60 * 60  # 1 day
            response.set_cookie(
                'access_token',
                response.data['access'],
                max_age=access_max_age,
                httponly=True,
                samesite='Lax',
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE']
            )
            response.set_cookie(
                'refresh_token',
                response.data['refresh'],
                max_age=refresh_max_age,
                httponly=True,
                samesite='Lax',
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE']
            )
            del response.data['access']
            del response.data['refresh']
        return super().finalize_response(request, response, *args, **kwargs)


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
        logger.info(f"Attempting to refresh token. Refresh token present: {bool(refresh_token)}")

        if not refresh_token:
            logger.warning("Refresh token not found in cookies")
            return Response({"detail": "No refresh token provided"}, status=400)

        # Override the request data with the token from the cookie
        request.data['refresh'] = refresh_token

        try:
            return super().post(request, *args, **kwargs)
        except InvalidToken as e:
            logger.error(f"Invalid token error: {str(e)}")
            return Response({"detail": "Invalid refresh token"}, status=401)
        except TokenError as e:
            logger.error(f"Token error: {str(e)}")
            return Response({"detail": str(e)}, status=400)
        except Exception as e:
            logger.exception("Unexpected error during token refresh")
            return Response({"detail": "Unexpected error"}, status=500)

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get('access'):
            access_max_age = 15 * 60  # 15 minutes
            response.set_cookie(
                settings.SIMPLE_JWT['AUTH_COOKIE'],
                response.data['access'],
                max_age=access_max_age,
                httponly=True,
                samesite='Lax',
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE']
            )
            del response.data['access']
        return super().finalize_response(request, response, *args, **kwargs)


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            access_max_age = 15 * 60  # 15 minutes
            refresh_max_age = 24 * 60 * 60  # 1 day
            response.set_cookie(
                'access_token',
                str(refresh.access_token),
                max_age=access_max_age,
                httponly=True,
                samesite='Lax',
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE']
            )
            response.set_cookie(
                'refresh_token',
                str(refresh),
                max_age=refresh_max_age,
                httponly=True,
                samesite='Lax',
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE']
            )
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def auth_check(request):
    return Response({"authenticated": True})


class LogoutView(APIView):
    def post(self, request):
        response = Response({"detail": "Successfully logged out."})
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
