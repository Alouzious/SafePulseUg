from rest_framework import serializers
from .models import AnalysisResult, AgentConversation, ConversationMessage


# ─────────────────────────────────────────────────────────────
# ANALYSIS RESULT SERIALIZER
# ─────────────────────────────────────────────────────────────
class AnalysisResultSerializer(serializers.ModelSerializer):

    requested_by_name   = serializers.SerializerMethodField()
    case_number         = serializers.SerializerMethodField()

    class Meta:
        model  = AnalysisResult
        fields = [
            'id',
            'requested_by_name',
            'case_number',
            'prompt',
            'ai_summary',
            'patterns_found',
            'hotspots',
            'trends',
            'recommendations',
            'risk_assessment',
            'status',
            'error_message',
            'created_at',
            'completed_at',
        ]

    def get_requested_by_name(self, obj):
        if obj.requested_by:
            return obj.requested_by.full_name
        return 'Unknown'

    def get_case_number(self, obj):
        if obj.crime_report:
            return obj.crime_report.case_number
        return None


# ─────────────────────────────────────────────────────────────
# CONVERSATION MESSAGE SERIALIZER
# ─────────────────────────────────────────────────────────────
class ConversationMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model  = ConversationMessage
        fields = ['id', 'role', 'content', 'created_at']


# ─────────────────────────────────────────────────────────────
# AGENT CONVERSATION SERIALIZER
# ─────────────────────────────────────────────────────────────
class AgentConversationSerializer(serializers.ModelSerializer):

    messages        = ConversationMessageSerializer(many=True, read_only=True)
    officer_name    = serializers.SerializerMethodField()

    class Meta:
        model  = AgentConversation
        fields = [
            'id',
            'session_id',
            'title',
            'is_active',
            'officer_name',
            'messages',
            'created_at',
            'updated_at',
        ]

    def get_officer_name(self, obj):
        return obj.officer.full_name