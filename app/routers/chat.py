from datetime import date
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse, TTSRequest
from app.config import get_settings
from app.models.doctor import Doctor
from app.services.elevenlabs import ElevenLabsError, text_to_speech
from app.services.elevenlabs_agent import ElevenLabsAgentError, conversation_reply
from app.services.appointments import (
    AppointmentConflictError,
    AppointmentNotFoundError,
    create_booking,
)
from app.services.booking_intent import extract_booking_intent
from app.services.gemini import GeminiServiceError, generate_agent_reply, generate_chat_reply


router = APIRouter(tags=["Chatbot"])
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def chat(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    if payload.agent == "elevenlabs":
        settings = get_settings()
        if not settings.elevenlabs_webhook_url:
            try:
                intent = extract_booking_intent(payload.message, payload.history)
            except GeminiServiceError as exc:
                logger.exception("Booking intent extraction failed")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=str(exc),
                ) from exc

            if intent.wants_booking:
                if intent.needs_more_info:
                    missing = ", ".join(intent.missing_fields) if intent.missing_fields else "details"
                    return ChatResponse(
                        reply=f"I can book that for you. Please share: {missing}."
                    )

                doctor = None
                if intent.doctor_id is not None:
                    doctor = db.get(Doctor, intent.doctor_id)
                elif intent.doctor_name:
                    doctor = db.scalar(
                        select(Doctor).where(Doctor.name.ilike(f"%{intent.doctor_name}%"))
                    )

                if doctor is None:
                    return ChatResponse(reply="Please tell me which doctor you want to book.")

                if intent.patient_name is None or intent.phone is None or intent.appointment_date is None or intent.slot is None:
                    return ChatResponse(
                        reply="Please share your name, phone number, date, and slot so I can book it."
                    )

                try:
                    appointment = create_booking(
                        db,
                        patient_name=intent.patient_name,
                        phone=intent.phone,
                        doctor_id=doctor.id,
                        appointment_date=intent.appointment_date,
                        slot=intent.slot,
                    )
                except AppointmentNotFoundError as exc:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=str(exc),
                    ) from exc
                except AppointmentConflictError as exc:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=str(exc),
                    ) from exc

                return ChatResponse(
                    reply=(
                        f"Appointment booked with {doctor.name} on {appointment.date} at {appointment.slot}. "
                        f"Booking ID: {appointment.id}."
                    )
                )

            try:
                reply = generate_agent_reply(payload.message, payload.history)
            except GeminiServiceError as exc:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Chat service unavailable",
                ) from exc
            return ChatResponse(reply=reply)

        try:
            reply = conversation_reply(payload.message, payload.history)
        except ElevenLabsAgentError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            ) from exc
        return ChatResponse(reply=reply)

    try:
        reply = generate_chat_reply(payload.message, payload.history)
    except GeminiServiceError as exc:
        logger.exception("Gemini chat request failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return ChatResponse(reply=reply)


@router.post("/tts", status_code=status.HTTP_200_OK)
def tts(payload: TTSRequest) -> Response:
    try:
        audio = text_to_speech(payload.text, payload.voice_id)
    except ElevenLabsError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return Response(content=audio, media_type="audio/mpeg")
