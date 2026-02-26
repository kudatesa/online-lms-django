from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Comment
from courses.models import Lesson
from .forms import CommentForm

@login_required
def add_comment(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.lesson = lesson
            comment.user = request.user
            
            # Check if it's a reply
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    parent = Comment.objects.get(id=parent_id)
                    comment.parent = parent
                except Comment.DoesNotExist:
                    pass
            
            comment.save()
            messages.success(request, "Comment added successfully")
    
    return redirect('course_detail', course_id=lesson.course.id)