from django.urls import path
from . import views
from .views import SignUpView, TaskListCreateAPIView, TaskRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('create/', views.task_create, name='task_create'),
    path('update/<int:pk>/', views.task_update, name='task_update'),
    path('delete/<int:pk>/', views.task_delete, name='task_delete'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('api/tasks/', TaskListCreateAPIView.as_view()),
    path('api/tasks/<int:pk>/', TaskRetrieveUpdateDestroyAPIView.as_view()),
    path('extend_session/', views.extend_session, name = 'extend_session'),
]