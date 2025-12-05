from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DesignRequest
from .forms import CustomUserCreationForm, DesignRequestForm


# Главная страница
def home(request):
    # 4 последние заявки со статусом "Выполнено"
    completed_requests = DesignRequest.objects.filter(status='completed').order_by('-created_at')[:4]
    # Счётчик заявок в статусе "Принято в работу"
    in_progress_count = DesignRequest.objects.filter(status='in_progress').count()
    return render(request, 'catalog/index.html', {
        'completed_requests': completed_requests,
        'in_progress_count': in_progress_count
    })

# Регистрация
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('profile')
        else:
            messages.error(request, 'Ошибка при регистрации.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'catalog/register.html', {'form': form})

# Вход
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, 'Неверный логин или пароль.')
    return render(request, 'catalog/login.html')

# Выход
def user_logout(request):
    logout(request)
    return redirect('home')

# Личный кабинет
@login_required
def profile(request):
    return render(request, 'catalog/profile.html')

# Список своих заявок
@login_required
def my_requests(request):
    status_filter = request.GET.get('status', '')
    requests = DesignRequest.objects.filter(client=request.user)
    if status_filter:
        requests = requests.filter(status=status_filter)
    requests = requests.order_by('-created_at')
    return render(request, 'catalog/my_requests.html', {
        'requests': requests,
        'status_filter': status_filter
    })

# Создание заявки
@login_required
def create_request(request):
    if request.method == 'POST':
        form = DesignRequestForm(request.POST, request.FILES)
        if form.is_valid():
            design_req = form.save(commit=False)
            design_req.client = request.user
            design_req.save()
            messages.success(request, 'Заявка успешно создана!')
            return redirect('my_requests')
        else:
            messages.error(request, 'Ошибка при создании заявки.')
    else:
        form = DesignRequestForm()
    return render(request, 'catalog/create_request.html', {'form': form})

# Удаление заявки
@login_required
def delete_request(request, pk):
    req = get_object_or_404(DesignRequest, pk=pk, client=request.user)
    if not req.can_be_deleted:
        messages.error(request, 'Нельзя удалить заявку, которая уже в работе или выполнена.')
        return redirect('my_requests')
    if request.method == 'POST':
        req.delete()
        messages.success(request, 'Заявка удалена.')
        return redirect('my_requests')
    return render(request, 'catalog/delete_request_confirm.html', {'request_obj': req})

# Детали заявки
@login_required
def request_detail(request, pk):
    req = get_object_or_404(DesignRequest, pk=pk, client=request.user)
    return render(request, 'catalog/request_detail.html', {'request': req})