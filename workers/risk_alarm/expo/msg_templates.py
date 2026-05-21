"""
workers/risk/expo/msg_templates.py

Push notification message templates for visa and TOPIK risk alerts.
VISA_TEMPLATES key 2 uses {days_left} — inject via .format(days_left=...) at render time.
"""

VISA_TEMPLATES: dict[int, str] = {
    1: "Your visa expiry is more than 90 days away. Renewal preparation begins at D-40.",
    2: "Your visa expires in {days_left} days. Contact the International Student Support Office soon.",
    3: "School office processing deadline is approaching. Submit your documents now.",
    4: "School office deadline has passed. Book an appointment at the Immigration Office immediately.",
    5: "URGENT: Contact the Immigration Office or International Student Support Office right now.",
}

TOPIK_TEMPLATES: dict[int, str] = {
    1: "TOPIK Level 3+ is required for D-2 Visa admission. Check the upcoming exam schedule.",
    2: "You need to register for TOPIK soon. Exam registration may close shortly.",
    3: "URGENT: Register for TOPIK immediately, or contact the Ajou International Student Office.",
}
