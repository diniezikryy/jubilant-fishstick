from django.urls import path
from .views import CookieTokenObtainPairView, CookieTokenRefreshView, RegisterView, LogoutView, auth_check

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('auth-check/', auth_check, name='auth_check'),
]
