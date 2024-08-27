from django.db.models import Count, Max, Q
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import QuizAttempt, UserAnswer
from .serializers import QuizAttemptSerializer, UserAnswerSerializer, QuizAttemptsOverviewSerializer
from quizzes.models import Quiz, Question


class QuizAttemptViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing quiz attempts.

    This ViewSet provides CRUD operations for QuizAttempt objects and includes
    a custom action for submitting a completed quiz attempt.
    """

    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Get the list of quiz attempts for the current user.

        Returns:
            QuerySet: QuizAttempt objects filtered by the current user.
        """
        return QuizAttempt.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Create a new quiz attempt for the current user.

        Args:
            serializer: The serializer instance containing the validated data.
        """
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Submit a completed quiz attempt.

        This action processes the user's answers, calculates the score,
        and marks the attempt as completed.

        Args:
            request: The HTTP request object.
            pk: The primary key of the QuizAttempt object.

        Returns:
            Response: The serialized QuizAttempt data or an error message.
        """
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
        """
        Calculate the score for a completed quiz attempt.

        This method calculates the percentage of correct answers for MCQ questions.
        It does not currently score short answer questions.

        Args:
            attempt: The QuizAttempt object to calculate the score for.

        Returns:
            float: The calculated score as a percentage.
        """
        correct_answers = 0
        total_questions = attempt.quiz.questions.count()

        for user_answer in attempt.user_answers.all():
            if user_answer.question.question_type == 'mcq':
                if user_answer.selected_answer and user_answer.selected_answer.is_correct:
                    correct_answers += 1
            # For short answer questions, might want to implement a more sophisticated scoring system

        return (correct_answers / total_questions) * 100 if total_questions > 0 else 0


class QuizAttemptsOverviewView(APIView):
    """
    API View for retrieving an overview of quiz attempts

    This view provides aggregated data about quiz attempts, including the number of
    attempts and the highest score for each quiz.

    id refers to the PK for the quiz objects
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Get the overview of quiz attempts for the authenticated user.
        """

        quiz_data = Quiz.objects.annotate(
            attempt_count=Count('quizattempt', filter=Q(quizattempt__user=request.user)),
            highest_score=Max('quizattempt__score', filter=Q(quizattempt__user=request.user))
        ).values('id', 'title', 'attempt_count', 'highest_score')

        serializer = QuizAttemptsOverviewSerializer(quiz_data, many=True)
        return Response(serializer.data)

class TestView(APIView):
    def get(self, request):
        return Response({'message': "Test view is working"})
