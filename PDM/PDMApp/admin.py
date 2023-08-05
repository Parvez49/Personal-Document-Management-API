from django.contrib import admin

# Register your models here.

from .models import Document, ShareDocument

class DocumentAttr(admin.ModelAdmin):
    list_display=['title','format','owner']
admin.site.register(Document,DocumentAttr)


admin.site.register(ShareDocument)