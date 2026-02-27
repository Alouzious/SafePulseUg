from django.contrib import admin
from .models import CrimeReport, Suspect, Witness


class SuspectInline(admin.TabularInline):
    model  = Suspect
    extra  = 0


class WitnessInline(admin.TabularInline):
    model  = Witness
    extra  = 0


@admin.register(CrimeReport)
class CrimeReportAdmin(admin.ModelAdmin):
    list_display    = [
        'case_number', 'title', 'category', 'severity',
        'status', 'district', 'date_occurred', 'is_analyzed'
    ]
    list_filter     = ['category', 'severity', 'status', 'district', 'is_analyzed']
    search_fields   = ['case_number', 'title', 'description', 'location']
    ordering        = ['-date_reported']
    readonly_fields = ['case_number', 'date_reported', 'date_updated']
    inlines         = [SuspectInline, WitnessInline]

    fieldsets = (
        ('Case Info',     {'fields': ('case_number', 'title', 'category', 'severity', 'status')}),
        ('Description',   {'fields': ('description', 'weapons_used', 'modus_operandi')}),
        ('Location',      {'fields': ('location', 'district', 'latitude', 'longitude')}),
        ('Victim Info',   {'fields': ('victim_count', 'victim_details')}),
        ('Evidence',      {'fields': ('evidence_notes', 'attachment')}),
        ('Reporting',     {'fields': ('reported_by', 'date_occurred', 'date_reported', 'date_updated')}),
        ('AI Analysis',   {'fields': ('is_analyzed',)}),
    )


@admin.register(Suspect)
class SuspectAdmin(admin.ModelAdmin):
    list_display  = ['name', 'alias', 'gender', 'is_arrested', 'crime_report']
    list_filter   = ['gender', 'is_arrested', 'known_to_victim']
    search_fields = ['name', 'alias', 'description']


@admin.register(Witness)
class WitnessAdmin(admin.ModelAdmin):
    list_display  = ['name', 'contact', 'is_anonymous', 'crime_report']
    list_filter   = ['is_anonymous']
    search_fields = ['name', 'statement']