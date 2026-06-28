from datetime import date

from pydantic import BaseModel, ConfigDict


class BookingListItem(BaseModel):
    id: int
    patient_name: str
    phone: str
    doctor_name: str
    specialization: str
    date: date
    slot: str
    status: str

    model_config = ConfigDict(from_attributes=True)
