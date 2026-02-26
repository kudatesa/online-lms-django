from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Assignment, Submission
from courses.models import Course
from .forms import AssignmentForm, SubmissionForm, GradeForm

@login_required
def assignment_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Check permissions
    if request.user.profile.user_type == 'student':
        # Students see assignments for courses they're enrolled in
        if not course.students.filter(id=request.user.id).exists():
            messages.error(request, "You are not enrolled in this course.")
            return redirect('course_list')
        assignments = course.assignments.all()
    elif request.user.profile.user_type == 'teacher' and request.user == course.teacher:
        # Teachers see all assignments for their courses
        assignments = course.assignments.all()
    elif request.user.profile.user_type == 'admin':
        assignments = course.assignments.all()
    else:
        messages.error(request, "You don't have permission to view these assignments.")
        return redirect('dashboard')
    
    context = {
        'course': course,
        'assignments': assignments,
        'now': timezone.now(),
    }
    return render(request, 'assignments/assignment_list.html', context)

@login_required
def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    submission = None
    all_submissions = None
    
    # Check permissions
    if request.user.profile.user_type == 'student':
        # Students can only view if enrolled
        if not assignment.course.students.filter(id=request.user.id).exists():
            messages.error(request, "You are not enrolled in this course.")
            return redirect('course_list')
        
        # Get student's submission if any
        try:
            submission = Submission.objects.get(assignment=assignment, student=request.user)
        except Submission.DoesNotExist:
            submission = None
            
    elif request.user == assignment.teacher or request.user.profile.user_type == 'admin':
        # Teachers and admins see all submissions
        all_submissions = assignment.submissions.all().select_related('student')
    
    context = {
        'assignment': assignment,
        'submission': submission,
        'all_submissions': all_submissions,
        'now': timezone.now(),
    }
    return render(request, 'assignments/assignment_detail.html', context)

@login_required
def create_assignment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Only teachers of this course or admins can create assignments
    if request.user != course.teacher and request.user.profile.user_type != 'admin':
        messages.error(request, "You don't have permission to create assignments for this course.")
        return redirect('course_detail', course_id=course.id)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.course = course
            assignment.teacher = request.user
            assignment.save()
            messages.success(request, f"Assignment '{assignment.title}' created successfully!")
            
            # Send notification to enrolled students (you can implement this later)
            
            return redirect('assignment_list', course_id=course.id)
    else:
        form = AssignmentForm()
    
    return render(request, 'assignments/create_assignment.html', {
        'form': form, 
        'course': course
    })

@login_required
def edit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Check permissions
    if request.user != assignment.teacher and request.user.profile.user_type != 'admin':
        messages.error(request, "You don't have permission to edit this assignment.")
        return redirect('assignment_detail', assignment_id=assignment.id)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment updated successfully!")
            return redirect('assignment_detail', assignment_id=assignment.id)
    else:
        form = AssignmentForm(instance=assignment)
    
    return render(request, 'assignments/edit_assignment.html', {
        'form': form,
        'assignment': assignment
    })

@login_required
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Check permissions
    if request.user != assignment.teacher and request.user.profile.user_type != 'admin':
        messages.error(request, "You don't have permission to delete this assignment.")
        return redirect('assignment_detail', assignment_id=assignment.id)
    
    if request.method == 'POST':
        course_id = assignment.course.id
        assignment.delete()
        messages.success(request, "Assignment deleted successfully!")
        return redirect('assignment_list', course_id=course_id)
    
    return render(request, 'assignments/delete_assignment.html', {'assignment': assignment})

@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Only enrolled students can submit
    if request.user.profile.user_type != 'student':
        messages.error(request, "Only students can submit assignments.")
        return redirect('assignment_detail', assignment_id=assignment.id)
    
    if not assignment.course.students.filter(id=request.user.id).exists():
        messages.error(request, "You are not enrolled in this course.")
        return redirect('course_list')
    
    # Check if already submitted
    try:
        submission = Submission.objects.get(assignment=assignment, student=request.user)
        messages.info(request, "You have already submitted this assignment. You can update your submission below.")
        return redirect('update_submission', submission_id=submission.id)
    except Submission.DoesNotExist:
        pass
    
    # Check if assignment is past due
    if timezone.now() > assignment.due_date:
        messages.warning(request, "This assignment is past the due date. You can still submit, but it may be marked as late.")
    
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.save()
            messages.success(request, "Assignment submitted successfully!")
            return redirect('assignment_detail', assignment_id=assignment.id)
    else:
        form = SubmissionForm()
    
    return render(request, 'assignments/submit_assignment.html', {
        'form': form, 
        'assignment': assignment
    })

@login_required
def update_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    
    # Only the student who submitted can update
    if request.user != submission.student:
        messages.error(request, "You don't have permission to update this submission.")
        return redirect('assignment_detail', assignment_id=submission.assignment.id)
    
    # Check if already graded
    if submission.is_graded():
        messages.warning(request, "This submission has already been graded. Contact your teacher if you need to resubmit.")
        return redirect('assignment_detail', assignment_id=submission.assignment.id)
    
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, "Your submission has been updated!")
            return redirect('assignment_detail', assignment_id=submission.assignment.id)
    else:
        form = SubmissionForm(instance=submission)
    
    return render(request, 'assignments/update_submission.html', {
        'form': form,
        'submission': submission
    })

@login_required
def grade_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    
    # Only the teacher of the course or admin can grade
    if request.user != submission.assignment.teacher and request.user.profile.user_type != 'admin':
        messages.error(request, "You don't have permission to grade this submission.")
        return redirect('assignment_detail', assignment_id=submission.assignment.id)
    
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, f"Grade saved for {submission.student.username}!")
            return redirect('assignment_detail', assignment_id=submission.assignment.id)
    else:
        form = GradeForm(instance=submission)
    
    return render(request, 'assignments/grade_submission.html', {
        'form': form, 
        'submission': submission
    })

@login_required
def assignment_statistics(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Only teacher or admin can view statistics
    if request.user != assignment.teacher and request.user.profile.user_type != 'admin':
        messages.error(request, "You don't have permission to view statistics.")
        return redirect('assignment_detail', assignment_id=assignment.id)
    
    # Get all submissions
    submissions = assignment.submissions.all()
    
    # Calculate statistics
    total_students = assignment.course.students.count()
    submitted_count = submissions.count()
    graded_count = submissions.filter(grade__isnull=False).count()
    
    # Grade distribution
    grades = [s.grade for s in submissions if s.grade is not None]
    avg_grade = sum(grades) / len(grades) if grades else 0
    max_grade = max(grades) if grades else 0
    min_grade = min(grades) if grades else 0
    
    # Late submissions
    late_count = submissions.filter(submitted_at__gt=assignment.due_date).count()
    
    context = {
        'assignment': assignment,
        'total_students': total_students,
        'submitted_count': submitted_count,
        'graded_count': graded_count,
        'avg_grade': round(avg_grade, 2),
        'max_grade': max_grade,
        'min_grade': min_grade,
        'late_count': late_count,
    }
    
    return render(request, 'assignments/assignment_statistics.html', context)