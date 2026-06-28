from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.availability import Availability
from app.models.doctor import Doctor
from app.schemas.doctor import AvailabilityCreate


DEFAULT_SLOTS = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]

router = APIRouter(tags=["Availability"])


@router.post("/availability", status_code=status.HTTP_201_CREATED)
def create_availability(
    payload: AvailabilityCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_admin),
) -> dict[str, str]:
    doctor = db.get(Doctor, payload.doctor_id)
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

    slots = payload.slots or DEFAULT_SLOTS
    start_date = date.fromisoformat(payload.start_date)

    for offset in range(payload.days_ahead):
        target_date = start_date + timedelta(days=offset)
        for slot in slots:
            existing = db.query(Availability).filter_by(
                doctor_id=doctor.id,
                date=target_date,
                slot=slot,
            ).first()
            if existing is None:
                db.add(
                    Availability(
                        doctor_id=doctor.id,
                        date=target_date,
                        slot=slot,
                        status="available",
                    )
                )

    db.commit()
    return {"message": "Availability created"}
