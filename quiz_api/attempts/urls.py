from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizAttemptViewSet

router = DefaultRouter()
router.register(r'', QuizAttemptViewSet, basename='quiz-attempts')

urlpatterns = [
    path('', include(router.urls)),
]