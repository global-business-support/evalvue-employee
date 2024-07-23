# evalvue_project/employees/urls.py

from django.urls import path
from info import views
from .views import ShootOtpToEmployeeAPIView
urlpatterns = [
    path('hello/', views.hello_world, name='hello_world'),
    path('shoot/otp/',ShootOtpToEmployeeAPIView.as_view() , name='shoot_otp'),
]
