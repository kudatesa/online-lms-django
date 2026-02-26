from django.contrib import admin
from .models import Assignment, Submission

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'teacher', 'due_date', 'total_points']
    list_filter = ['course', 'due_date']
    search_fields = ['title', 'description']

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'submitted_at', 'get_grade')

    def get_grade(self, obj):
        grade = obj.grades.first()  # because related_name="grades"
        return grade.score if grade else "Not graded"

    get_grade.short_description = "Grade"