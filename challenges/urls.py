from django.urls import path
from challenges import views

urlpatterns = [
    path("", views.my_challenges, name="challengeQR"),
    path("api/v1/removeChallenge", views.remove_challenge),
    path("api/v1/removeTask", views.remove_task),
    path('challenge_increment_progress/<int:challenge_Id>', views.challenge_increment_progress, name='challenge_increment_progress'),
    path('scan-challenge/<int:challenge_id>/<str:qr_code>/', views.scan_challenge, name='scan_challenge'),
]