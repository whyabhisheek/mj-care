from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user
from app.database import get_db
from app.models.doctor import Doctor
from app.schemas.appointment import AppointmentConfirmation, AppointmentCreate
from app.services.appointments import (
    AppointmentConflictError,
    AppointmentNotFoundError,
    create_booking,
)


router = APIRouter(tags=["Appointments"])


@router.post(
    "/book-appointment",
    response_model=AppointmentConfirmation,
    status_code=status.HTTP_201_CREATED,
)
def book_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: object = Depends(get_current_user),
) -> AppointmentConfirmation:
    current_user_email = getattr(current_user, "email", None)
    try:
        appointment = create_booking(
            db,
            patient_email=current_user_email,
            patient_name=payload.name,
            phone=payload.phone,
            doctor_id=payload.doctor_id,
            appointment_date=payload.date,
            slot=payload.slot,
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

    return AppointmentConfirmation(
        message="Appointment booked",
        booking_id=appointment.id,
    )
