from django.contrib import admin
from .models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'created_at', 'parent']
    list_filter = ['lesson__course']
    search_fields = ['content']