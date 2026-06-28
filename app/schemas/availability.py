from pydantic import BaseModel


class AvailableSlotsResponse(BaseModel):
    doctor: str
    slots: list[str]
