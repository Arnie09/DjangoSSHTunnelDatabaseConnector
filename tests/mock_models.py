from datetime import datetime
from django.db import models


class SampleModel(models.Model):

    class Meta:
        app_label = 'sample_app'
        db_table = 'sample_table'

    sample_column = models.CharField(default='value')
    date = models.DateField(default=datetime.now())
    null_column = models.CharField(default=None)
    another_column = models.CharField(default="sample")
