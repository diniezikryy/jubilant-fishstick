from django.contrib import admin
from .models import Quiz, Question, Answer

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz')
    list_filter = ('quiz',)
    inlines = [AnswerInline]

class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'created_at')
    list_filter = ('creator', 'created_at')

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)