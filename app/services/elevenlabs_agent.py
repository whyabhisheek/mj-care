import requests
from requests import RequestException

from app.config import get_settings


class ElevenLabsAgentError(Exception):
    pass


def conversation_reply(message: str, history: list | None = None) -> str:
    settings = get_settings()
    if not settings.elevenlabs_webhook_url:
        raise ElevenLabsAgentError(
            "ELEVENLABS_WEBHOOK_URL is not set. Configure it in backend/.env"
        )

    conversation_lines = []
    if history:
        for entry in history:
            role_label = "user" if entry.role == "user" else "assistant"
            conversation_lines.append(f"{role_label}: {entry.content}")
    conversation_lines.append(f"user: {message}")
    full_conversation = "\n".join(conversation_lines)

    try:
        response = requests.post(
            settings.elevenlabs_webhook_url,
            json={"message": full_conversation},
            timeout=30,
        )
    except RequestException as exc:
        raise ElevenLabsAgentError("ElevenLabs agent request failed") from exc

    if response.status_code >= 400:
        raise ElevenLabsAgentError("ElevenLabs agent request failed")

    try:
        data = response.json()
    except ValueError as exc:
        raise ElevenLabsAgentError("ElevenLabs agent returned invalid JSON") from exc

    reply = (
        data.get("reply")
        or data.get("response")
        or data.get("message")
        or data.get("text")
    )
    if not reply or not isinstance(reply, str):
        raise ElevenLabsAgentError("ElevenLabs agent did not return a reply")

    return reply.strip()
