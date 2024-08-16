from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from quizzes.models import Quiz, Question, Answer

class QuizModelTest(TestCase):
    """Test case for the Quiz model"""

    def test_quiz_creation(self):
        """Test creating a new quiz"""
        user = User.objects.create_user(username='testuser', password='12345')
        quiz = Quiz.objects.create(title='Test Quiz', creator=user)
        self.assertEqual(quiz.title, 'Test Quiz')
        self.assertEqual(quiz.creator, user)

class QuestionAPITest(APITestCase):
    """Test case for the Question API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)
        self.quiz = Quiz.objects.create(title='Test Quiz', creator=self.user)
        self.base_url = f'/api/quizzes/{self.quiz.id}/questions/'

    def test_create_question(self):
        """Test creating a new question with answers"""
        data = {
            'text': 'Test question?',
            'question_type': 'mcq',
            'answers': [
                {'text': 'Correct answer', 'is_correct': True},
                {'text': 'Wrong answer', 'is_correct': False}
            ]
        }
        response = self.client.post(self.base_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Question.objects.count(), 1)

    def test_list_questions(self):
        """Test listing all questions for a quiz"""
        Question.objects.create(quiz=self.quiz, text='Test question?', question_type='mcq')
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_question(self):
        """Test retrieving a specific question"""
        question = Question.objects.create(quiz=self.quiz, text='Test question?', question_type='mcq')
        url = f'{self.base_url}{question.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['text'], 'Test question?')

    def test_update_question(self):
        """Test updating a question"""
        question = Question.objects.create(quiz=self.quiz, text='Test question?', question_type='mcq')
        url = f'{self.base_url}{question.id}/'
        data = {'text': 'Updated question?', 'question_type': 'mcq'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Question.objects.get(pk=question.pk).text, 'Updated question?')

    def test_delete_question(self):
        """Test deleting a question"""
        question = Question.objects.create(quiz=self.quiz, text='Test question?', question_type='mcq')
        url = f'{self.base_url}{question.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Question.objects.count(), 0)

class QuestionAnswerAPITest(APITestCase):
    """Test case for Question-Answer interactions in the API"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)
        self.quiz = Quiz.objects.create(title='Test Quiz', creator=self.user)
        self.base_url = f'/api/quizzes/{self.quiz.id}/questions/'

    def test_create_question_with_answers(self):
        """Test creating a question with multiple answers"""
        data = {
            'text': 'Test question?',
            'question_type': 'mcq',
            'answers': [
                {'text': 'Correct answer', 'is_correct': True},
                {'text': 'Wrong answer', 'is_correct': False}
            ]
        }
        response = self.client.post(self.base_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(Answer.objects.count(), 2)

        question = Question.objects.first()
        answers = Answer.objects.filter(question=question)
        self.assertEqual(answers.count(), 2)
        self.assertTrue(answers.filter(text='Correct answer', is_correct=True).exists())
        self.assertTrue(answers.filter(text='Wrong answer', is_correct=False).exists())

    def test_update_question_with_answers(self):
        """Test updating a question and its answers"""
        question = Question.objects.create(quiz=self.quiz, text='Original question?', question_type='mcq')
        Answer.objects.create(question=question, text='Original answer 1', is_correct=True)
        Answer.objects.create(question=question, text='Original answer 2', is_correct=False)

        url = f'{self.base_url}{question.id}/'
        data = {
            'text': 'Updated question?',
            'question_type': 'mcq',
            'answers': [
                {'text': 'New correct answer', 'is_correct': True},
                {'text': 'New wrong answer', 'is_correct': False}
            ]
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        question.refresh_from_db()
        self.assertEqual(question.text, 'Updated question?')
        answers = Answer.objects.filter(question=question)
        self.assertEqual(answers.count(), 2)
        self.assertTrue(answers.filter(text='New correct answer', is_correct=True).exists())
        self.assertTrue(answers.filter(text='New wrong answer', is_correct=False).exists())
        self.assertFalse(answers.filter(text='Original answer 1').exists())
        self.assertFalse(answers.filter(text='Original answer 2').exists())

    def test_retrieve_question_with_answers(self):
        """Test retrieving a question with its answers"""
        question = Question.objects.create(quiz=self.quiz, text='Test question?', question_type='mcq')
        Answer.objects.create(question=question, text='Correct answer', is_correct=True)
        Answer.objects.create(question=question, text='Wrong answer', is_correct=False)

        url = f'{self.base_url}{question.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['text'], 'Test question?')
        self.assertEqual(len(response.data['answers']), 2)
        self.assertTrue(any(answer['text'] == 'Correct answer' and answer['is_correct'] for answer in response.data['answers']))
        self.assertTrue(any(answer['text'] == 'Wrong answer' and not answer['is_correct'] for answer in response.data['answers']))

    def test_delete_question_cascades_to_answers(self):
        """Test that deleting a question also deletes its associated answers"""
        question = Question.objects.create(quiz=self.quiz, text='Test question?', question_type='mcq')
        Answer.objects.create(question=question, text='Answer 1', is_correct=True)
        Answer.objects.create(question=question, text='Answer 2', is_correct=False)

        url = f'{self.base_url}{question.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Question.objects.count(), 0)
        self.assertEqual(Answer.objects.count(), 0)