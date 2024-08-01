from django.db import models
from documents.models import PDF
from django.contrib.auth.models import User

# Create your models here.
class Quiz(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    num_questions = models.IntegerField()
    time_limit = models.IntegerField(help_text="Time limit in minutes", null=True, blank=True)
    pdf = models.ForeignKey(PDF, on_delete=models.SET_NULL, related_name='quizzes', null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_quizzes', default=1)

    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPES = (
        ('MC', 'Multiple Choice'),
        ('TF', 'True/False'),
        ('SA', 'Short Answer'),
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPES)
    difficulty = models.IntegerField(choices=[(1, 'Easy'), (2, 'Medium'), (3, 'Hard')])

    def __str__(self):
        return f"{self.quiz.title} - Question {self.id}"

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.id} - {self.text[:20]}"
