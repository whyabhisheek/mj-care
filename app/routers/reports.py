from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.report import Report
from app.schemas.report import ReportAnalysisRequest, ReportSummaryResponse, ReportTextResponse
from app.services.gemini import GeminiServiceError, summarize_report


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

router = APIRouter(tags=["Reports"])


@router.post(
    "/upload-report",
    response_model=ReportTextResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_report(
    patient_name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ReportTextResponse:
    is_pdf_content = file.content_type == "application/pdf"
    is_pdf_filename = file.filename is not None and file.filename.lower().endswith(".pdf")
    if not is_pdf_content and not is_pdf_filename:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are supported",
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded PDF is empty",
        )

    try:
        reader = PdfReader(BytesIO(contents))
        extracted_text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except PdfReadError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid PDF file",
        ) from exc

    file_name = f"{uuid4().hex}_{file.filename}"
    file_path = str(UPLOAD_DIR / file_name)
    with open(file_path, "wb") as f:
        f.write(contents)

    report = Report(
        patient_name=patient_name,
        file_path=file_path,
        content=extracted_text,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return ReportTextResponse(
        report_id=report.id,
        text=extracted_text,
    )


@router.post(
    "/analyze-report",
    response_model=ReportSummaryResponse,
    status_code=status.HTTP_200_OK,
)
def analyze_report(
    payload: ReportAnalysisRequest,
    db: Session = Depends(get_db),
) -> ReportSummaryResponse:
    report = db.get(Report, payload.report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    text_to_analyze = payload.text or report.content
    if not text_to_analyze.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No text available to analyze",
        )

    try:
        summary = summarize_report(text_to_analyze)
    except GeminiServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Report analysis service unavailable",
        ) from exc

    report.summary = summary
    db.commit()

    return ReportSummaryResponse(summary=summary)
