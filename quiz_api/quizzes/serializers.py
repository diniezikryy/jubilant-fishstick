from rest_framework import serializers
from .models import Quiz, Question, Answer

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'answers']

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    creator = serializers.ReadOnlyField(source='creator.username')

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'creator', 'created_at', 'questions']
        read_only_fields = ['creator', 'created_at']