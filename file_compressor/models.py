from django.db import models

class CompressedFile(models.Model):
    original_file = models.FileField(upload_to='uploads/')
    compressed_file = models.FileField(upload_to='compressed/', null=True, blank=True)

    original_size = models.PositiveIntegerField()
    compressed_size = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_file.name
