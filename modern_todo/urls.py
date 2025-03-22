from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from django.shortcuts import redirect
from tasks import views

def redirect_to_task_list(request): #Add this function
    return redirect('task_list')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tasks/', include('tasks.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('', views.home, name='home'),
]
urlpatterns = format_suffix_patterns(urlpatterns)