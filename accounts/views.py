from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone 
from django.contrib import messages
from django.db.models import Count
from .forms import UserRegistrationForm, UserLoginForm

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.profile.user_type = form.cleaned_data.get('user_type')
            user.profile.save()
            
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def dashboard(request):
    user_type = request.user.profile.user_type
    
    if user_type == 'admin':
        return redirect('admin_dashboard')
    elif user_type == 'teacher':
        return redirect('teacher_dashboard')
    elif user_type == 'student':
        return redirect('student_dashboard')
    elif user_type == 'parent':
        return redirect('parent_dashboard')
    else:
        return render(request, 'accounts/dashboard.html')

@login_required
def admin_dashboard(request):
    if request.user.profile.user_type != 'admin':
        return redirect('dashboard')
    
    from courses.models import Course
    from django.contrib.auth.models import User
    
    total_users = User.objects.count()
    total_teachers = User.objects.filter(profile__user_type='teacher').count()
    total_students = User.objects.filter(profile__user_type='student').count()
    total_courses = Course.objects.count()
    
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_courses = Course.objects.order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_courses': total_courses,
        'recent_users': recent_users,
        'recent_courses': recent_courses,
    }
    return render(request, 'accounts/admin_dashboard.html', context)

@login_required
def teacher_dashboard(request):
    if request.user.profile.user_type != 'teacher':
        return redirect('dashboard')
    
    from courses.models import Course
    from assignments.models import Assignment, Submission
    
    courses = Course.objects.filter(teacher=request.user)
    assignments = Assignment.objects.filter(teacher=request.user)
    
    # Get recent submissions needing grading
    pending_submissions = Submission.objects.filter(
        assignment__teacher=request.user
    ).annotate(
    grade_count=Count('grades')
    ).filter(
    grade_count=0
    ).order_by('-submitted_at')[:10]
    
    context = {
        'courses': courses,
        'assignments': assignments,
        'pending_submissions': pending_submissions,
    }
    return render(request, 'accounts/teacher_dashboard.html', context)

@login_required
def student_dashboard(request):
    if request.user.profile.user_type != 'student':
        return redirect('dashboard')
    
    from courses.models import Course, Enrollment
    from assignments.models import Assignment, Submission
    from django.utils import timezone
    
    # Get courses the student is enrolled in
    enrolled_courses = Course.objects.filter(
        enrollment__student=request.user,
        enrollment__is_active=True,
        is_active=True
    )
    
    # Get upcoming assignments from enrolled courses
    upcoming_assignments = Assignment.objects.filter(
        course__in=enrolled_courses,
        due_date__gte=timezone.now()
    ).order_by('due_date')[:5]
    
    # Get recent submissions
    recent_submissions = Submission.objects.filter(
        student=request.user
    ).order_by('-submitted_at')[:5]
    
    context = {
        'enrolled_courses': enrolled_courses,
        'upcoming_assignments': upcoming_assignments,
        'recent_submissions': recent_submissions,
    }
    return render(request, 'accounts/student_dashboard.html', context)
    
@login_required
def parent_dashboard(request):
    if request.user.profile.user_type != 'parent':
        return redirect('dashboard')
    
    # Get linked student
    linked_student = request.user.profile.linked_student
    
    if not linked_student:
        messages.info(request, "No student linked to your account yet.")
        return render(request, 'accounts/parent_dashboard.html', {'no_student': True})
    
    from courses.models import Course, Enrollment
    from assignments.models import Assignment, Submission
    
    # Get student's courses and assignments
    student_courses = linked_student.user.enrolled_courses.all()
    
    # Get recent grades
    recent_grades = Submission.objects.filter(
        student=linked_student.user,
        grade__isnull=False
    ).order_by('-submitted_at')[:10]
    
    context = {
        'student': linked_student.user,
        'student_courses': student_courses,
        'recent_grades': recent_grades,
    }
    return render(request, 'accounts/parent_dashboard.html', context)