from django.urls import *
from .views import *

urlpatterns = [
    path('employees', EmployeeListCreateAPIView.as_view()),
    path('employees/<int:pk>', EmployeeRetrieveUpdateDestroyAPIView.as_view()),
    path('attendance', AttendanceListCreateAPIView.as_view()),
    path('attendance/<int:pk>', AttendanceRetrieveUpdateDestroyAPIView.as_view()),
]
