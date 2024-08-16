from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizViewSet, QuestionViewSet, AnswerViewSet

router = DefaultRouter()

router.register(r'', QuizViewSet, basename='quiz')

quiz_router = DefaultRouter()
quiz_router.register(r'questions', QuestionViewSet, basename='quiz-questions')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:quiz_pk>/', include(quiz_router.urls)),
]