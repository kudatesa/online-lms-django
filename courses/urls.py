from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('create/', views.create_course, name='create_course'),
    path('<int:course_id>/lesson/create/', views.create_lesson, name='create_lesson'),
    path('<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('<int:course_id>/announcement/create/', views.create_announcement, name='create_announcement'),
]