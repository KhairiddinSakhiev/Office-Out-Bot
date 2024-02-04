from django.urls import *
from .views import *

urlpatterns = [
    path('employees', EmployeeListAPIView.as_view()),
    path('employee/create', EmployeeCreateAPIView.as_view()),
    path('employee/<int:pk>', EmployeeRetrieveUpdateDestroyAPIView.as_view()),
    path('attendances', AttendanceListAPIView.as_view()),
    path('attendance/create', AttendanceCreateAPIView.as_view()),
    path('attendance/<int:pk>', AttendanceRetrieveUpdateDestroyAPIView.as_view()), 
    path('todays_attendances', TodaysEmployeesAttendaceListAPIView.as_view()), 
]
