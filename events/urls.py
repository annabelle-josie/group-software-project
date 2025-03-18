from django.urls import path
from . import views

urlpatterns = [
    path("", views.events, name="events"),
    path('sign_up_for_event/<int:event_id>/', views.sign_up_for_event, name='sign_up_for_event'),
    path('delete_event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('scan-qr/<int:event_id>/<str:qr_code>/', views.scan_qr, name='scan_qr'),
    path('incrementProgress/<int:event_id>/', views.incrementProgress, name='incrementProgress'),
]