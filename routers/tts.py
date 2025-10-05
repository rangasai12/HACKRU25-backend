# routers/tts.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import os
from typing import Iterable, Union

load_dotenv()  # loads ELEVENLABS_API_KEY from .env if present

API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not API_KEY:
    # Fail fast so you notice during startup
    raise RuntimeError(
        "Missing ELEVENLABS_API_KEY. Add it to your environment or .env file."
    )

client = ElevenLabs(api_key=API_KEY)

router = APIRouter(prefix="/tts", tags=["tts"])


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    voice_id: str = "JBFqnCBsd6RMkjVDRZzb"           # default voice from docs
    model_id: str = "eleven_turbo_v2_5"          # default model from docs
    output_format: str = "mp3_44100_128"              # mp3 streamed back


def _to_bytes_iter(
    audio: Union[bytes, bytearray, Iterable[bytes]]
) -> Iterable[bytes]:
    """ElevenLabs SDK may return bytes or an iterable of bytes; normalize."""
    if isinstance(audio, (bytes, bytearray)):
        yield audio
    else:
        for chunk in audio:
            yield chunk


@router.post("/speak")
def speak(req: TTSRequest):
    """
    Synthesize speech and stream the audio back.
    """
    try:
        audio = client.text_to_speech.convert(
            text=req.text,
            voice_id=req.voice_id,
            model_id=req.model_id,
            output_format=req.output_format,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"ElevenLabs error: {e}")

    media_type = (
        "audio/mpeg" if req.output_format.startswith("mp3") else "audio/wav"
    )
    filename_ext = "mp3" if media_type == "audio/mpeg" else "wav"

    return StreamingResponse(
        _to_bytes_iter(audio),
        media_type=media_type,
        headers={"Content-Disposition": f'inline; filename="speech.{filename_ext}"'},
    )
