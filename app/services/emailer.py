import logging
import smtplib
from email.message import EmailMessage

from app.config import get_settings


logger = logging.getLogger(__name__)


def send_booking_confirmation_email(*, to_email: str, patient_name: str, doctor_name: str, date: str, slot: str) -> None:
    settings = get_settings()
    if not settings.email_host or not settings.email_username or not settings.email_app_password:
        logger.warning("Email not sent: missing SMTP config (EMAIL_HOST=%s, EMAIL_USERNAME=%s, EMAIL_APP_PASSWORD=%s)",
                       bool(settings.email_host), bool(settings.email_username), bool(settings.email_app_password))
        return

    from_email = settings.email_from or settings.email_username

    html = f"""\
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#f4f7fb;font-family:Inter,-apple-system,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f7fb;padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="520" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:16px;box-shadow:0 4px 24px rgba(0,0,0,0.06);overflow:hidden;">
          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#14395b,#0f87d8);padding:32px 40px 28px;text-align:center;">
              <h1 style="margin:0;font-size:22px;font-weight:700;color:#ffffff;letter-spacing:0.5px;">&#x2714; Appointment Confirmed</h1>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:36px 40px 32px;">
              <p style="margin:0 0 6px;font-size:15px;color:#1e293b;">Dear <strong style="color:#0f87d8;">{patient_name}</strong>,</p>
              <p style="margin:0 0 24px;font-size:14px;color:#475569;line-height:1.6;">
                Your appointment has been successfully confirmed. Please find the details below.
              </p>

              <!-- Details Card -->
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc;border-radius:12px;border:1px solid #e2e8f0;margin-bottom:28px;">
                <tr>
                  <td style="padding:20px 24px;">
                    <table width="100%" cellpadding="0" cellspacing="0">
                      <tr>
                        <td style="padding:6px 0;font-size:13px;font-weight:600;color:#64748b;width:90px;">Doctor</td>
                        <td style="padding:6px 0;font-size:14px;color:#1e293b;">{doctor_name}</td>
                      </tr>
                      <tr>
                        <td style="padding:6px 0;font-size:13px;font-weight:600;color:#64748b;">Date</td>
                        <td style="padding:6px 0;font-size:14px;color:#1e293b;">{date}</td>
                      </tr>
                      <tr>
                        <td style="padding:6px 0;font-size:13px;font-weight:600;color:#64748b;">Time</td>
                        <td style="padding:6px 0;font-size:14px;color:#1e293b;">{slot}</td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>

              <p style="margin:0 0 4px;font-size:13px;color:#64748b;">
                Need to reschedule? Contact the hospital directly.
              </p>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="background:#f8fafc;padding:18px 40px;text-align:center;border-top:1px solid #e2e8f0;">
              <p style="margin:0;font-size:13px;font-weight:600;color:#14395b;">MJ Care</p>
              <p style="margin:2px 0 0;font-size:11px;color:#94a3b8;">Wellness Hospital</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    message = EmailMessage()
    message["Subject"] = "MJ Care - Appointment Confirmed"
    message["From"] = from_email
    message["To"] = to_email
    message.set_content(
        f"Dear {patient_name},\n\nYour appointment has been confirmed.\n\nDoctor: {doctor_name}\nDate: {date}\nTime: {slot}\n\nThank you,\nMJ Care"
    )
    message.add_alternative(html, subtype="html")

    try:
        with smtplib.SMTP(settings.email_host, settings.email_port, timeout=30) as smtp:
            if settings.email_use_tls:
                smtp.starttls()
            smtp.login(settings.email_username, settings.email_app_password)
            smtp.send_message(message)
        logger.info("Email sent successfully to %s", to_email)
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to_email, exc)
