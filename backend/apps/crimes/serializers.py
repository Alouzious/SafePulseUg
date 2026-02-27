from rest_framework import serializers
from .models import CrimeReport, Suspect, Witness


# ─────────────────────────────────────────────────────────────
# SUSPECT SERIALIZER
# ─────────────────────────────────────────────────────────────
class SuspectSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Suspect
        fields = [
            'id',
            'name',
            'alias',
            'age_estimate',
            'gender',
            'nationality',
            'description',
            'known_to_victim',
            'is_arrested',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ─────────────────────────────────────────────────────────────
# WITNESS SERIALIZER
# ─────────────────────────────────────────────────────────────
class WitnessSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Witness
        fields = [
            'id',
            'name',
            'contact',
            'statement',
            'is_anonymous',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


# ─────────────────────────────────────────────────────────────
# CRIME REPORT — LIST SERIALIZER (lightweight)
# ─────────────────────────────────────────────────────────────
class CrimeReportListSerializer(serializers.ModelSerializer):

    reported_by_name = serializers.SerializerMethodField()

    class Meta:
        model  = CrimeReport
        fields = [
            'id',
            'case_number',
            'title',
            'category',
            'severity',
            'status',
            'location',
            'district',
            'date_occurred',
            'date_reported',
            'victim_count',
            'is_analyzed',
            'reported_by_name',
        ]

    def get_reported_by_name(self, obj):
        if obj.reported_by:
            return obj.reported_by.full_name
        return 'Unknown'


# ──────────────��──────────────────────────────────────────────
# CRIME REPORT — DETAIL SERIALIZER (full data)
# ─────────────────────────────────────────────────────────────
class CrimeReportDetailSerializer(serializers.ModelSerializer):

    suspects         = SuspectSerializer(many=True, read_only=True)
    witnesses        = WitnessSerializer(many=True, read_only=True)
    reported_by_name = serializers.SerializerMethodField()

    class Meta:
        model  = CrimeReport
        fields = [
            'id',
            'case_number',
            'reported_by',
            'reported_by_name',
            'title',
            'category',
            'severity',
            'status',
            'description',
            'weapons_used',
            'modus_operandi',
            'location',
            'district',
            'latitude',
            'longitude',
            'date_occurred',
            'date_reported',
            'date_updated',
            'victim_count',
            'victim_details',
            'evidence_notes',
            'attachment',
            'is_analyzed',
            'suspects',
            'witnesses',
        ]
        read_only_fields = [
            'id',
            'case_number',
            'reported_by',
            'date_reported',
            'date_updated',
            'is_analyzed',
        ]

    def get_reported_by_name(self, obj):
        if obj.reported_by:
            return obj.reported_by.full_name
        return 'Unknown'


# ─────────────────────────────────────────────────────────────
# CRIME REPORT — CREATE SERIALIZER
# ─────────────────────────────────────────────────────────────
class CrimeReportCreateSerializer(serializers.ModelSerializer):

    suspects  = SuspectSerializer(many=True, required=False)
    witnesses = WitnessSerializer(many=True, required=False)

    class Meta:
        model  = CrimeReport
        fields = [
            'title',
            'category',
            'severity',
            'description',
            'weapons_used',
            'modus_operandi',
            'location',
            'district',
            'latitude',
            'longitude',
            'date_occurred',
            'victim_count',
            'victim_details',
            'evidence_notes',
            'attachment',
            'suspects',
            'witnesses',
        ]

    def create(self, validated_data):
        # Extract nested data
        suspects_data  = validated_data.pop('suspects',  [])
        witnesses_data = validated_data.pop('witnesses', [])

        # Attach the logged-in officer
        validated_data['reported_by'] = self.context['request'].user

        # Create the crime report
        crime_report = CrimeReport.objects.create(**validated_data)

        # Create nested suspects
        for suspect_data in suspects_data:
            Suspect.objects.create(crime_report=crime_report, **suspect_data)

        # Create nested witnesses
        for witness_data in witnesses_data:
            Witness.objects.create(crime_report=crime_report, **witness_data)

        return crime_report


# ─────────────────────────────────────────────────────────────
# CRIME REPORT — UPDATE SERIALIZER
# ─────────────────────────────────────────────────────────────
class CrimeReportUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model  = CrimeReport
        fields = [
            'title',
            'category',
            'severity',
            'status',
            'description',
            'weapons_used',
            'modus_operandi',
            'location',
            'district',
            'latitude',
            'longitude',
            'date_occurred',
            'victim_count',
            'victim_details',
            'evidence_notes',
            'attachment',
        ]