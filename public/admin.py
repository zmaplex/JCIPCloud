from django.contrib import admin

# Register your models here.
from public.models import IPInfo


@admin.register(IPInfo)
class IPInfoAdmin(admin.ModelAdmin):
    list_display = ['ipaddress', 'asn_info', 'recaptcha_score', 'risk', 'update_at', 'source_ip']
    list_filter = ('risk',)
    search_fields = ['ipaddress', 'source_ip', 'asn_info']
