from django.db import models
from django.conf import settings


# ─────────────────────────────────────────────────────────────
# ANALYSIS STATUS
# ─────────────────────────────────────────────────────────────
class AnalysisStatus(models.TextChoices):
    PENDING     = 'pending',    'Pending'
    PROCESSING  = 'processing', 'Processing'
    COMPLETED   = 'completed',  'Completed'
    FAILED      = 'failed',     'Failed'


# ─────────────────────────────────────────────────────────────
# ANALYSIS RESULT MODEL
# Stores results from AI agent analysis
# ─────────────────────────────────────────────────────────────
class AnalysisResult(models.Model):

    # ── Who triggered the analysis ───────────────────────────
    requested_by    = models.ForeignKey(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.SET_NULL,
                        null=True,
                        related_name='analysis_requests'
                      )

    # ── What was analyzed ────────────────────────────────────
    crime_report    = models.ForeignKey(
                        'crimes.CrimeReport',
                        on_delete=models.SET_NULL,
                        null=True,
                        blank=True,
                        related_name='analysis_results'
                      )

    # ── The prompt sent to the agent ─────────────────────────
    prompt          = models.TextField()

    # ── AI Agent response ────────────────────────────────────
    ai_summary          = models.TextField(blank=True)
    patterns_found      = models.TextField(blank=True)
    hotspots            = models.TextField(blank=True)
    trends              = models.TextField(blank=True)
    recommendations     = models.TextField(blank=True)
    risk_assessment     = models.TextField(blank=True)

    # ── Status ───────────────────────────────────────────────
    status          = models.CharField(
                        max_length=20,
                        choices=AnalysisStatus.choices,
                        default=AnalysisStatus.PENDING
                      )
    error_message   = models.TextField(blank=True)

    # ── Timestamps ───────────────────────────────────────────
    created_at      = models.DateTimeField(auto_now_add=True)
    completed_at    = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name        = 'Analysis Result'
        verbose_name_plural = 'Analysis Results'
        ordering            = ['-created_at']

    def __str__(self):
        case = self.crime_report.case_number if self.crime_report else 'General'
        return f"Analysis [{self.status}] — {case} — {self.created_at:%Y-%m-%d %H:%M}"


# ─────────────────────────────────────────────────────────────
# AGENT CONVERSATION MODEL
# Stores back-and-forth chat with the AI agent
# ─────────────────────────────────────────────────────────────
class AgentConversation(models.Model):

    officer         = models.ForeignKey(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                        related_name='conversations'
                      )
    session_id      = models.CharField(max_length=100, unique=True)
    title           = models.CharField(max_length=200, blank=True)
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Agent Conversation'
        verbose_name_plural = 'Agent Conversations'
        ordering            = ['-updated_at']

    def __str__(self):
        return f"Conversation [{self.session_id}] — {self.officer.full_name}"


# ─────────────────────────────────────────────────────────────
# CONVERSATION MESSAGE MODEL
# Individual messages in a conversation
# ─────────────────────────────────────────────────────────────
class ConversationMessage(models.Model):

    class Role(models.TextChoices):
        USER        = 'user',       'User'
        ASSISTANT   = 'assistant',  'Assistant'

    conversation    = models.ForeignKey(
                        AgentConversation,
                        on_delete=models.CASCADE,
                        related_name='messages'
                      )
    role            = models.CharField(
                        max_length=10,
                        choices=Role.choices
                      )
    content         = models.TextField()
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Message'
        ordering     = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:60]}..."