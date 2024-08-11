from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import F

from .models import Question


@receiver(post_save, sender=Question)
def increment_num_questions(sender, instance, created, **kwargs):
    if created:
        instance.quiz.num_questions = F('num_questions') + 1
        instance.quiz.save()


@receiver(post_delete, sender=Question)
def decrement_num_questions(sender, instance, **kwargs):
    instance.quiz.num_questions = F('num_questions') - 1
    instance.quiz.save()
