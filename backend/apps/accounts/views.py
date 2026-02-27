import logging
from rest_framework                         import status, generics
from rest_framework.response                import Response
from rest_framework.views                   import APIView
from rest_framework.permissions             import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens        import RefreshToken
from rest_framework_simplejwt.exceptions    import TokenError
from drf_spectacular.utils                  import extend_schema, OpenApiExample

from .models        import OfficerUser
from .serializers   import (
    RegisterSerializer,
    LoginSerializer,
    OfficerProfileSerializer,
    UpdateProfileSerializer,
    ChangePasswordSerializer,
)

logger = logging.getLogger('apps.accounts')


# ─────────────────────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────────────────────
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access':  str(refresh.access_token),
    }


# ─────────────────────────────────────────────────────────────
# REGISTER
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['🔐 Authentication'],
    summary='Register a new police officer',
    description='Creates a new officer account and returns JWT tokens.',
    examples=[
        OpenApiExample(
            'Register Example',
            value={
                'badge_number': 'UPF-002',
                'email':        'officer@safepulse.ug',
                'first_name':   'John',
                'last_name':    'Doe',
                'password':     'SecurePass123',
                'password2':    'SecurePass123',
                'rank':         'constable',
                'role':         'officer',
                'station':      'Kampala Central',
            },
            request_only=True,
        )
    ]
)
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user   = serializer.save()
            tokens = get_tokens_for_user(user)
            logger.info(f"New officer registered: {user.badge_number}")
            return Response({
                'message': 'Officer registered successfully.',
                'officer': OfficerProfileSerializer(user).data,
                'tokens':  tokens,
            }, status=status.HTTP_201_CREATED)
        logger.warning(f"Registration failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['🔐 Authentication'],
    summary='Officer login',
    description='Login with badge number and password. Returns JWT access and refresh tokens.',
    examples=[
        OpenApiExample(
            'Login Example',
            value={
                'badge_number': 'UPF-001',
                'password':     'SecurePass123',
            },
            request_only=True,
        )
    ]
)
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            user   = serializer.validated_data['user']
            tokens = get_tokens_for_user(user)
            logger.info(f"Officer logged in: {user.badge_number}")
            return Response({
                'message': 'Login successful.',
                'officer': OfficerProfileSerializer(user).data,
                'tokens':  tokens,
            }, status=status.HTTP_200_OK)
        logger.warning(f"Login failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['🔐 Authentication'],
    summary='Officer logout',
    description='Blacklists the refresh token to invalidate the session.',
    examples=[
        OpenApiExample(
            'Logout Example',
            value={'refresh': 'your-refresh-token-here'},
            request_only=True,
        )
    ]
)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info(f"Officer logged out: {request.user.badge_number}")
            return Response(
                {'message': 'Logged out successfully.'},
                status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {'error': 'Invalid or expired token.'},
                status=status.HTTP_400_BAD_REQUEST
            )


# ─────────────────────────────────────────────────────────────
# PROFILE
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['🔐 Authentication'],
    summary='Get or update officer profile',
    description='GET returns current officer profile. PUT updates it.',
)
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = OfficerProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Profile updated: {request.user.badge_number}")
            return Response({
                'message': 'Profile updated successfully.',
                'officer': OfficerProfileSerializer(request.user).data,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────────────────────
# CHANGE PASSWORD
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['🔐 Authentication'],
    summary='Change officer password',
    description='Requires old password and new password confirmation.',
)
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Password changed: {request.user.badge_number}")
            return Response(
                {'message': 'Password changed successfully.'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────────────────────
# OFFICER LIST
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['🔐 Authentication'],
    summary='List all officers',
    description='Admin sees all officers. Regular officer sees only themselves.',
)
class OfficerListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = OfficerProfileSerializer

    def get_queryset(self):
        if self.request.user.is_admin:
            return OfficerUser.objects.all()
        return OfficerUser.objects.filter(id=self.request.user.id)