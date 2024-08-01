from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Quiz, Question
from .serializers import QuizSerializer, QuizDetailSerializer, QuestionSerializer, AnswerSerializer


class QuizViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    # This method customizes the queryset to only include quizzes created by the current user
    def get_queryset(self):
        return Quiz.objects.filter(creator=self.request.user)

    # This method determines which serializer to use based on the action
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', 'retrieve']:
            return QuizDetailSerializer
        return QuizSerializer

    # This method customizes the creation process to set the creator to the current user
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    # Custom action to add a question to a specific quiz
    @action(detail=True, methods=['post'])
    def add_question(self, request, pk=None):
        quiz = self.get_object()
        question_data = request.data
        # Extract answers_data, default to empty list if not present
        answers_data = question_data.pop('answers', [])

        # Create the question
        question_serializer = QuestionSerializer(data=question_data)
        if question_serializer.is_valid():
            question = question_serializer.save(quiz=quiz)

            # Create answers for the question
            for answer_data in answers_data:
                answer_serializer = AnswerSerializer(data=answer_data)
                if answer_serializer.is_valid():
                    answer_serializer.save(question=question)
                else:
                    # If any answer is invalid, delete the question and return error
                    question.delete()
                    return Response(answer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Return the created question data
            return Response(QuestionSerializer(question).data, status=status.HTTP_201_CREATED)

        # If question data is invalid, return error response
        return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Custom action to retrieve all quizzes created by the current user
    @action(detail=False, methods=['get'])
    def my_quizzes(self, request):
        quizzes = self.get_queryset()
        serializer = self.get_serializer(quizzes, many=True)
        return Response({
            "user": request.user.username,
            "quizzes": serializer.data
        })

    @action(detail=True, methods=['get'])
    def get_questions(self, request, pk=None):
        # Get all questions for a specific quiz
        quiz = self.get_object()
        questions = quiz.questions.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def get_question(self, request, pk=None):
        # Get a specific question from a quiz
        quiz = self.get_object()
        question_id = request.query_params.get('question_id')

        if not question_id:
            return Response({"error": "Question ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            question = Question.objects.get(id=question_id, quiz=quiz)
            serializer = QuestionSerializer(question)
            return Response(serializer.data)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['delete'])
    def delete_question(self, request, pk=None):
        # Delete a specific question from a quiz
        quiz = self.get_object()
        question_id = request.data.get('question_id')

        if not question_id:
            return Response({"error": "Question ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            question = Question.objects.get(id=question_id, quiz=quiz)
            question.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
