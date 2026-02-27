import logging
from datetime                   import datetime, timedelta
from django.utils               import timezone
from langchain_core.tools       import tool          # ← updated import

logger = logging.getLogger('apps.analysis')


# ─────────────────────────────────────────────────────────────
# TOOL 1 — Get All Crimes
# ─────────────────────────────────────────────────────────────
@tool
def get_all_crimes(limit: int = 50) -> str:
    """
    Fetch all crime reports from the database.
    Returns a formatted summary of crime reports.
    Use limit to control how many records to retrieve (default 50).
    """
    try:
        from apps.crimes.models import CrimeReport
        reports = CrimeReport.objects.all().order_by('-date_reported')[:limit]
        if not reports:
            return "No crime reports found in the database."
        result = f"Found {reports.count()} crime reports:\n\n"
        for r in reports:
            result += (
                f"- Case: {r.case_number} | {r.title} | "
                f"Category: {r.category} | Severity: {r.severity} | "
                f"Status: {r.status} | District: {r.district} | "
                f"Date: {r.date_occurred.strftime('%Y-%m-%d')}\n"
            )
        return result
    except Exception as e:
        logger.error(f"get_all_crimes error: {e}")
        return f"Error retrieving crimes: {str(e)}"


# ─────────────────────────────────────────────────────────────
# TOOL 2 — Get Crimes by Category
# ─────────────────────────────────────────────────────────────
@tool
def get_crimes_by_category(category: str) -> str:
    """
    Fetch crime reports filtered by category.
    Categories: theft, assault, homicide, fraud, cybercrime,
    robbery, burglary, drug_offense, sexual_offense,
    vandalism, kidnapping, arson, corruption, other
    """
    try:
        from apps.crimes.models import CrimeReport
        reports = CrimeReport.objects.filter(
            category__iexact=category
        ).order_by('-date_reported')
        if not reports.exists():
            return f"No crime reports found for category: {category}"
        result = f"Found {reports.count()} {category} cases:\n\n"
        for r in reports:
            result += (
                f"- Case: {r.case_number} | {r.title} | "
                f"Severity: {r.severity} | Status: {r.status} | "
                f"Location: {r.location}, {r.district} | "
                f"Date: {r.date_occurred.strftime('%Y-%m-%d')}\n"
                f"  Description: {r.description[:150]}...\n"
            )
        return result
    except Exception as e:
        logger.error(f"get_crimes_by_category error: {e}")
        return f"Error retrieving crimes by category: {str(e)}"


# ─────────────────────────────────────────────────────────────
# TOOL 3 — Get Crimes by District
# ─────────────────────────────────────────────────────────────
@tool
def get_crimes_by_district(district: str) -> str:
    """
    Fetch all crime reports from a specific district or location.
    Example: 'Kampala', 'Wakiso', 'Mukono'
    """
    try:
        from apps.crimes.models import CrimeReport
        reports = CrimeReport.objects.filter(
            district__icontains=district
        ).order_by('-date_reported')
        if not reports.exists():
            return f"No crime reports found for district: {district}"
        result = f"Found {reports.count()} crimes in {district}:\n\n"
        for r in reports:
            result += (
                f"- Case: {r.case_number} | {r.title} | "
                f"Category: {r.category} | Severity: {r.severity} | "
                f"Status: {r.status} | "
                f"Date: {r.date_occurred.strftime('%Y-%m-%d')}\n"
            )
        return result
    except Exception as e:
        logger.error(f"get_crimes_by_district error: {e}")
        return f"Error retrieving crimes by district: {str(e)}"


# ─────────────────────────────────────────────────────────────
# TOOL 4 — Get Crimes by Status
# ─────────────────────────────────────────────────────────────
@tool
def get_crimes_by_status(crime_status: str) -> str:
    """
    Fetch crime reports by their investigation status.
    Statuses: reported, under_investigation, solved, closed, cold_case
    """
    try:
        from apps.crimes.models import CrimeReport
        reports = CrimeReport.objects.filter(
            status__iexact=crime_status
        ).order_by('-date_reported')
        if not reports.exists():
            return f"No crime reports found with status: {crime_status}"
        result = f"Found {reports.count()} cases with status '{crime_status}':\n\n"
        for r in reports:
            result += (
                f"- Case: {r.case_number} | {r.title} | "
                f"Category: {r.category} | Severity: {r.severity} | "
                f"District: {r.district} | "
                f"Date: {r.date_occurred.strftime('%Y-%m-%d')}\n"
            )
        return result
    except Exception as e:
        logger.error(f"get_crimes_by_status error: {e}")
        return f"Error retrieving crimes by status: {str(e)}"


# ─────────────────────────────────────────────────────────────
# TOOL 5 — Get Recent Crimes
# ─────────────────────────────────────────────────────────────
@tool
def get_recent_crimes(days: int = 7) -> str:
    """
    Fetch crime reports from the last N days.
    Default is last 7 days. Use days=30 for last month.
    """
    try:
        from apps.crimes.models import CrimeReport
        since   = timezone.now() - timedelta(days=days)
        reports = CrimeReport.objects.filter(
            date_reported__gte=since
        ).order_by('-date_reported')
        if not reports.exists():
            return f"No crime reports found in the last {days} days."
        result = f"Found {reports.count()} crimes in the last {days} days:\n\n"
        for r in reports:
            result += (
                f"- Case: {r.case_number} | {r.title} | "
                f"Category: {r.category} | Severity: {r.severity} | "
                f"District: {r.district} | "
                f"Date: {r.date_occurred.strftime('%Y-%m-%d %H:%M')}\n"
            )
        return result
    except Exception as e:
        logger.error(f"get_recent_crimes error: {e}")
        return f"Error retrieving recent crimes: {str(e)}"


# ─────────────────────────────────────────────────────────────
# TOOL 6 — Get Crime Summary Stats
# ─────────────────────────────────────────────────────────────
@tool
def get_crime_summary_stats(placeholder: str = "") -> str:
    """
    Get overall crime statistics including totals by category,
    status, severity, and district. Use this for overview analysis.
    """
    try:
        from apps.crimes.models import CrimeReport
        from django.db.models   import Count

        total = CrimeReport.objects.count()
        if total == 0:
            return "No crime reports in the database yet."

        by_category = CrimeReport.objects.values('category').annotate(
                        count=Count('id')).order_by('-count')
        by_status   = CrimeReport.objects.values('status').annotate(
                        count=Count('id')).order_by('-count')
        by_severity = CrimeReport.objects.values('severity').annotate(
                        count=Count('id')).order_by('-count')
        by_district = CrimeReport.objects.values('district').annotate(
                        count=Count('id')).order_by('-count')[:10]

        result  = f"=== CRIME SUMMARY STATISTICS ===\n"
        result += f"Total Crime Reports: {total}\n\n"

        result += "BY CATEGORY:\n"
        for item in by_category:
            result += f"  - {item['category']}: {item['count']} cases\n"

        result += "\nBY STATUS:\n"
        for item in by_status:
            result += f"  - {item['status']}: {item['count']} cases\n"

        result += "\nBY SEVERITY:\n"
        for item in by_severity:
            result += f"  - {item['severity']}: {item['count']} cases\n"

        result += "\nTOP DISTRICTS:\n"
        for item in by_district:
            result += f"  - {item['district']}: {item['count']} cases\n"

        return result
    except Exception as e:
        logger.error(f"get_crime_summary_stats error: {e}")
        return f"Error retrieving stats: {str(e)}"


# ─────────────────────────────────────────────────────────────
# TOOL 7 — Get Single Crime Details
# ─────────────────────────────────────────────────────────────
@tool
def get_single_crime(case_number: str) -> str:
    """
    Get full details of a specific crime report by its case number.
    Example case number format: UPF-CASE-00001
    """
    try:
        from apps.crimes.models import CrimeReport

        report    = CrimeReport.objects.get(case_number=case_number)
        suspects  = report.suspects.all()
        witnesses = report.witnesses.all()

        result  = f"=== CRIME REPORT DETAILS ===\n"
        result += f"Case Number   : {report.case_number}\n"
        result += f"Title         : {report.title}\n"
        result += f"Category      : {report.category}\n"
        result += f"Severity      : {report.severity}\n"
        result += f"Status        : {report.status}\n"
        result += f"Location      : {report.location}, {report.district}\n"
        result += f"Date Occurred : {report.date_occurred.strftime('%Y-%m-%d %H:%M')}\n"
        result += f"Date Reported : {report.date_reported.strftime('%Y-%m-%d %H:%M')}\n"
        result += f"Victim Count  : {report.victim_count}\n"
        result += f"Victim Info   : {report.victim_details or 'Not provided'}\n"
        result += f"Description   : {report.description}\n"
        result += f"Weapons Used  : {report.weapons_used  or 'None reported'}\n"
        result += f"Modus Operandi: {report.modus_operandi or 'Not provided'}\n"
        result += f"Evidence      : {report.evidence_notes or 'None'}\n"

        if suspects.exists():
            result += f"\nSUSPECTS ({suspects.count()}):\n"
            for s in suspects:
                result += (
                    f"  - {s.name or 'Unknown'} | "
                    f"Age: {s.age_estimate or 'Unknown'} | "
                    f"Gender: {s.gender} | "
                    f"Arrested: {s.is_arrested}\n"
                    f"    Description: {s.description}\n"
                )

        if witnesses.exists():
            result += f"\nWITNESSES ({witnesses.count()}):\n"
            for w in witnesses:
                name = 'Anonymous' if w.is_anonymous else w.name
                result += f"  - {name}: {w.statement[:100]}\n"

        return result

    except CrimeReport.DoesNotExist:
        return f"No crime report found with case number: {case_number}"
    except Exception as e:
        logger.error(f"get_single_crime error: {e}")
        return f"Error retrieving crime: {str(e)}"


# ─────────────────────────────────────────────────────────────
# EXPORT ALL TOOLS
# ─────────────────────────────────────────────────────────────
ALL_TOOLS = [
    get_all_crimes,
    get_crimes_by_category,
    get_crimes_by_district,
    get_crimes_by_status,
    get_recent_crimes,
    get_crime_summary_stats,
    get_single_crime,
]