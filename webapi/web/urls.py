from django.urls import path
from .views import *

urlpatterns = [
    path("", AttendanceListView.as_view(), name="attendance_list"),
    path("attendance_detail/<int:pk>", AttendanceDetail.as_view(), name="attendance_detail"),
    path("employees", EmployeeListView.as_view(), name="employee_list"),
    path("employees_detail/<int:pk>", EmployeeDetail.as_view(), name="employee_detail"),
]
