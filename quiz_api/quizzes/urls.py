from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizViewSet, QuestionViewSet, AnswerViewSet

router = DefaultRouter()
router.register(r'', QuizViewSet, basename='quiz')

quiz_router = DefaultRouter()
quiz_router.register(r'questions', QuestionViewSet, basename='quiz-questions')

question_router = DefaultRouter()
question_router.register(r'answers', AnswerViewSet, basename='question-answers')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:quiz_pk>/', include(quiz_router.urls)),
    path('<int:quiz_pk>/questions/<int:question_pk>/', include(question_router.urls)),
]