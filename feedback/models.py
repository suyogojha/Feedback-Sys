from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from _datetime import datetime


class Company(models.Model):
    name = models.CharField(max_length=100)
    tag_line = models.TextField()
    description = models.TextField()
    employee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    company_pic = models.ImageField(upload_to='pic_folder/', default='/pic_folder/nologo.jpg')

    def __str__(self):
        return self.name

    def save(self):

        if not self.id and not self.photo:
            return

        super(Company, self).save()

        company_pic = Image.open(self.company_pic)
        (width, height) = company_pic.size

        size = (500,350)
        size = (500,350)
        company_pic = company_pic.resize(size, Image.ANTIALIAS)
        company_pic.save(self.company_pic.path)


class Feedback(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.IntegerField()
    comment = models.TextField()
    timestamp = models.DateTimeField(default=datetime.now(), blank=True)

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)