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