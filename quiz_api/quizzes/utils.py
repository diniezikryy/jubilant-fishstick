# quizzes/utils.py

from .models import Question, Answer


def make_permanent(temp_question):
    """
    Function to permanently add the question to the quiz and deletes the temporary question or answers.
    """
    permanent_question = Question.objects.create(
        quiz=temp_question.quiz,
        text=temp_question.text,
        question_type=temp_question.question_type,
    )

    for temp_answer in temp_question.temp_answers.all():
        Answer.objects.create(
            question=permanent_question,
            text=temp_answer.text,
            is_correct=temp_answer.is_correct
        )
    temp_question.delete()  # This will also delete associated temp answers
    return permanent_question
