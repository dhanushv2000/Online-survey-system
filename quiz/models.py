from django.db import models
from django.contrib.auth.models import User

from student.models import Student
class Course(models.Model):
   user = models.ForeignKey(User,on_delete = models.CASCADE)
   course_name = models.CharField(max_length=50)
   question_number = models.PositiveIntegerField()
   status = models.BooleanField(default=False)
   start_date = models.DateTimeField()
   end_date = models.DateTimeField()
   def __str__(self):
        return self.course_name

class Question(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    question=models.CharField(max_length=600)
    option1=models.CharField(max_length=200)
    option2=models.CharField(max_length=200)
    option3=models.CharField(max_length=200)
    option4=models.CharField(max_length=200)
    cat=(('Option1','Option1'),('Option2','Option2'),('Option3','Option3'),('Option4','Option4'))
    option1_count = models.IntegerField(default = 0)
    option2_count = models.IntegerField(default = 0)
    option3_count = models.IntegerField(default = 0)
    option4_count = models.IntegerField(default = 0)

    def total(self):
        return self.option1_count+self.option2_count+self.option3_count+self.option4_count
