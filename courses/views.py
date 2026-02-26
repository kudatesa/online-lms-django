from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Lesson, Announcement, Enrollment
from .forms import CourseForm, LessonForm, AnnouncementForm

@login_required
def course_list(request):
    user_type = request.user.profile.user_type
    
    if user_type == 'teacher':
        courses = Course.objects.filter(teacher=request.user, is_active=True)
    elif user_type == 'student':
        # For students, show all active courses they can enroll in
        courses = Course.objects.filter(is_active=True)
    elif user_type == 'parent':
        # For parents, show courses of their linked student
        if request.user.profile.linked_student:
            student = request.user.profile.linked_student.user
            courses = student.enrolled_courses.filter(is_active=True)
        else:
            courses = Course.objects.none()
    else:  # admin
        courses = Course.objects.all()
    
    return render(request, 'courses/course_list.html', {'courses': courses})

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all()
    announcements = course.announcements.all()
    
    # Check if student is enrolled
    is_enrolled = False
    if request.user.profile.user_type == 'student':
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    
    context = {
        'course': course,
        'lessons': lessons,
        'announcements': announcements,
        'is_enrolled': is_enrolled,
    }
    return render(request, 'courses/course_detail.html', context)

@login_required
def create_course(request):
    if request.user.profile.user_type != 'admin' and request.user.profile.user_type != 'teacher':
        messages.error(request, "You don't have permission to create courses")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            messages.success(request, "Course created successfully")
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseForm()
    
    return render(request, 'courses/create_course.html', {'form': form})

@login_required
def create_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if request.user != course.teacher and request.user.profile.user_type != 'admin':
        messages.error(request, "You don't have permission to add lessons")
        return redirect('course_detail', course_id=course.id)
    
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, "Lesson created successfully")
            return redirect('course_detail', course_id=course.id)
    else:
        form = LessonForm()
    
    return render(request, 'courses/create_lesson.html', {'form': form, 'course': course})

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if request.user.profile.user_type == 'student':
        # Check if already enrolled
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course,
            defaults={'is_active': True}
        )
        
        if created:
            messages.success(request, f"You have successfully enrolled in {course.title}!")
        else:
            if not enrollment.is_active:
                enrollment.is_active = True
                enrollment.save()
                messages.success(request, f"Your enrollment in {course.title} has been reactivated!")
            else:
                messages.info(request, f"You are already enrolled in {course.title}.")
        
        return redirect('course_detail', course_id=course.id)
    else:
        messages.error(request, "Only students can enroll in courses.")
        return redirect('course_list')

@login_required
def create_announcement(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if request.user != course.teacher and request.user.profile.user_type != 'admin':
        messages.error(request, "You don't have permission to post announcements")
        return redirect('course_detail', course_id=course.id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        Announcement.objects.create(
            course=course,
            teacher=request.user,
            title=title,
            content=content
        )
        messages.success(request, "Announcement posted successfully")
    
    return redirect('course_detail', course_id=course.id)