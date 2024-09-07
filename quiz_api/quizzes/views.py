from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Quiz, Question, Answer
from .serializers import QuizSerializer, QuestionSerializer, AnswerSerializer

# for the pdf upload and quiz generation
from rest_framework.decorators import action
from .models import TempPDF, TempQuestion
from .serializers import TempQuestionSerializer
from .pdf_processor import process_pdf_and_generate_questions


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def get_queryset(self):
        return Quiz.objects.prefetch_related('questions', 'questions__answers')

    # for the pdf upload and quiz generation
    @action(detail=True, methods=['post'])
    def upload_pdf(self, request, pk=None):
        quiz = self.get_object()

        try:
            pdf_file = request.FILES['pdf']
        except KeyError:
            return Response({'error': 'No PDF file provided'}, status=status.HTTP_400_BAD_REQUEST)

        if not pdf_file:
            return Response({'error': 'Empty PDF file provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            temp_pdf = TempPDF.objects.create(
                user=request.user,
                file=pdf_file,
                quiz=quiz
            )

            # process pdf and generate the questions
            num_questions = process_pdf_and_generate_questions(temp_pdf.file.path, quiz)

            # fetch the generated temp questions
            temp_questions = TempQuestion.objects.filter(quiz=quiz)
            serializer = TempQuestionSerializer(temp_questions, many=True)

            return Response({
                'message': f'{num_questions} questions generated',
                'questions': serializer.data
            }, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # if an error occurs, delete the temp pdf and return an error response
            if 'temp_pdf' in locals():
                temp_pdf.delete()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def add_selected_questions(self, request, pk=None):
        quiz = self.get_object()
        question_ids = request.data.get('question_ids', [])

        if not question_ids:
            return Response({'error': 'No question ids provided'}, status=status.HTTP_400_BAD_REQUEST)

        selected_questions = TempQuestion.objects.filter(id__in=question_ids, quiz=quiz)
        permanent_questions = []

        for temp_question in selected_questions:
            question = Question.objects.create(
                quiz=quiz,
                text=temp_question.text,
                question_type=temp_question.question_type
            )
            for temp_answer in temp_question.temp_answers.all():
                Answer.objects.create(
                    question=question,
                    text=temp_answer.text,
                    is_correct=temp_answer.is_correct
                )
            permanent_questions.append(question)

            # Delete all temporary questions for this quiz
        TempQuestion.objects.filter(quiz=quiz).delete()

        return Response({'success': f'{len(permanent_questions)} questions added to the quiz'})

    @action(detail=True, methods=['get'])
    def temp_questions(self, request, pk=None):
        quiz = self.get_object()
        temp_questions = TempQuestion.objects.filter(quiz=quiz)
        serializer = TempQuestionSerializer(temp_questions, many=True)
        return Response(serializer.data)


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
