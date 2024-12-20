# quizzes/models.py

from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)

class Tag(models.Model):
    name = models.CharField(max_length=50)

class Quiz(models.Model):
    DIFFICULTY_CHOICES = [
        ('not_specified', 'Not Specified'),
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_quizzes')
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='quizzes')
    tags = models.ManyToManyField(Tag, blank=True, related_name='quizzes')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='not_specified')
    time_limit = models.IntegerField(null=True, blank=True, help_text="Time limit in minutes")

    def __str__(self):
        return self.title


class Question(models.Model):
    QUESTION_TYPES = [
        ('mcq', 'Multiple Choice'),
        ('short_answer', 'Short Answer'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='mcq')

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class TempQuestion(models.Model):
    QUESTION_TYPES = [
        ('mcq', 'Multiple Choice'),
        ('short_answer', 'Short Answer'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='temp_questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='mcq')
    slide_number = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return f"Temp: {self.text[:50]}"


class TempAnswer(models.Model):
    temp_question = models.ForeignKey(TempQuestion, on_delete=models.CASCADE, related_name='temp_answers')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Temp: {self.text}"

class TempPDF(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='temp_pdfs')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='temp_pdfs', null=True, blank=True)
    file = models.FileField(upload_to='temp_pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s PDF uploaded at {self.uploaded_at}"



