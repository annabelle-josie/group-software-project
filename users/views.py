import json
import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth import logout
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from users.models import CustomUser
from .forms import CustomUserCreationForm, ProfileUpdateForm, CustomPasswordChangeForm

custom_user = get_user_model()

# Explicitly set correct template path, as we arent using registration, so without this it assumes the path as /registration/login.html 
class CustomLoginView(LoginView):
    template_name = "users/login.html"

class SignUpView(CreateView):
    model = custom_user
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "users/signup.html"

class PrivacyView(TemplateView):
    template_name = 'users/privacy.html'

class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'users/password_reset.html'

    def form_valid(self, form):
        print("PASSWORD: ", os.getenv("EMAIL_HOST_PASSWORD"))
        return super().form_valid(form)

class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'

class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'

class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'


@login_required(login_url="/auth/login")
def friends(request):
    user_friends = request.user.get_friends()
    friends_total = user_friends.count()

    if friends_total > 4:
        paginator = Paginator(user_friends, 4)
        page_number = request.GET.get('page')
        friends_page = paginator.get_page(page_number)
    else:
        friends_page = user_friends

    return render(request, "users/friends.html", {"friends_page": friends_page, "friends_total": friends_total})

@login_required
@api_view(["POST"])
def remove_friend(request):
    """API to remove a friend"""
    data = json.loads(request.body)
    friend_id = data.get("user_id")
    if not friend_id:
        return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
    
    friend = get_object_or_404(CustomUser, id=friend_id)
    request.user.unfriend(friend)
    return Response({"message": "Friend removed successfully."}, status=status.HTTP_200_OK)


@login_required
@api_view(["POST"])
def send_friend_request(request):
    """API to send a friend request"""
    data = json.loads(request.body)
    username = data.get("username")
    if not username:
        return Response({"success": False, "message": "Username is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        to_user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        return Response({"success": False, "message": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

    request.user.send_friend_request(to_user)
    return Response({"success": True, "message": "Friend request sent."}, status=status.HTTP_200_OK)



@login_required
@api_view(["POST"])
def accept_friend_request(request):
    """API to accept a friend request"""
    data = json.loads(request.body)
    friend_id = data.get("user_id")
    if not friend_id:
        return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
    
    friend = get_object_or_404(CustomUser, id=friend_id)
    request.user.accept_friend_request(friend)
    return Response({"message": "Friend request accepted."}, status=status.HTTP_200_OK)



@login_required
@api_view(["POST"])
def reject_friend_request(request):
    """API to reject a friend request"""
    data = json.loads(request.body)
    friend_id = data.get("user_id")
    if not friend_id:
        return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
    
    friend = get_object_or_404(CustomUser, id=friend_id)
    request.user.reject_friend_request(friend)
    return Response({"message": "Friend request rejected."}, status=status.HTTP_200_OK)


@login_required
@api_view(["GET"])
def get_friend_requests(request):
    """API to get all incoming friend requests"""
    friend_requests = request.user.get_incoming_friend_requests().values("id", "username")
    return Response({"friend_requests": list(friend_requests)}, status=status.HTTP_200_OK)


@login_required()
def settings(request):
    user_form = ProfileUpdateForm(instance=request.user)
    password_form = CustomPasswordChangeForm(user=request.user)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user_form = ProfileUpdateForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('settings')
        elif 'change_password' in request.POST:
            password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, 'Your password has been changed successfully!')
                return redirect('/auth/login/')
    else:
        user_form = ProfileUpdateForm(instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user)

    context = {
        'user_form': user_form,
        'password_form': password_form
    }
    return render(request, "users/settings.html", context)

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('home')
    return render(request, 'users/settings.html')