from rest_framework.serializers import ModelSerializer
from .models import *
from rest_framework import serializers


class EmployeeSerializer(ModelSerializer):
    class Meta:
        model = Employee
        fields = ['fullname', 'telegram_account','phone_number']


class AttendanceSerializer(ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['permission', 'reason', 'arrival_time', 'employee']

class AttendanceListSerializer(ModelSerializer):
    employee = EmployeeSerializer(read_only = True)
    class Meta:
        model = Attendance
        fields = ['id', 'permission', 'reason', 'arrival_time', 'created_at', 'employee']
        

class EmployeeListSerializer(ModelSerializer):
    attendances = AttendanceSerializer(many = True, read_only = True)
    
    class Meta:
        model = Employee
        fields = ['id', 'fullname', 'telegram_account','phone_number', 'attendances']