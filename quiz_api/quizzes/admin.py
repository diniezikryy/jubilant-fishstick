from django.contrib import admin
from .models import Quiz, Question, Answer

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'text', 'question_type', 'difficulty')
    list_filter = ('quiz', 'question_type', 'difficulty')
    search_fields = ('text', 'quiz__title')
    inlines = [AnswerInline]

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'pdf', 'created_at', 'num_questions', 'time_limit')
    list_filter = ('created_at', 'creator')
    search_fields = ('title', 'creator__username', 'pdf__title')