import datetime
from rest_framework import generics
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404

class EmployeeListAPIView(generics.ListAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeListSerializer

class EmployeeCreateAPIView(generics.CreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class EmployeeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class AttendanceListAPIView(generics.ListAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceListSerializer

class AttendanceCreateAPIView(generics.CreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

class AttendanceRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer


class TodaysEmployeesAttendaceListAPIView(generics.ListAPIView):
    queryset = Attendance.objects.all().filter(created_at = datetime.date.today())
    serializer_class=AttendanceListSerializer
