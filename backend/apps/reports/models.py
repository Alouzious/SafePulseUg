from django.db      import models
from django.conf    import settings


# ─────────────────────────────────────────────────────────────
# REPORT TYPE CHOICES
# ─────────────────────────────────────────────────────────────
class ReportType(models.TextChoices):
    CRIME_LIST      = 'crime_list',     'Crime List Report'
    SINGLE_CRIME    = 'single_crime',   'Single Crime Report'
    ANALYSIS        = 'analysis',       'AI Analysis Report'
    STATISTICS      = 'statistics',     'Statistics Report'
    DISTRICT        = 'district',       'District Report'


# ─────────────────────────────────────────────────────────────
# REPORT FORMAT CHOICES
# ─────────────────────────────────────────────────────────────
class ReportFormat(models.TextChoices):
    PDF     = 'pdf',    'PDF'
    EXCEL   = 'excel',  'Excel'


# ─────────────────────────────────────────────────────────────
# GENERATED REPORT MODEL
# ─────────────────────────────────────────────────────────────
class GeneratedReport(models.Model):

    generated_by    = models.ForeignKey(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.SET_NULL,
                        null=True,
                        related_name='generated_reports'
                      )
    title           = models.CharField(max_length=200)
    report_type     = models.CharField(
                        max_length=20,
                        choices=ReportType.choices,
                        default=ReportType.CRIME_LIST
                      )
    report_format   = models.CharField(
                        max_length=10,
                        choices=ReportFormat.choices,
                        default=ReportFormat.PDF
                      )
    file            = models.FileField(
                        upload_to='reports/',
                        null=True,
                        blank=True
                      )
    parameters      = models.JSONField(default=dict, blank=True)  # filters used
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Generated Report'
        verbose_name_plural = 'Generated Reports'
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.title} [{self.report_format}] — {self.created_at:%Y-%m-%d}"