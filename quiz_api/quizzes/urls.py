from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizViewSet, QuestionViewSet, AnswerViewSet

router = DefaultRouter()
router.register(r'', QuizViewSet)
router.register(r'(?P<quiz_pk>\d+)/questions', QuestionViewSet, basename='quiz-questions')
router.register(r'answers', AnswerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]