from django.db import models

class Employee(models.Model):
    fullname = models.CharField(max_length=100)
    telegram_account = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=9, null=True, blank=True)
    
    def __str__(self):
        return self.fullname
    

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, related_name='attendances', on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(auto_now_add=True)
    permission = models.CharField(max_length=255)
    reason = models.CharField(max_length=100)
    arrival_time = models.DateTimeField(auto_now_add=False)
    created_at =  models.DateField(auto_now=True)
    
    
    def __str__(self):
        return f"{self.employee} {self.permission}"
