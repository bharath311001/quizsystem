from django.contrib import admin
from .models import Quiz, Question, Option, StudentQuizResult

class OptionInline(admin.TabularInline):
    model = Option
    extra = 2

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1

class QuizAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ('title', 'created_by', 'created_at')

class QuestionAdmin(admin.ModelAdmin):
    inlines = [OptionInline]
    list_display = ('text', 'quiz')

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Option)
admin.site.register(StudentQuizResult)
