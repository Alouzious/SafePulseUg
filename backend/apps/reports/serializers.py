from rest_framework import serializers
from .models        import GeneratedReport


class GeneratedReportSerializer(serializers.ModelSerializer):

    generated_by_name = serializers.SerializerMethodField()

    class Meta:
        model  = GeneratedReport
        fields = [
            'id',
            'title',
            'report_type',
            'report_format',
            'file',
            'parameters',
            'generated_by_name',
            'created_at',
        ]

    def get_generated_by_name(self, obj):
        if obj.generated_by:
            return obj.generated_by.full_name
        return 'Unknown'