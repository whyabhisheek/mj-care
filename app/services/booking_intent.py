from datetime import date

from pydantic import BaseModel, Field

from app.services.gemini import GeminiServiceError, _generate_json_text


class BookingIntent(BaseModel):
    wants_booking: bool = False
    patient_name: str | None = None
    phone: str | None = None
    doctor_name: str | None = None
    doctor_id: int | None = None
    appointment_date: date | None = Field(default=None, alias="date")
    slot: str | None = None
    needs_more_info: bool = False
    missing_fields: list[str] = []
    reply: str = ""


def extract_booking_intent(message: str, history: list | None = None) -> BookingIntent:
    conversation_block = ""
    if history:
        conversation_lines = []
        for entry in history:
            role_label = "User" if entry.role == "user" else "Assistant"
            conversation_lines.append(f"{role_label}: {entry.content}")
        conversation_block = "\n".join(conversation_lines)

    history_section = f"""
Conversation so far:
{conversation_block}
""" if conversation_block else ""

    prompt = f"""
You are extracting appointment booking details for a hospital assistant.

Return only valid JSON with these keys:
- wants_booking: boolean
- patient_name: string or null
- phone: string or null
- doctor_name: string or null
- doctor_id: number or null
- date: string in YYYY-MM-DD format or null
- slot: string or null
- needs_more_info: boolean
- missing_fields: array of strings
- reply: string

Rules:
- Set wants_booking true if the user is trying to book an appointment.
- If the user is not booking, set wants_booking false and reply with a helpful message.
- If critical booking fields are missing, set needs_more_info true and list missing_fields.
- Never invent phone numbers or patient names.

{history_section}
User message:
{message}
""".strip()

    try:
        text = _generate_json_text(prompt)
        data = BookingIntent.model_validate_json(text)
    except Exception as exc:
        raise GeminiServiceError("Could not understand booking request") from exc

    return data
