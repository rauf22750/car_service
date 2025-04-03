

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.car_register, name='car_register'),
    path('list/', views.car_list, name='car_list'),
    path('<int:car_id>/', views.car_detail, name='car_detail'),
    path('<int:car_id>/history/', views.service_history, name='service_history'),
    path('<int:car_id>/recommendations/', views.service_recommendations, name='service_recommendations'),
    path('schedule-service/', views.schedule_service, name='schedule_service'),
    path('checkout/', views.service_checkout, name='service_checkout'),
    path('checkout/confirm/', views.confirm_checkout, name='confirm_checkout'),
    # path('checkout/confirmation/', views.service_confirmation, name='service_confirmation'),
]