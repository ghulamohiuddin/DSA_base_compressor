from django.contrib import admin
from .models import CompressedFile

@admin.register(CompressedFile)
class CompressedFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'original_file', 'original_size', 'compressed_size', 'created_at')
