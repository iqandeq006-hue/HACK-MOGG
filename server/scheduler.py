import random
import string
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict

def generate_google_meet_code() -> str:
    """
    Generates a realistic Google Meet code format: abc-defg-hij
    """
    p1 = ''.join(random.choices(string.ascii_lowercase, k=3))
    p2 = ''.join(random.choices(string.ascii_lowercase, k=4))
    p3 = ''.join(random.choices(string.ascii_lowercase, k=3))
    return f"{p1}-{p2}-{p3}"

def create_google_meet_session(topic: str, teacher_name: str, learner_name: str, start_time: datetime = None, duration_minutes: int = 45) -> Dict:
    """
    Creates Google Meet URL and a 1-click Google Calendar invitation link.
    """
    if start_time is None:
        start_time = datetime.utcnow() + timedelta(hours=2)

    end_time = start_time + timedelta(minutes=duration_minutes)
    meet_code = generate_google_meet_code()
    meet_url = f"https://meet.google.com/{meet_code}"

    # Format dates for Google Calendar URL (YYYYMMDDTHHMMSSZ)
    fmt = "%Y%m%dT%H%M%SZ"
    start_str = start_time.strftime(fmt)
    end_str = end_time.strftime(fmt)

    title = f"SkillSwap Session: {topic} ({teacher_name} & {learner_name})"
    details = (
        f"SkillSwap Peer Learning Session\n"
        f"Topic: {topic}\n"
        f"Teacher: {teacher_name}\n"
        f"Learner: {learner_name}\n"
        f"Google Meet Link: {meet_url}\n\n"
        f"Exchange verified via SkillSwap Ledger."
    )

    calendar_params = {
        "action": "TEMPLATE",
        "text": title,
        "dates": f"{start_str}/{end_str}",
        "details": details,
        "location": meet_url
    }
    calendar_url = f"https://calendar.google.com/calendar/render?{urllib.parse.urlencode(calendar_params)}"

    return {
        "meet_code": meet_code,
        "meet_url": meet_url,
        "scheduled_time": start_time.isoformat(),
        "duration_minutes": duration_minutes,
        "calendar_url": calendar_url
    }
