from django.contrib import admin
from .models import Course, Lesson, Announcement, Enrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'teacher', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['code', 'title', 'description']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'created_at']
    list_filter = ['course']
    search_fields = ['title', 'content']

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'teacher', 'created_at']
    list_filter = ['course']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_date', 'is_active']
    list_filter = ['is_active', 'course']