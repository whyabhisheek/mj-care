from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DoctorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    specialization: str = Field(..., min_length=1, max_length=100)
    experience: int = Field(..., ge=0)
    consultation_fee: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)


class DoctorResponse(BaseModel):
    id: int
    name: str
    specialization: str
    experience: int
    consultation_fee: Decimal

    model_config = ConfigDict(from_attributes=True)


class AvailabilityCreate(BaseModel):
    doctor_id: int = Field(..., gt=0)
    start_date: str = Field(..., min_length=10, max_length=10)
    days_ahead: int = Field(default=14, ge=1, le=60)
    slots: list[str] = Field(default_factory=list)
