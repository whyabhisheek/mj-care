import json

import requests
from requests import RequestException

from app.config import get_settings


GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class GeminiServiceError(Exception):
    pass


def _generate_json_text(prompt: str) -> str:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise GeminiServiceError("GEMINI_API_KEY is not set. Configure it in backend/.env")
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
        },
    }

    try:
        response = requests.post(
            GEMINI_API_URL.format(model=GEMINI_MODEL),
            params={"key": settings.gemini_api_key},
            json=payload,
            timeout=30,
        )
    except RequestException as exc:
        raise GeminiServiceError("Gemini API request failed") from exc

    if response.status_code >= 400:
        raise GeminiServiceError("Gemini API request failed")

    try:
        data = response.json()
    except ValueError as exc:
        raise GeminiServiceError("Gemini API returned invalid JSON") from exc
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as exc:
        raise GeminiServiceError("Gemini API returned an unexpected response") from exc

    return text.strip()


def summarize_report(report_text: str) -> str:
    prompt = f"""
You are a medical assistant.

Explain report in simple language.
Mention abnormal values.
Never diagnose diseases.
Always suggest consulting doctor.

Return only valid JSON in this format:
{{"summary":"Vitamin D is lower than normal..."}}

Report text:
{report_text}
""".strip()

    text = _generate_json_text(prompt)

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return text

    summary = parsed.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        raise GeminiServiceError("Gemini API did not return a summary")

    return summary.strip()


def generate_chat_reply(message: str, history: list | None = None) -> str:
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
You are the MJ Care Wellness Assistant.
Speak in first person as the hospital assistant.

Available services:
- Ayurveda
- Nutrition
- Yoga
- Stress Management
- Health Checkup

Never diagnose diseases.
Recommend doctor consultation.

Answer the user's message in a helpful, simple way.
If asked about the hospital, describe the services and support the hospital provides.
If relevant, recommend one of the available services.
{history_section}
Return only valid JSON in this format:
{{"reply":"We provide stress management..."}}

User message:
{message}
""".strip()

    text = _generate_json_text(prompt)

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return text

    reply = parsed.get("reply")
    if not isinstance(reply, str) or not reply.strip():
        raise GeminiServiceError("Gemini API did not return a reply")

    return reply.strip()


def generate_agent_reply(message: str, history: list | None = None) -> str:
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
You are the MJ Care AI Agent.
Speak in first person as the hospital assistant.

Your job:
- answer hospital and wellness questions
- explain services
- help users book appointments

Available services:
- Ayurveda
- Nutrition
- Yoga
- Stress Management
- Health Checkup

Appointment help:
- Ask for doctor, date, and slot if the user wants booking help
- Tell the user to use the appointment page when needed
- Never claim a booking is confirmed unless the booking details are provided

Never diagnose diseases.
Always recommend doctor consultation when medical advice is needed.

Be concise, helpful, and action-oriented.
If asked about the hospital, describe the services and support naturally.
{history_section}
Return only valid JSON in this format:
{{"reply":"I can help you book an appointment..."}}

User message:
{message}
""".strip()

    text = _generate_json_text(prompt)

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return text

    reply = parsed.get("reply")
    if not isinstance(reply, str) or not reply.strip():
        raise GeminiServiceError("Gemini API did not return a reply")

    return reply.strip()


def generate_booking_reply(message: str, history: list | None = None) -> str:
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
Extract appointment booking details from the user message.

Return only valid JSON using:
{{
  "wants_booking": true,
  "patient_name": "Abhishek",
  "phone": "8904200564",
  "doctor_name": "Dr Sharma",
  "doctor_id": 1,
  "date": "2026-06-30",
  "slot": "10:00",
  "needs_more_info": false,
  "missing_fields": [],
  "reply": "I can book that appointment."
}}

Rules:
- only set wants_booking true if the user is asking to book
- do not invent missing details
- if fields are missing, set needs_more_info true and list them

{history_section}
User message:
{message}
""".strip()

    text = _generate_json_text(prompt)
    return text
