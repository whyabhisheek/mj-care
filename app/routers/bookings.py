from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import require_admin
from app.database import get_db
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.schemas.booking import BookingListItem
from app.services.emailer import send_booking_confirmation_email


router = APIRouter(tags=["Bookings"])


@router.get("/appointments", response_model=list[BookingListItem], status_code=status.HTTP_200_OK)
def list_appointments(
    db: Session = Depends(get_db),
    _: object = Depends(require_admin),
) -> list[BookingListItem]:
    rows = db.execute(
        select(
            Appointment.id,
            Appointment.patient_name,
            Appointment.phone,
            Appointment.date,
            Appointment.slot,
            Appointment.status,
            Doctor.name.label("doctor_name"),
            Doctor.specialization,
        )
        .join(Doctor, Doctor.id == Appointment.doctor_id)
        .order_by(Appointment.date.desc(), Appointment.slot.asc(), Appointment.id.desc())
    ).all()

    return [
        BookingListItem(
            id=row.id,
            patient_name=row.patient_name,
            phone=row.phone,
            doctor_name=row.doctor_name,
            specialization=row.specialization,
            date=row.date,
            slot=row.slot,
            status=row.status,
        )
        for row in rows
    ]


@router.post("/appointments/{appointment_id}/approve", status_code=status.HTTP_200_OK)
def approve_appointment(
    appointment_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: object = Depends(require_admin),
) -> dict[str, str]:
    appointment = db.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    doctor = db.get(Doctor, appointment.doctor_id)
    appointment.status = "confirmed"
    db.commit()
    if appointment.patient_email and doctor is not None:
        background_tasks.add_task(
            send_booking_confirmation_email,
            to_email=appointment.patient_email,
            patient_name=appointment.patient_name,
            doctor_name=doctor.name,
            date=str(appointment.date),
            slot=appointment.slot,
        )
    return {"message": "Appointment confirmed"}


@router.post("/appointments/{appointment_id}/reject", status_code=status.HTTP_200_OK)
def reject_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_admin),
) -> dict[str, str]:
    appointment = db.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    appointment.status = "rejected"
    db.commit()
    return {"message": "Appointment rejected"}
