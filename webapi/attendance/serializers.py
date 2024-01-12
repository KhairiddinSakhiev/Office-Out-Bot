from rest_framework.serializers import ModelSerializer
from .models import *

class EmployeeListSerializer(ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"


class AttendanceSerializer(ModelSerializer):
    class Meta:
        model = Attendance
        fields = "__all__"