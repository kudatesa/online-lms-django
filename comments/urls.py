from django.urls import path
from . import views

urlpatterns = [
    path('lesson/<int:lesson_id>/add/', views.add_comment, name='add_comment'),
]