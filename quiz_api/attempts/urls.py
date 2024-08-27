from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizAttemptViewSet, QuizAttemptsOverviewView, TestView

router = DefaultRouter()
router.register(r'', QuizAttemptViewSet, basename='quiz-attempts')

urlpatterns = [
    path('overview/', QuizAttemptsOverviewView.as_view(), name='quiz-attempts-overview'),
    path('test/', TestView.as_view(), name='test-view'),
    path('', include(router.urls)),
]