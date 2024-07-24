# evalvue_project/employees/urls.py

from django.urls import path
from info import views
from .views import EmployeeReviewDataPIView, ShootOtpToEmployeeAPIView,VerifyOtpLoginAPIView,EmployeeOrganizationDataPIView
urlpatterns = [
    path('hello/', views.hello_world, name='hello_world'),
    path('shoot/otp/',ShootOtpToEmployeeAPIView.as_view() , name='shoot_otp'),
    path('login/verify/',VerifyOtpLoginAPIView.as_view() , name='verify_login'),
    path('employee/organizations/',EmployeeOrganizationDataPIView.as_view() , name='employee_organization'),
    path('employee/review/',EmployeeReviewDataPIView.as_view() , name='employee_review'),
]
