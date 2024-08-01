from django.contrib import admin
from .models import PDF

@admin.register(PDF)
class PDFAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'uploaded_at', 'file_size', 'num_pages')
    list_filter = ('uploaded_at', 'user')
    search_fields = ('title', 'user__username')