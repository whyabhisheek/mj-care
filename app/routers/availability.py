from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.appointment import Appointment
from app.models.availability import Availability
from app.models.doctor import Doctor
from app.schemas.availability import AvailableSlotsResponse


router = APIRouter(tags=["Availability"])


@router.get(
    "/available-slots",
    response_model=AvailableSlotsResponse,
    status_code=status.HTTP_200_OK,
)
def get_available_slots(
    doctor_id: int = Query(..., gt=0),
    date_: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
) -> AvailableSlotsResponse:
    doctor = db.get(Doctor, doctor_id)
    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    all_slots = set(
        db.scalars(
            select(Availability.slot).where(
                Availability.doctor_id == doctor_id,
                Availability.date == date_,
                Availability.status == "available",
            )
        ).all()
    )

    booked_slots = set(
        db.scalars(
            select(Appointment.slot).where(
                Appointment.doctor_id == doctor_id,
                Appointment.date == date_,
                Appointment.status != "cancelled",
            )
        ).all()
    )

    return AvailableSlotsResponse(
        doctor=doctor.name,
        slots=sorted(all_slots - booked_slots),
    )
