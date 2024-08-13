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
        fields = ['id', 'text', 'question_type', 'answers']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers', [])
        question = Question.objects.create(**validated_data)
        for answer_data in answers_data:
            Answer.objects.create(question=question, **answer_data)
        return question

    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answers', [])
        instance.text = validated_data.get('text', instance.text)
        instance.question_type = validated_data.get('question_type', instance.question_type)
        instance.save()

        # Keep track of the answers we've updated
        updated_answer_ids = []

        # Update or create answers
        for answer_data in answers_data:
            answer_id = answer_data.get('id')
            if answer_id:
                answer = Answer.objects.get(id=answer_id, question=instance)
                answer.text = answer_data.get('text', answer.text)
                answer.is_correct = answer_data.get('is_correct', answer.is_correct)
                answer.save()
                updated_answer_ids.append(answer_id)
            else:
                answer = Answer.objects.create(question=instance, **answer_data)
                updated_answer_ids.append(answer.id)

        # Delete any answers that weren't in the update data
        instance.answers.exclude(id__in=updated_answer_ids).delete()

        return instance

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    creator = serializers.ReadOnlyField(source='creator.username')

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'creator', 'created_at', 'questions']
        read_only_fields = ['creator', 'created_at']