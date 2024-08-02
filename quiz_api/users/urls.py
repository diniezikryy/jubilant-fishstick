from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, CookieTokenObtainPairView, CookieTokenRefreshView

"""
This urls.py file uses individual URL patterns for each view.
This approach is useful when you have a small number of views
or when each view has a distinct purpose.
"""

urlpatterns = [
    # User registration endpoint
    path('register/', RegisterView.as_view(), name='register'),

    # JWT token generation endpoint
    path('token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),

    # JWT token refresh endpoint
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
]

# Note: This style of URL configuration provides explicit control over each endpoint,
# making it easy to see at a glance what functionality is available in the users' app.
