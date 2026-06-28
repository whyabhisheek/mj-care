import requests
from requests import RequestException

from app.config import get_settings


ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel


class ElevenLabsError(Exception):
    pass


def text_to_speech(text: str, voice_id: str = DEFAULT_VOICE_ID) -> bytes:
    settings = get_settings()
    if not settings.elevenlabs_api_key:
        raise ElevenLabsError("ELEVENLABS_API_KEY is not set. Configure it in backend/.env")

    try:
        response = requests.post(
            ELEVENLABS_TTS_URL.format(voice_id=voice_id),
            headers={
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": settings.elevenlabs_api_key,
            },
            json={
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                },
            },
            timeout=30,
        )
    except RequestException as exc:
        raise ElevenLabsError("ElevenLabs API request failed") from exc

    if response.status_code >= 400:
        detail = response.text.strip()
        if detail:
            raise ElevenLabsError(
                f"ElevenLabs API request failed ({response.status_code}): {detail}"
            )
        raise ElevenLabsError(f"ElevenLabs API request failed ({response.status_code})")

    return response.content
