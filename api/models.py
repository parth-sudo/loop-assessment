from django.db import models

# Create your models here.
STATUS_CHOICES = (
    ("Running", "Running"),
    ("Complete", "Complete")
)
  
class Report(models.Model):
    report_id = models.CharField(max_length=10, unique=True, blank=False)
    status = models.CharField(max_length=10, choices = STATUS_CHOICES, default="Running")

    def __str__(self):
        return self.report_id


class MyCSVFile(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to='csv_files/')
    report_id = models.CharField(max_length=10, default="abcd123456")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

