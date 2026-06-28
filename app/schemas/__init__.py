from app.schemas.appointment import AppointmentConfirmation, AppointmentCreate
from app.schemas.availability import AvailableSlotsResponse
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.doctor import DoctorCreate, DoctorResponse
from app.schemas.report import ReportAnalysisRequest, ReportSummaryResponse, ReportTextResponse

__all__ = [
    "AppointmentConfirmation",
    "AppointmentCreate",
    "AvailableSlotsResponse",
    "ChatRequest",
    "ChatResponse",
    "DoctorCreate",
    "DoctorResponse",
    "ReportAnalysisRequest",
    "ReportSummaryResponse",
    "ReportTextResponse",
]
