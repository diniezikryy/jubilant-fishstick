from rest_framework import serializers
from .models import Quiz, Question, Answer


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'answers', 'quiz']

    def create(self, validated_data):
        quiz = self.context['view'].kwargs.get('quiz_pk')
        question = Question.objects.create(quiz_id=quiz, **validated_data)
        return question


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    creator = serializers.ReadOnlyField(source='creator.username')

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'creator', 'created_at', 'questions']
        read_only_fields = ['creator', 'created_at']
