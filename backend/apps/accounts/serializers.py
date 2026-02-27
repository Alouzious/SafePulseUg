from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import OfficerUser, OfficerRole, OfficerRank


# ─────────────────────────────────────────────────────────────
# REGISTER SERIALIZER
# ─────────────────────────────────────────────────────────────
class RegisterSerializer(serializers.ModelSerializer):

    password  = serializers.CharField(
                    write_only=True,
                    required=True,
                    validators=[validate_password]
                )
    password2 = serializers.CharField(
                    write_only=True,
                    required=True,
                    label='Confirm Password'
                )

    class Meta:
        model  = OfficerUser
        fields = [
            'badge_number',
            'email',
            'first_name',
            'last_name',
            'password',
            'password2',
            'role',
            'rank',
            'station',
            'district',
            'phone_number',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user     = OfficerUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


# ─────────────────────────────────────────────────────────────
# LOGIN SERIALIZER
# ─────────────────────────────────────────────────────────────
class LoginSerializer(serializers.Serializer):

    badge_number = serializers.CharField()
    password     = serializers.CharField(write_only=True)

    def validate(self, attrs):
        badge_number = attrs.get('badge_number')
        password     = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=badge_number,
            password=password
        )

        if not user:
            raise serializers.ValidationError('Invalid badge number or password.')

        if not user.is_active:
            raise serializers.ValidationError('This account has been deactivated.')

        attrs['user'] = user
        return attrs


# ─────────────────────────────────────────────────────────────
# OFFICER PROFILE SERIALIZER (Read)
# ─────────────────────────────────────────────────────────────
class OfficerProfileSerializer(serializers.ModelSerializer):

    full_name = serializers.ReadOnlyField()

    class Meta:
        model  = OfficerUser
        fields = [
            'id',
            'badge_number',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'role',
            'rank',
            'station',
            'district',
            'phone_number',
            'profile_photo',
            'is_verified',
            'date_joined',
            'last_updated',
        ]
        read_only_fields = [
            'id',
            'badge_number',
            'is_verified',
            'date_joined',
            'last_updated',
        ]


# ─────────────────────────────────────────────────────────────
# UPDATE PROFILE SERIALIZER
# ─────────────────────────────────────────────────────────────
class UpdateProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model  = OfficerUser
        fields = [
            'first_name',
            'last_name',
            'email',
            'station',
            'district',
            'phone_number',
            'profile_photo',
        ]


# ─────────────────────────────────────────────────────────────
# CHANGE PASSWORD SERIALIZER
# ─────────────────────────────────────────────────────────────
class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(
                        write_only=True,
                        required=True,
                        validators=[validate_password]
                    )
    new_password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password': 'New passwords do not match.'})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user