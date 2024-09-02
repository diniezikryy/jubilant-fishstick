from rest_framework import serializers
from .models import QuizAttempt, UserAnswer
from django.db.models import Count, Case, When, IntegerField, F



class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = ['id', 'question', 'selected_answer', 'text_answer']


class DetailedAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text')
    correct_answer_text = serializers.SerializerMethodField()
    selected_answer_text = serializers.CharField(source='selected_answer.text', allow_null=True)
    is_correct = serializers.SerializerMethodField()

    class Meta:
        model = UserAnswer
        fields = ['id', 'question', 'question_text', 'selected_answer', 'selected_answer_text', 'correct_answer_text', 'text_answer', 'is_correct']

    def get_correct_answer_text(self, obj):
        correct_answer = obj.question.answers.filter(is_correct=True).first()
        return correct_answer.text if correct_answer else None

    def get_is_correct(self, obj):
        if obj.question.question_type == 'mcq':
            return obj.selected_answer and obj.selected_answer.is_correct
        # For other question types, you might need to implement a different logic
        return False

class QuizAttemptSerializer(serializers.ModelSerializer):
    user_answers = DetailedAnswerSerializer(many=True, read_only=True)
    total_questions = serializers.SerializerMethodField()
    correct_answers = serializers.SerializerMethodField()
    incorrect_answers = serializers.SerializerMethodField()
    detailed_results = serializers.SerializerMethodField()

    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'user', 'start_time', 'end_time', 'score', 'user_answers', 'total_questions',
                  'correct_answers', 'incorrect_answers', 'detailed_results']
        read_only_fields = ['user', 'start_time', 'end_time', 'score', 'total_questions', 'correct_answers',
                            'incorrect_answers', 'detailed_results']

    def create(self, validated_data):
        user = self.context['request'].user
        if 'user' not in validated_data:
            validated_data['user'] = user
        return QuizAttempt.objects.create(**validated_data)

    def get_total_questions(self, obj):
        return obj.user_answers.count()

    def get_correct_answers(self, obj):
        return obj.user_answers.filter(selected_answer__is_correct=True).count()

    def get_incorrect_answers(self, obj):
        return self.get_total_questions(obj) - self.get_correct_answers(obj)

    def get_detailed_results(self, obj):
        correct_answers = obj.user_answers.filter(selected_answer__is_correct=True)
        incorrect_answers = obj.user_answers.filter(selected_answer__is_correct=False)

        return {
            'correct_answers': DetailedAnswerSerializer(correct_answers, many=True).data,
            'incorrect_answers': DetailedAnswerSerializer(incorrect_answers, many=True).data
        }



class QuizAttemptsOverviewSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    attempt_count = serializers.IntegerField()
    highest_score = serializers.IntegerField(allow_null=True)
