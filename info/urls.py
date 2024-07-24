# evalvue_project/employees/urls.py

from django.urls import path
from info import views
from .views import EmployeeDashboardDataAPIView, EmployeeReviewDatAPIView, EmployeeReviewReportPIView, ShootOtpToEmployeeAPIView,VerifyOtpLoginAPIView,EmployeeOrganizationDataPIView
urlpatterns = [
    path('hello/', views.hello_world, name='hello_world'),
    path('shoot/otp/',ShootOtpToEmployeeAPIView.as_view() , name='shoot_otp'),
    path('login/verify/',VerifyOtpLoginAPIView.as_view() , name='verify_login'),
    path('employee/organizations/',EmployeeOrganizationDataPIView.as_view() , name='employee_organization'),
    path('employee/review/',EmployeeReviewDatAPIView.as_view() , name='employee_review'),
    path('employee/dashboard/',EmployeeDashboardDataAPIView.as_view(), name = 'dashboard'),
    path('report/',EmployeeReviewReportPIView.as_view() , name='report'), 
]
