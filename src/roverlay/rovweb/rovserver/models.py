from django.db import models

# Create your models here.

class ResearchObject(models.Model):
    uri = models.CharField(max_length=1000)

    def __unicode__(self):
        return self.uri
