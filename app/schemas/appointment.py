from datetime import date

from pydantic import BaseModel, Field


class AppointmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=7, max_length=20)
    doctor_id: int = Field(..., gt=0)
    date: date
    slot: str = Field(..., min_length=1, max_length=50)


class AppointmentConfirmation(BaseModel):
    message: str
    booking_id: int


class AppointmentReviewActionResponse(BaseModel):
    message: str
