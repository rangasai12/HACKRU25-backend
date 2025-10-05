# routers/tts.py
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import os
from typing import Iterable, Union, Optional, List
from io import BytesIO

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


class STTResponse(BaseModel):
    transcription: str
    language_code: Optional[str] = None
    audio_events: Optional[List] = None
    speakers: Optional[List] = None


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


@router.post("/transcribe", response_model=STTResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    model_id: str = "scribe_v1",
    tag_audio_events: bool = True,
    language_code: str = "eng",
    diarize: bool = True
):
    """
    Convert speech to text using ElevenLabs Speech-to-Text API.
    
    Args:
        file: Audio file to transcribe (supports MP3, WAV, M4A, etc.)
        model_id: Model to use (currently only "scribe_v1" is supported)
        tag_audio_events: Whether to tag audio events like laughter, applause, etc.
        language_code: Language of the audio file. If None, auto-detects language.
        diarize: Whether to annotate who is speaking (speaker diarization)
    
    Returns:
        STTResponse with transcription and metadata
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith('audio/'):
        raise HTTPException(
            status_code=400, 
            detail="File must be an audio file (MP3, WAV, M4A, etc.)"
        )
    
    try:
        # Read the uploaded file content
        audio_content = await file.read()
        audio_data = BytesIO(audio_content)
        
        # Transcribe using ElevenLabs
        transcription = client.speech_to_text.convert(
            file=audio_data,
            model_id=model_id,
            tag_audio_events=tag_audio_events,
            language_code=language_code if language_code != "auto" else None,
            diarize=diarize
        )
        
        # Parse the response
        transcription_text = transcription.text if hasattr(transcription, 'text') else str(transcription)
        
        # Extract additional metadata if available
        detected_language = getattr(transcription, 'language_code', language_code)
        audio_events = getattr(transcription, 'audio_events', None)
        speakers = getattr(transcription, 'speakers', None)
        
        # Ensure lists are properly formatted or None
        if audio_events is not None and not isinstance(audio_events, list):
            audio_events = None
        if speakers is not None and not isinstance(speakers, list):
            speakers = None
        
        return STTResponse(
            transcription=transcription_text,
            language_code=detected_language,
            audio_events=audio_events,
            speakers=speakers
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=502, 
            detail=f"ElevenLabs Speech-to-Text error: {str(e)}"
        )
