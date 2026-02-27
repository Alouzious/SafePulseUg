from django.contrib import admin
from .models import AnalysisResult, AgentConversation, ConversationMessage


class ConversationMessageInline(admin.TabularInline):
    model       = ConversationMessage
    extra       = 0
    readonly_fields = ['role', 'content', 'created_at']


@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display    = ['id', 'requested_by', 'crime_report', 'status', 'created_at']
    list_filter     = ['status']
    readonly_fields = ['created_at', 'completed_at']
    search_fields   = ['prompt', 'ai_summary']


@admin.register(AgentConversation)
class AgentConversationAdmin(admin.ModelAdmin):
    list_display    = ['session_id', 'officer', 'title', 'is_active', 'created_at']
    inlines         = [ConversationMessageInline]
    readonly_fields = ['session_id', 'created_at', 'updated_at']