from rest_framework import serializers
from .models import Quiz, Question, Answer, TempPDF, TempQuestion, TempAnswer


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
        # Remove answers data from the validated_data
        answers_data = validated_data.pop('answers', [])

        # Create the question
        quiz = self.context['view'].kwargs.get('quiz_pk')
        question = Question.objects.create(quiz_id=quiz, **validated_data)

        # Create answers for the question
        for answer_data in answers_data:
            Answer.objects.create(question=question, **answer_data)

        return question

    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answers', [])
        instance.text = validated_data.get('text', instance.text)
        instance.question_type = validated_data.get('question_type', instance.question_type)
        instance.save()

        # Keep track of existing answers
        existing_answers = {answer.id: answer for answer in instance.answers.all()}

        # Update or create answers
        for answer_data in answers_data:
            answer_id = answer_data.get('id')
            if answer_id and answer_id in existing_answers:
                # Update existing answer
                answer = existing_answers.pop(answer_id)
                for attr, value in answer_data.items():
                    setattr(answer, attr, value)
                answer.save()
            else:
                # Create new answer
                Answer.objects.create(question=instance, **answer_data)

        # Delete any answers not in the update data
        for answer in existing_answers.values():
            answer.delete()

        return instance


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    creator = serializers.ReadOnlyField(source='creator.username')

    class Meta:
        model = Quiz
        fields = '__all__'
        read_only_fields = ['creator', 'created_at']


class TempAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempAnswer
        fields = ['id', 'text', 'is_correct']


class TempQuestionSerializer(serializers.ModelSerializer):
    temp_answers = TempAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = TempQuestion
        fields = ['id', 'text', 'question_type', 'temp_answers']


class TempPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempPDF
        fields = ['id', 'file', 'uploaded_at']
