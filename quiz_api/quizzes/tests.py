from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import Quiz, Question


class QuizAPITestCase(TestCase):
    def setUp(self):
        # Create a test client and a test user
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

    def test_create_quiz(self):
        # Test creating a new quiz
        data = {"title": "Test Quiz", "num_questions": 5, "time_limit": 30}
        response = self.client.post('/api/quizzes/', data)
        self.assertEqual(response.status_code, 201)  # Check if creation was successful
        self.assertEqual(Quiz.objects.count(), 1)  # Check if a quiz was actually created
        self.assertEqual(Quiz.objects.get().title, 'Test Quiz')  # Check if the quiz title is correct

    def test_get_quizzes(self):
        # Test retrieving all quizzes
        Quiz.objects.create(title="Quiz 1", num_questions=5, creator=self.user)
        Quiz.objects.create(title="Quiz 2", num_questions=10, creator=self.user)
        response = self.client.get('/api/quizzes/')
        self.assertEqual(response.status_code, 200)  # Check if request was successful
        self.assertEqual(len(response.data), 2)  # Check if both quizzes are returned

    def test_get_single_quiz(self):
        # Test retrieving a single quiz
        quiz = Quiz.objects.create(title="Single Quiz", num_questions=5, creator=self.user)
        response = self.client.get(f'/api/quizzes/{quiz.id}/')
        self.assertEqual(response.status_code, 200)  # Check if request was successful
        self.assertEqual(response.data['title'], "Single Quiz")  # Check if the correct quiz is returned

    def test_delete_quiz(self):
        quiz = Quiz.objects.create(title="Quiz to Delete", num_questions=5, creator=self.user)
        self.assertEqual(Quiz.objects.count(), 1)
        response = self.client.delete(f'/api/quizzes/{quiz.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Quiz.objects.count(), 0)

    def test_add_question_to_quiz(self):
        # Create a quiz
        quiz = Quiz.objects.create(title="Quiz with Questions", num_questions=1, creator=self.user)

        # Prepare question data with answers
        question_data = {
            "quiz": quiz.id,
            "text": "What is 2+2?",
            "question_type": "MC",
            "difficulty": 1,
            "answers": [
                {"text": "3", "is_correct": False},
                {"text": "4", "is_correct": True},
                {"text": "5", "is_correct": False},
                {"text": "6", "is_correct": False}
            ]
        }

        # Send request to add question
        response = self.client.post(f'/api/quizzes/{quiz.id}/add_question/', question_data, format='json')

        # Print response content regardless of status code
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.content}")

        # Check if question was added successfully
        self.assertEqual(response.status_code, 201)

        # Check if the question is associated with the quiz
        self.assertEqual(quiz.questions.count(), 1)
        new_question = quiz.questions.first()
        if new_question:
            self.assertEqual(new_question.text, "What is 2+2?")

            # Check if all answers were added
            self.assertEqual(new_question.answers.count(), 4)

            # Check if the correct answer is properly set
            correct_answers = new_question.answers.filter(is_correct=True)
            self.assertEqual(correct_answers.count(), 1)
            if correct_answers.exists():
                self.assertEqual(correct_answers.first().text, "4")
        else:
            print("No question was created.")

    def test_get_questions(self):
        # Create a quiz with questions
        quiz = Quiz.objects.create(title="Test Quiz", num_questions=2, creator=self.user)
        question1 = Question.objects.create(quiz=quiz, text="Q1", question_type="MC", difficulty=1)
        question2 = Question.objects.create(quiz=quiz, text="Q2", question_type="TF", difficulty=2)

        # Get questions
        response = self.client.get(f'/api/quizzes/{quiz.id}/get_questions/')

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['text'], "Q1")
        self.assertEqual(response.data[1]['text'], "Q2")

    def test_get_specific_question(self):
        # Create a quiz with a question
        quiz = Quiz.objects.create(title="Test Quiz", num_questions=1, creator=self.user)
        question = Question.objects.create(quiz=quiz, text="Q1", question_type="MC", difficulty=1)

        # Get the specific question
        response = self.client.get(f'/api/quizzes/{quiz.id}/get_question/', {'question_id': question.id})

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['text'], "Q1")

    def test_delete_question(self):
        # Create a quiz with a question
        quiz = Quiz.objects.create(title="Test Quiz", num_questions=1, creator=self.user)
        question = Question.objects.create(quiz=quiz, text="Q1", question_type="MC", difficulty=1)

        # Delete the question
        response = self.client.delete(f'/api/quizzes/{quiz.id}/delete_question/', {'question_id': question.id})

        # Check response
        self.assertEqual(response.status_code, 204)

        # Verify question is deleted
        self.assertEqual(Question.objects.filter(id=question.id).count(), 0)

    def test_delete_nonexistent_question(self):
        # Create a quiz without questions
        quiz = Quiz.objects.create(title="Test Quiz", num_questions=0, creator=self.user)

        # Try to delete a nonexistent question
        response = self.client.delete(f'/api/quizzes/{quiz.id}/delete_question/', {'question_id': 999})

        # Check response
        self.assertEqual(response.status_code, 404)
