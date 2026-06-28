from pydantic import BaseModel, Field


class ReportTextResponse(BaseModel):
    report_id: int
    text: str


class ReportAnalysisRequest(BaseModel):
    report_id: int
    text: str = ""


class ReportSummaryResponse(BaseModel):
    summary: str
