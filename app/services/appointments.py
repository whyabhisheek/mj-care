from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.availability import Availability
from app.models.doctor import Doctor


class AppointmentServiceError(Exception):
    pass


class AppointmentNotFoundError(AppointmentServiceError):
    pass


class AppointmentConflictError(AppointmentServiceError):
    pass


def create_booking(
    db: Session,
    *,
    patient_email: str | None,
    patient_name: str,
    phone: str,
    doctor_id: int,
    appointment_date: date,
    slot: str,
) -> Appointment:
    doctor = db.get(Doctor, doctor_id)
    if doctor is None:
        raise AppointmentNotFoundError("Doctor not found")

    available_slot = db.scalar(
        select(Availability).where(
            Availability.doctor_id == doctor_id,
            Availability.date == appointment_date,
            Availability.slot == slot,
            Availability.status == "available",
        )
    )
    if available_slot is None:
        raise AppointmentConflictError("Slot is not available")

    existing_appointment = db.scalar(
        select(Appointment).where(
            Appointment.doctor_id == doctor_id,
            Appointment.date == appointment_date,
            Appointment.slot == slot,
            Appointment.status != "cancelled",
        )
    )
    if existing_appointment is not None:
        raise AppointmentConflictError("Slot already booked")

    appointment = Appointment(
        patient_email=patient_email,
        patient_name=patient_name,
        phone=phone,
        doctor_id=doctor_id,
        date=appointment_date,
        slot=slot,
        status="pending_review",
    )
    db.add(appointment)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AppointmentConflictError("Slot already booked") from exc

    db.refresh(appointment)
    return appointment
