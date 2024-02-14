from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views import generic
from attendance.models import *

class AttendanceListView(generic.ListView):
    queryset = Attendance.objects.order_by("-id")
    template_name = "index.html"

class AttendanceDetail(generic.DetailView):
    
    model = Attendance
    template_name = "attendance_detail.html"
    
class EmployeeListView(generic.ListView):
    model = Employee
    template_name = "employees.html"

class EmployeeDetail(generic.DetailView):
    model = Employee

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attendances"] = Attendance.objects.filter(employee = self.kwargs['pk']).order_by('-created_at')
        return context
    template_name = "employee_detail.html"
    