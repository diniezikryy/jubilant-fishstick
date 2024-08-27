from rest_framework import serializers
from .models import QuizAttempt, UserAnswer


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = ['id', 'question', 'selected_answer', 'text_answer']


class QuizAttemptSerializer(serializers.ModelSerializer):
    user_answers = UserAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'user', 'start_time', 'end_time', 'score', 'user_answers']
        read_only_fields = ['user', 'start_time', 'end_time', 'score']

        def create(self, validated_data):
            user = self.context['request'].user
            return QuizAttempt.objects.create(user=user, **validated_data)


class QuizAttemptsOverviewSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    attempt_count = serializers.IntegerField()
    highest_score = serializers.IntegerField(allow_null=True)
