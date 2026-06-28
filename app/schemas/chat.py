from pydantic import BaseModel, Field


class HistoryEntry(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    history: list[HistoryEntry] = []
    agent: str = Field(default="gemini", pattern="^(gemini|elevenlabs)$")


class ChatResponse(BaseModel):
    reply: str


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1)
    voice_id: str = "21m00Tcm4TlvDq8ikWAM"
