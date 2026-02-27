from django.contrib import admin
from .models        import GeneratedReport


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display    = [
        'title', 'report_type', 'report_format',
        'generated_by', 'created_at'
    ]
    list_filter     = ['report_type', 'report_format']
    search_fields   = ['title']
    readonly_fields = ['created_at']