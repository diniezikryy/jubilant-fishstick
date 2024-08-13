from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import Quiz

class QuizAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

    def test_create_quiz(self):
        data = {"title": "Test Quiz", "description": "A test quiz"}
        response = self.client.post('/api/quizzes/', data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Quiz.objects.count(), 1)
        self.assertEqual(Quiz.objects.get().title, 'Test Quiz')

    def test_delete_quiz(self):
        # Create a quiz to delete
        quiz = Quiz.objects.create(title="Quiz to Delete", description="This quiz will be deleted",
                                   created_by=self.user)

        # Verify the quiz exists
        self.assertEqual(Quiz.objects.count(), 1)

        # Send DELETE request
        response = self.client.delete(f'/api/quizzes/{quiz.id}/')

        # Check response status code
        self.assertEqual(response.status_code, 204)

        # Verify the quiz has been deleted
        self.assertEqual(Quiz.objects.count(), 0)