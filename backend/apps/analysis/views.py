import logging
import uuid
from django.utils               import timezone
from rest_framework             import status
from rest_framework.views       import APIView
from rest_framework.response    import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils      import extend_schema, OpenApiExample

from apps.crimes.models         import CrimeReport
from .models                    import AnalysisResult, AgentConversation, ConversationMessage, AnalysisStatus
from .serializers               import AnalysisResultSerializer, AgentConversationSerializer
from .agent                     import run_agent, run_agent_with_history
from .prompts                   import SINGLE_REPORT_PROMPT, GENERAL_ANALYSIS_PROMPT

logger = logging.getLogger('apps.analysis')


# ─────────────────────────────────────────────────────────────
# ANALYZE SINGLE REPORT
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['🤖 AI Analysis'],
    summary='Analyze a specific crime report with AI',
    description='Triggers the Gemini AI agent to deeply analyze a crime report and compare with historical data.',
    examples=[
        OpenApiExample(
            'Analyze Report Example',
            value={'case_number': 'UPF-CASE-00001'},
            request_only=True,
        )
    ]
)
class AnalyzeCrimeReportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        case_number = request.data.get('case_number')
        if not case_number:
            return Response(
                {'error': 'case_number is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            report = CrimeReport.objects.get(case_number=case_number)
        except CrimeReport.DoesNotExist:
            return Response(
                {'error': f'Crime report {case_number} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        suspects_summary = ""
        for s in report.suspects.all():
            suspects_summary += (
                f"{s.name or 'Unknown'} "
                f"(Age: {s.age_estimate or 'Unknown'}, Gender: {s.gender}), "
            )

        prompt = SINGLE_REPORT_PROMPT.format(
            case_number    = report.case_number,
            title          = report.title,
            category       = report.category,
            severity       = report.severity,
            location       = report.location,
            district       = report.district,
            date_occurred  = report.date_occurred.strftime('%Y-%m-%d %H:%M'),
            description    = report.description,
            weapons_used   = report.weapons_used   or 'None reported',
            modus_operandi = report.modus_operandi or 'Not provided',
            victim_count   = report.victim_count,
            suspects       = suspects_summary      or 'No suspects recorded',
        )

        analysis = AnalysisResult.objects.create(
            requested_by = request.user,
            crime_report = report,
            prompt       = prompt,
            status       = AnalysisStatus.PROCESSING,
        )

        result = run_agent(prompt)

        if result['success']:
            analysis.ai_summary   = result['response']
            analysis.status       = AnalysisStatus.COMPLETED
            analysis.completed_at = timezone.now()
            analysis.save()
            report.is_analyzed = True
            report.save()
            logger.info(f"Analysis completed for {case_number}")
            return Response({
                'message':  'Analysis completed successfully.',
                'analysis': AnalysisResultSerializer(analysis).data,
            }, status=status.HTTP_200_OK)
        else:
            analysis.status        = AnalysisStatus.FAILED
            analysis.error_message = result['error']
            analysis.save()
            return Response({
                'error':   'Analysis failed.',
                'details': result['error'],
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─────────────────────────────────────────────────────────────
# GENERAL ANALYSIS
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['🤖 AI Analysis'],
    summary='Run a general analysis on all crime data',
    description='AI agent analyzes all crime data and returns patterns, hotspots, trends and recommendations.',
    examples=[
        OpenApiExample(
            'Custom Prompt Example',
            value={'prompt': 'What are the most dangerous areas in Kampala this month?'},
            request_only=True,
        )
    ]
)
class GeneralAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        custom_prompt = request.data.get('prompt', GENERAL_ANALYSIS_PROMPT)
        analysis = AnalysisResult.objects.create(
            requested_by = request.user,
            prompt       = custom_prompt,
            status       = AnalysisStatus.PROCESSING,
        )
        result = run_agent(custom_prompt)
        if result['success']:
            analysis.ai_summary   = result['response']
            analysis.status       = AnalysisStatus.COMPLETED
            analysis.completed_at = timezone.now()
            analysis.save()
            return Response({
                'message':  'General analysis completed.',
                'analysis': AnalysisResultSerializer(analysis).data,
            }, status=status.HTTP_200_OK)
        else:
            analysis.status        = AnalysisStatus.FAILED
            analysis.error_message = result['error']
            analysis.save()
            return Response({
                'error':   'Analysis failed.',
                'details': result['error'],
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─────────────────────────────────────────────────────────────
# CHAT WITH AGENT
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['🤖 AI Analysis'],
    summary='Chat with the AI agent',
    description=(
        'Send a message to the Gemini AI agent. '
        'Supports full conversation history via session_id. '
        'Leave session_id empty to start a new conversation.'
    ),
    examples=[
        OpenApiExample(
            'New Chat Example',
            value={'message': 'What are the most common crimes in Kampala?'},
            request_only=True,
        ),
        OpenApiExample(
            'Continue Chat Example',
            value={
                'message':    'Which district has the most robberies?',
                'session_id': 'your-session-uuid-here',
            },
            request_only=True,
        ),
    ]
)
class AgentChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        message    = request.data.get('message')
        session_id = request.data.get('session_id')

        if not message:
            return Response(
                {'error': 'message is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if session_id:
            try:
                conversation = AgentConversation.objects.get(
                    session_id=session_id,
                    officer=request.user
                )
            except AgentConversation.DoesNotExist:
                return Response(
                    {'error': 'Conversation not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            conversation = AgentConversation.objects.create(
                officer    = request.user,
                session_id = str(uuid.uuid4()),
                title      = message[:80],
            )

        history = [
            {'role': msg.role, 'content': msg.content}
            for msg in conversation.messages.all()
        ]

        ConversationMessage.objects.create(
            conversation = conversation,
            role         = ConversationMessage.Role.USER,
            content      = message,
        )

        result = run_agent_with_history(message, history)

        if result['success']:
            ConversationMessage.objects.create(
                conversation = conversation,
                role         = ConversationMessage.Role.ASSISTANT,
                content      = result['response'],
            )
            return Response({
                'session_id': conversation.session_id,
                'message':    message,
                'response':   result['response'],
            }, status=status.HTTP_200_OK)

        return Response({
            'error':   'Agent failed to respond.',
            'details': result['error'],
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        tags=['🤖 AI Analysis'],
        summary='Get full conversation history by session ID',
    )
    def get(self, request, session_id):
        try:
            conversation = AgentConversation.objects.get(
                session_id=session_id,
                officer=request.user
            )
            serializer = AgentConversationSerializer(conversation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except AgentConversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


# ─────────────────────────────────────────────────────────────
# ANALYSIS RESULTS LIST
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['🤖 AI Analysis'],
    summary='List all analysis results for the logged-in officer',
)
class AnalysisResultsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        results    = AnalysisResult.objects.filter(
            requested_by=request.user
        ).order_by('-created_at')
        serializer = AnalysisResultSerializer(results, many=True)
        return Response({
            'count':   results.count(),
            'results': serializer.data,
        }, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────
# ANALYSIS RESULT DETAIL
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['🤖 AI Analysis'],
    summary='Get a single analysis result by ID',
)
class AnalysisResultDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            result     = AnalysisResult.objects.get(pk=pk, requested_by=request.user)
            serializer = AnalysisResultSerializer(result)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except AnalysisResult.DoesNotExist:
            return Response(
                {'error': 'Analysis result not found.'},
                status=status.HTTP_404_NOT_FOUND
            )