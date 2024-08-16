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
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
