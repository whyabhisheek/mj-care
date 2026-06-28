import smtplib
from email.message import EmailMessage

from app.config import get_settings


def send_booking_confirmation_email(*, to_email: str, patient_name: str, doctor_name: str, date: str, slot: str) -> None:
    settings = get_settings()
    if not settings.email_host or not settings.email_username or not settings.email_app_password:
        return

    from_email = settings.email_from or settings.email_username
    message = EmailMessage()
    message["Subject"] = "MJ Care appointment confirmed"
    message["From"] = from_email
    message["To"] = to_email
    message.set_content(
        f"""Hello {patient_name},

Your appointment has been confirmed.

Doctor: {doctor_name}
Date: {date}
Slot: {slot}

Thank you,
MJ Care
"""
    )

    with smtplib.SMTP(settings.email_host, settings.email_port, timeout=10) as smtp:
        if settings.email_use_tls:
            smtp.starttls()
        smtp.login(settings.email_username, settings.email_app_password)
        smtp.send_message(message)
