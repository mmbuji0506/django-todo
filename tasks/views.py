from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Task
from .forms import TaskForm
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from .forms import CustomUserCreationForm
from django.db.models import Q
import datetime
from rest_framework import generics, permissions, filters
from .serializers import TaskSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator


def home(request):
    return render(request, 'tasks/home.html')

def extend_session(request):
    request.session.set_expiry(1200)
    return JsonResponse({"status": "ok"})

@login_required
def task_list(request):
    search_query = request.GET.get('search', '')
    priority_filter = request.GET.get('priority', '')
    status_filter = request.GET.get('status', '')
    sort_by = request.GET.get('sort_by', '')

    tasks = Task.objects.filter(user=request.user)
    if search_query:
        tasks = tasks.filter(title__icontains=search_query)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    if sort_by:
        tasks = tasks.order_by(sort_by)
    else:
        tasks = tasks.order_by('due_date')

    paginator = Paginator(tasks, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'task_list.html', {'tasks': page_obj})

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            messages.success(request, "Task created successfully.")
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('task_list')
    else:
        messages.error(request, "Task creation failed.")
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})

class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

class TaskListCreateAPIView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['priority', 'status', 'category']
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'priority']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TaskRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)