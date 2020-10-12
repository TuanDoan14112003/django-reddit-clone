from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, LoginForm
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash,authenticate,login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
# Create your views here.
def register(request):
    if request.user.is_authenticated:
        return redirect('homepage')
    if request.is_ajax():
        field = request.POST.get('field')
        response = {'error': 'success'}
        if field == 'username':
            username = request.POST.get('username')
            print(username)
            if User.objects.filter(username=username).exists():
                response['error'] = 'Username already exists'
        elif field == 'email':
            email = request.POST.get('email')
            if User.objects.filter(email=email).exists():
                response['error'] = 'A user with this email already exists'
        return JsonResponse(response)
    elif request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(
                request, f'Your account has been created! You are now able to log in')
            return redirect('login')
    else:
        form = UserRegisterForm(auto_id='signup_%s')
    return render(request, 'user/register.html', {'register_form': form})

# def login_view(request):
#     print('here')
#     if request.method == 'POST':
#         form = AuthenticationForm(request.POST)
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(username=username, password=password)

#         if user is not None:
#             if user.is_active:
#                 auth_login(request, user)
#                 return redirect('homepage')
#         # else:
#         #     messages.error(request,'username or password not correct')
#         #     return redirect('login')

#     else:
#         form = AuthenticationForm()
#     if request.user.is_authenticated():
#         print('user is authenticated')
#         return redirect('homepage')
#     return render(request, 'user/login.html', {'login_form': form})

# def loginPage(request):
#     form = AuthenticationForm()
#     if request.user.is_authenticated:
#         return redirect('homepage')
#     else:
#         if request.method == 'POST':
#             form = AuthenticationForm(request.POST)
#             username = request.POST.get('username')
#             password = request.POST.get('password')

#             user = authenticate(username=username, password=password)

#             if user is not None:
#                 login(request, user)
#                 return redirect("homepage")
#     context = {'form': form}
#     return render(request, 'user/login.html', context)
def loginPage(request):
    form = LoginForm(request.POST or None)
    if request.user.is_authenticated:
        return redirect('homepage')
    if request.POST and form.is_valid():
        user = form.login(request)
        if user:
            login(request, user)
            return redirect('homepage')
    return render(request, 'user/login.html', {'form': form })

@login_required
def ProfileEdit(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                    request.FILES,
                                    instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile',pk=request.user.id)

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    notifications = request.user.notifications.order_by('-timestamp')
    context['notifications'] = notifications
    context['unread_notifications'] =len(request.user.notifications.filter(unread=True))
    return render(request, 'user/profile-edit.html', context)
