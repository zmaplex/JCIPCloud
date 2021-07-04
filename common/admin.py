# Register your models here.
from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget

# Register your models here.
from common.models import SystemConfig

@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'key', 'enable', 'module_name']
    list_editable = ['enable']
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

