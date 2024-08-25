from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from .models import Quiz, Question, Answer
from .serializers import QuizSerializer, QuestionSerializer, AnswerSerializer


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def get_queryset(self):
        return Quiz.objects.prefetch_related('questions', 'questions__answers')


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Retrieve all questions for a specified quiz.

        Returns:
            QuerySet: A queryset of Question objects for the specified quiz.
        """
        quiz_id = self.kwargs['quiz_pk']
        return Question.objects.filter(quiz_id=quiz_id)

    def create(self, request, *args, **kwargs):
        """
        Create a new question for a specific quiz.

        This method overrides the default create behavior to ensure that
        the quiz context is passed to the serializer. It handles the creation
        of a new question along with its associated answers in a single request.

        Args:
            request (Request): The HTTP request object containing the question data.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments. Expected to contain 'quiz_pk'.

        Returns:
            Response: A DRF Response object with the serialized question data,
                      HTTP 201 Created status, and appropriate headers.

        Raises:
            ValidationError: If the provided data is invalid.
            Http404: If the specified quiz does not exist.
        """
        serializer = self.get_serializer(data=request.data, context={'view': self, 'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        """
        Create a new question for a specific quiz.

        This method associates the newly created question with the quiz
        specified in the URL.

        Args:
            serializer (QuestionSerializer): The serializer instance containing
                                             the validated data for the new question.

        Raises:
            Http404: If the specified quiz does not exist.
        """
        quiz_id = self.kwargs['quiz_pk']
        quiz = get_object_or_404(Quiz, id=quiz_id)
        serializer.save(quiz=quiz)

    def update(self, request, *args, **kwargs):
        """
        Updates a specific question from the database.

        This method updates the question instance from the database and returns
        the modified question data. It overrides the default update method to ensure
        proper handling of the updating process.

        Args:
            request (Request): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: An HTTP response with the question data indicating
                      successful update of the question.

        Raises:
            Http404: If the question with the specified ID does not exist.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a specific question from the database.

        This method removes the question instance from the database and returns
        a success status code. It overrides the default destroy method to ensure
        proper handling of the deletion process.

        Args:
            request (Request): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: An HTTP response with status code 204 (No Content) indicating
                      successful deletion.

        Raises:
            Http404: If the question with the specified ID does not exist.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AnswerViewSet(viewsets.ModelViewSet):
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Retrieve all answers for a specified question within a specified quiz.
        """
        quiz_id = self.kwargs['quiz_pk']
        question_id = self.kwargs['question_pk']
        return Answer.objects.filter(question__id=question_id, question__quiz__id=quiz_id)

    def perform_create(self, serializer):
        """
        Create a new answer for a specific question.
        """
        quiz_id = self.kwargs['quiz_pk']
        question_id = self.kwargs['question_pk']
        question = get_object_or_404(Question, id=question_id, quiz__id=quiz_id)
        serializer.save(question=question)
