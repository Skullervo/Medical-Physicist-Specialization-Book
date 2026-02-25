from django.contrib import admin
from .models import Specialty, EPA, FrontPage, ExamQuestion, ExamAnswer, Section, LearningObjective

admin.site.register(FrontPage)
admin.site.register(ExamQuestion)
admin.site.register(ExamAnswer)


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(EPA)
class EPAAdmin(admin.ModelAdmin):
    list_display = ['title', 'specialty', 'slug', 'order']
    list_filter = ['specialty']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(LearningObjective)
class LearningObjectiveAdmin(admin.ModelAdmin):
    list_display = ['code', 'level', 'epa', 'description']
    list_filter = ['level', 'epa__specialty']
    search_fields = ['code', 'description']


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'epa', 'proficiency_level', 'order']
    list_filter = ['epa__specialty', 'proficiency_level']
