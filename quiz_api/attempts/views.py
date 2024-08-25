from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import QuizAttempt, UserAnswer
from .serializers import QuizAttemptSerializer, UserAnswerSerializer
from quizzes.models import Quiz, Question


class QuizAttemptViewSet(viewsets.ModelViewSet):
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        attempt = self.get_object()
        if attempt.end_time:
            return Response({"detail": "This attempt has already been submitted."}, status=status.HTTP_400_BAD_REQUEST)

        answers_data = request.data.get('answers', [])
        for answer_data in answers_data:
            question_id = answer_data.get('question')
            selected_answer_id = answer_data.get('selected_answer')
            text_answer = answer_data.get('text_answer')

            question = Question.objects.get(id=question_id)
            UserAnswer.objects.update_or_create(
                quiz_attempt=attempt,
                question=question,
                defaults={
                    'selected_answer_id': selected_answer_id,
                    'text_answer': text_answer
                }
            )

        attempt.end_time = timezone.now()
        attempt.score = self.calculate_score(attempt)
        attempt.save()

        serializer = self.get_serializer(attempt)
        return Response(serializer.data)

    def calculate_score(self, attempt):
        correct_answers = 0
        total_questions = attempt.quiz.questions.count()

        for user_answer in attempt.user_answers.all():
            if user_answer.question.question_type == 'mcq':
                if user_answer.selected_answer and user_answer.selected_answer.is_correct:
                    correct_answers += 1
            # For short answer questions, might want to implement a more sophisticated scoring system

        return (correct_answers / total_questions) * 100 if total_questions > 0 else 0
