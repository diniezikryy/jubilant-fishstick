from django.contrib import admin
from .models import QuizAttempt, UserAnswer

class UserAnswerInline(admin.TabularInline):
    model = UserAnswer
    extra = 0

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'start_time', 'end_time', 'score')
    list_filter = ('start_time', 'end_time')
    search_fields = ('user__username', 'quiz__title')
    inlines = [UserAnswerInline]

@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('quiz_attempt', 'question', 'answer', 'text_answer')
    list_filter = ('quiz_attempt__quiz',)
    search_fields = ('quiz_attempt__user__username', 'question__text')