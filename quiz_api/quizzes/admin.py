from django.contrib import admin
from .models import Category, Tag, Quiz, Question, Answer, TempQuestion, TempAnswer, TempPDF

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'question_type')
    list_filter = ('quiz', 'question_type')
    search_fields = ('text', 'quiz__title')
    inlines = [AnswerInline]

class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'created_at', 'category', 'difficulty', 'time_limit')
    list_filter = ('creator', 'created_at', 'category', 'difficulty')
    search_fields = ('title', 'description', 'creator__username')
    filter_horizontal = ('tags',)
    inlines = [QuestionInline]

class TempAnswerInline(admin.TabularInline):
    model = TempAnswer
    extra = 1

class TempQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'question_type')
    list_filter = ('quiz', 'question_type')
    search_fields = ('text', 'quiz__title')
    inlines = [TempAnswerInline]

class TempPDFAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'uploaded_at')
    list_filter = ('user', 'uploaded_at')
    search_fields = ('user__username', 'quiz__title')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(TempQuestion, TempQuestionAdmin)
admin.site.register(TempPDF, TempPDFAdmin)