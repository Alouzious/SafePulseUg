from django.db import models
from django.conf import settings


# ─────────────────────────────────────────────────────────────
# CRIME CATEGORY CHOICES
# ─────────────────────────────────────────────────────────────
class CrimeCategory(models.TextChoices):
    THEFT           = 'theft',          'Theft'
    ASSAULT         = 'assault',        'Assault'
    HOMICIDE        = 'homicide',       'Homicide'
    FRAUD           = 'fraud',          'Fraud'
    CYBERCRIME      = 'cybercrime',     'Cybercrime'
    ROBBERY         = 'robbery',        'Robbery'
    BURGLARY        = 'burglary',       'Burglary'
    DRUG_OFFENSE    = 'drug_offense',   'Drug Offense'
    SEXUAL_OFFENSE  = 'sexual_offense', 'Sexual Offense'
    VANDALISM       = 'vandalism',      'Vandalism'
    KIDNAPPING      = 'kidnapping',     'Kidnapping'
    ARSON           = 'arson',          'Arson'
    CORRUPTION      = 'corruption',     'Corruption'
    OTHER           = 'other',          'Other'


# ─────────────────────────────────────────────────────────────
# CRIME STATUS CHOICES
# ─────────────────────────────────────────────────────────────
class CrimeStatus(models.TextChoices):
    REPORTED        = 'reported',       'Reported'
    UNDER_INVESTIGATION = 'under_investigation', 'Under Investigation'
    SOLVED          = 'solved',         'Solved'
    CLOSED          = 'closed',         'Closed'
    COLD_CASE       = 'cold_case',      'Cold Case'


# ─────────────────────────────────────────────────────────────
# SEVERITY CHOICES
# ─────────────────────────────────────────────────────────────
class CrimeSeverity(models.TextChoices):
    LOW             = 'low',            'Low'
    MEDIUM          = 'medium',         'Medium'
    HIGH            = 'high',           'High'
    CRITICAL        = 'critical',       'Critical'


# ─────────────────────────────────────────────────────────────
# CRIME REPORT MODEL
# ─────────────────────────────────────────────────────────────
class CrimeReport(models.Model):

    # ── Reporting officer ────────────────────────────────────
    reported_by     = models.ForeignKey(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.SET_NULL,
                        null=True,
                        related_name='crime_reports'
                      )

    # ── Crime identification ─────────────────────────────────
    case_number     = models.CharField(max_length=30, unique=True, blank=True)
    title           = models.CharField(max_length=200)
    category        = models.CharField(
                        max_length=30,
                        choices=CrimeCategory.choices,
                        default=CrimeCategory.OTHER
                      )
    severity        = models.CharField(
                        max_length=10,
                        choices=CrimeSeverity.choices,
                        default=CrimeSeverity.MEDIUM
                      )
    status          = models.CharField(
                        max_length=30,
                        choices=CrimeStatus.choices,
                        default=CrimeStatus.REPORTED
                      )

    # ── Crime description ────────────────────────────────────
    description     = models.TextField()
    weapons_used    = models.CharField(max_length=200, blank=True)
    modus_operandi  = models.TextField(blank=True)     # how crime was committed

    # ── Location ─────────────────────────────────────────────
    location        = models.CharField(max_length=255)  # human readable address
    district        = models.CharField(max_length=100)
    latitude        = models.DecimalField(
                        max_digits=9,
                        decimal_places=6,
                        null=True,
                        blank=True
                      )
    longitude       = models.DecimalField(
                        max_digits=9,
                        decimal_places=6,
                        null=True,
                        blank=True
                      )

    # ── Date & Time ──────────────────────────────────────────
    date_occurred   = models.DateTimeField()
    date_reported   = models.DateTimeField(auto_now_add=True)
    date_updated    = models.DateTimeField(auto_now=True)

    # ── Victim info ──────────────────────────────────────────
    victim_count    = models.PositiveIntegerField(default=1)
    victim_details  = models.TextField(blank=True)

    # ── Evidence ─────────────────────────────────────────────
    evidence_notes  = models.TextField(blank=True)
    attachment      = models.FileField(
                        upload_to='crime_attachments/',
                        null=True,
                        blank=True
                      )

    # ── AI Analysis flag ─────────────────────────────────────
    is_analyzed     = models.BooleanField(default=False)

    class Meta:
        verbose_name        = 'Crime Report'
        verbose_name_plural = 'Crime Reports'
        ordering            = ['-date_reported']

    def __str__(self):
        return f"[{self.case_number}] {self.title} — {self.category}"

    def save(self, *args, **kwargs):
        # Auto-generate case number if not set
        if not self.case_number:
            last = CrimeReport.objects.order_by('-id').first()
            next_id = (last.id + 1) if last else 1
            self.case_number = f"UPF-CASE-{next_id:05d}"
        super().save(*args, **kwargs)


# ─────────────────────────────────────────────────────────────
# SUSPECT MODEL
# ─────────────────────────────────────────────────────────────
class Suspect(models.Model):

    crime_report    = models.ForeignKey(
                        CrimeReport,
                        on_delete=models.CASCADE,
                        related_name='suspects'
                      )

    # ── Personal info ────────────────────────────────────────
    name            = models.CharField(max_length=100, blank=True)  # may be unknown
    alias           = models.CharField(max_length=100, blank=True)
    age_estimate    = models.PositiveIntegerField(null=True, blank=True)
    gender          = models.CharField(
                        max_length=10,
                        choices=[
                            ('male',    'Male'),
                            ('female',  'Female'),
                            ('unknown', 'Unknown'),
                        ],
                        default='unknown'
                      )
    nationality     = models.CharField(max_length=50, blank=True)
    description     = models.TextField(blank=True)   # physical description

    # ── Relationship ─────────────────────────────────────────
    known_to_victim = models.BooleanField(default=False)
    is_arrested     = models.BooleanField(default=False)

    # ── Timestamps ───────────────────────────────────────────
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Suspect'
        verbose_name_plural = 'Suspects'

    def __str__(self):
        name = self.name or 'Unknown Suspect'
        return f"{name} — Case: {self.crime_report.case_number}"


# ─────────────────────────────────────────────────────────────
# WITNESS MODEL
# ──────────────────────────────────────────────────────────���──
class Witness(models.Model):

    crime_report    = models.ForeignKey(
                        CrimeReport,
                        on_delete=models.CASCADE,
                        related_name='witnesses'
                      )
    name            = models.CharField(max_length=100)
    contact         = models.CharField(max_length=50,  blank=True)
    statement       = models.TextField(blank=True)
    is_anonymous    = models.BooleanField(default=False)

    # ── Timestamps ───────────────────────────────────────────
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Witness'
        verbose_name_plural = 'Witnesses'

    def __str__(self):
        name = 'Anonymous' if self.is_anonymous else self.name
        return f"{name} — Case: {self.crime_report.case_number}"