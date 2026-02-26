from django import forms
from .models import Course, Lesson, Announcement


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'code', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'notes_file', 'video_url']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 6}),
        }
        
class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = '__all__'