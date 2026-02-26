from django.db import models
from django.contrib.auth.models import User
from courses.models import Course
from django.utils import timezone

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    total_points = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['due_date']
    
    def __str__(self):
        return f"{self.course.code} - {self.title}"
    
    def is_past_due(self):
        return timezone.now() > self.due_date

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    submission_file = models.FileField(upload_to='submissions/', blank=True, null=True)
    submission_text = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(blank=True)
    grade = models.IntegerField(null=True, blank=True)

class Grade(models.Model):
    submission = models.ForeignKey(
        'Submission',
        on_delete=models.CASCADE,
        related_name="grades"
    )
    score = models.IntegerField()
    feedback = models.TextField(blank=True)
    graded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.submission} - {self.score}"
    
    class Meta:
        ordering = ['-graded_at']

    def __str__(self):
        return f"{self.submission} - {self.score}"