from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class PDF(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='pdfs/')
    title = models.CharField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.IntegerField(help_text="File size in bytes")
    num_pages = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title
