# evalvue_project/employees/urls.py

from django.urls import path
from info import views

from .views import DeleteReportedReviewAPIView, EditEmployeeAPIview, EmployeeDashboardDataAPIView, EmployeeReviewDatAPIView, EmployeeReviewReportPIView, RejectReportedReviewRequestAPIView, ShootOtpToEmployeeAPIView,VerifyOtpLoginAPIView,EmployeeOrganizationDataPIView, VerifyReportedReviewDataAPIView
from .views import EmployeeDashboardDataAPIView, EmployeeProfileAPIView, EmployeeReviewDatAPIView, EmployeeReviewReportPIView, ShootOtpToEmployeeAPIView,VerifyOtpLoginAPIView,EmployeeOrganizationDataPIView
urlpatterns = [
    path('hello/', views.hello_world, name='hello_world'),
    path('shoot/otp/',ShootOtpToEmployeeAPIView.as_view() , name='shoot_otp'),
    path('login/verify/',VerifyOtpLoginAPIView.as_view() , name='verify_login'),
    path('employee/organizations/',EmployeeOrganizationDataPIView.as_view() , name='employee_organization'),
    path('employee/review/',EmployeeReviewDatAPIView.as_view() , name='employee_review'),
    path('employee/dashboard/',EmployeeDashboardDataAPIView.as_view(), name = 'dashboard'),
    path('report/',EmployeeReviewReportPIView.as_view() , name='report'), 
    path('edit/employee/',EditEmployeeAPIview.as_view() , name='edit_employee'), 
    path('employee/report/',EmployeeReviewReportPIView.as_view() , name='report'),
    path('employee/profile/',EmployeeProfileAPIView.as_view() , name='profile'),
    path('reported/reviews/',VerifyReportedReviewDataAPIView.as_view() , name='reported_reviews'),
    path('reject/review/request/',RejectReportedReviewRequestAPIView.as_view() , name='reject_review_request'),
    path('delete/review/',DeleteReportedReviewAPIView.as_view() , name='delete_review'),

]
