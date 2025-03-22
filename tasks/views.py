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


def home(request):
    return render(request, 'tasks/home.html')

def extend_session(request):
    request.session.set_expiry(1200) #reset the session expiry.
    return JsonResponse({"status": "ok"})

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)

    # Filtering
    priority = request.GET.get('priority')
    status = request.GET.get('status')

    if priority:
        tasks = tasks.filter(priority=priority)
    if status:
        tasks = tasks.filter(status=status)

    # Sorting
    sort_by = request.GET.get('sort_by')
    if sort_by:
        tasks = tasks.order_by(sort_by)
    else:
        tasks = tasks.order_by('due_date')

    # Search
    search_query = request.GET.get('search')
    if search_query:
        tasks = tasks.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

    category = request.GET.get('category')
    if category:
        tasks = tasks.filter(category=category)

    for task in tasks:
        if task.due_date:
            time_difference = task.due_date - datetime.datetime.now(task.due_date.tzinfo)
            if datetime.timedelta(hours=1) >= time_difference >= datetime.timedelta(minutes=0):
                task.due_soon = True
            else:
                task.due_soon = False

    return render(request, 'tasks/task_list.html', {'tasks': tasks})

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