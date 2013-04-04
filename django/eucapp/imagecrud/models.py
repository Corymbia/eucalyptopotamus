from django.db import models

class Image(models.Model):
    name = models.CharField(max_length=256)
    pub_date = models.DateTimeField('date published')
    path = models.CharField(max_length=256)
