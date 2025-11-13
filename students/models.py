from django.db import models

class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    course = models.CharField(max_length=50)
    age = models.IntegerField()
    gpa = models.FloatField()



def __str__(self):
    return f'Student: {self.first_name} {self.last_name}'


