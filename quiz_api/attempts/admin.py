from django.contrib import admin
from .models import QuizAttempt, UserAnswer

class UserAnswerInline(admin.TabularInline):
    model = UserAnswer
    extra = 0
    readonly_fields = ('question', 'selected_answer', 'text_answer')

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'start_time', 'end_time', 'score', 'is_completed')
    list_filter = ('start_time', 'end_time')
    search_fields = ('user__username', 'quiz__title')
    readonly_fields = ('start_time', 'end_time', 'score')
    inlines = [UserAnswerInline]

    def is_completed(self, obj):
        return obj.end_time is not None
    is_completed.boolean = True
    is_completed.short_description = 'Completed'

@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('quiz_attempt', 'question', 'selected_answer', 'text_answer')
    list_filter = ('quiz_attempt__quiz',)
    search_fields = ('quiz_attempt__user__username', 'question__text')
    readonly_fields = ('quiz_attempt', 'question')