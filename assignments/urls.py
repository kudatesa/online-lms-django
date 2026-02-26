from django.urls import path
from . import views

urlpatterns = [
    
    path('course/<int:course_id>/', views.assignment_list, name='assignment_list'),
    path('<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    
    path('course/<int:course_id>/create/', views.create_assignment, name='create_assignment'),
    path('<int:assignment_id>/edit/', views.edit_assignment, name='edit_assignment'),
    path('<int:assignment_id>/delete/', views.delete_assignment, name='delete_assignment'),
    path('<int:assignment_id>/statistics/', views.assignment_statistics, name='assignment_statistics'),
    
    path('<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('submission/<int:submission_id>/update/', views.update_submission, name='update_submission'),
    
    path('submission/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
]