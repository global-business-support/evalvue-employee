# evalvue_project/employees/urls.py

from django.urls import path
from info import views

urlpatterns = [
    path('hello/', views.hello_world, name='hello_world'),
]
