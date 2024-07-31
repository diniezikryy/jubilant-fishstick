from django.db import models
from documents.models import PDF

# Create your models here.
class Quiz(models.Model):
    pdf = models.ForeignKey(PDF, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    num_questions = models.IntegerField()
    time_limit = models.IntegerField(help_text="Time limit in minutes", null=True, blank=True)

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
