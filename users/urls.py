from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from .views import CustomLoginView, SignUpView, PrivacyView
from . import views

auth_patterns = [
    path("login/", CustomLoginView.as_view(), name="login"),  # Use CustomLoginView
    path("logout/", LogoutView.as_view(), name="logout"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path('privacy/', PrivacyView.as_view(), name='privacy'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='login/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='login/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='login/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='login/password_reset_complete.html'), name='password_reset_complete'),
]

friends_patterns = [
    path('', views.friends, name='friends'),
    path('api/v1/remove/', views.remove_friend),
    path('api/v1/send_request/', views.send_friend_request),
    path('api/v1/accept_request/', views.accept_friend_request),
    path('api/v1/reject_request/', views.reject_friend_request),
    path('api/v1/get_requests/', views.get_friend_requests),
]

settings_patterns = [
    path('', views.settings, name='settings'),
    path('delete_account/', views.delete_account, name='delete_account'),
]
