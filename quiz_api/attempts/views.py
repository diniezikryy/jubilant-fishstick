import logging
from django.db.models import Count, Max, Q, Case, When, IntegerField, F
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import QuizAttempt, UserAnswer
from .serializers import QuizAttemptSerializer, UserAnswerSerializer, QuizAttemptsOverviewSerializer
from quizzes.models import Quiz, Question

logger = logging.getLogger(__name__)


class QuizAttemptViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing quiz attempts.

    This ViewSet provides CRUD operations for QuizAttempt objects and includes
    a custom action for submitting a completed quiz attempt.
    """

    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list_by_quiz(self, request, quiz_id=None):
        """
        Custom action to retrieve quiz attempts filtered by quiz ID.
        """
        queryset = self.get_queryset().filter(quiz_id=quiz_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        """
        Filter quiz attempts by quiz ID and annotate with correct and incorrect answer counts.
        """
        quiz_id = self.request.query_params.get('quiz_id')
        queryset = QuizAttempt.objects.filter(user=self.request.user)

        if quiz_id:
            queryset = queryset.filter(quiz_id=quiz_id)

        queryset = queryset.annotate(
            total_questions=Count('user_answers'),
            correct_answers=Count(
                Case(
                    When(user_answers__selected_answer__is_correct=True, then=1),
                    output_field=IntegerField()
                )
            ),
            incorrect_answers=F('total_questions') - F('correct_answers')
        )

        return queryset

    def perform_create(self, serializer):
        """
        Create a new quiz attempt for the current user.

        Args:
            serializer: The serializer instance containing the validated data.
        """
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        attempt = self.get_object()
        if attempt.end_time:
            return Response({"detail": "This attempt has already been submitted."}, status=status.HTTP_400_BAD_REQUEST)

        answers_data = request.data.get('answers', [])
        logger.info(f"Submitting answers for attempt {attempt.id}: {answers_data}")

        for answer_data in answers_data:
            question_id = answer_data.get('question')
            selected_answer_id = answer_data.get('selected_answer')
            text_answer = answer_data.get('text_answer')

            question = Question.objects.get(id=question_id)
            user_answer, created = UserAnswer.objects.update_or_create(
                quiz_attempt=attempt,
                question=question,
                defaults={
                    'selected_answer_id': selected_answer_id,
                    'text_answer': text_answer
                }
            )
            logger.info(
                f"User answer for question {question_id}: selected_answer={selected_answer_id}, text_answer={text_answer}")

        attempt.end_time = timezone.now()
        score_data = self.calculate_score(attempt)
        attempt.score = score_data['score']
        attempt.save()

        logger.info(f"Attempt {attempt.id} submitted. Final score: {attempt.score}")

        response_data = self.get_serializer(attempt).data
        response_data.update(score_data)
        return Response(response_data)

    def calculate_score(self, attempt):
        correct_answers = 0
        total_questions = attempt.quiz.questions.count()
        incorrect_questions = []

        logger.info(f"Calculating score for attempt {attempt.id}")

        for user_answer in attempt.user_answers.all():
            if user_answer.question.question_type == 'mcq':
                if user_answer.selected_answer and user_answer.selected_answer.is_correct:
                    correct_answers += 1
                    logger.info(f"Question {user_answer.question.id}: Correct answer selected")
                else:
                    logger.info(f"Question {user_answer.question.id}: Incorrect answer selected")
                    incorrect_questions.append({
                        'question_id': user_answer.question.id,
                        'question_text': user_answer.question.text,
                        'selected_answer': user_answer.selected_answer.text if user_answer.selected_answer else None,
                        'correct_answer': user_answer.question.answers.filter(is_correct=True).first().text
                    })
            else:
                logger.info(f"Question {user_answer.question.id}: Short answer question (not scored)")

        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        logger.info(f"Final score calculation: {correct_answers}/{total_questions} = {score}%")

        return {
            'score': score,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'incorrect_questions': incorrect_questions
        }


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
